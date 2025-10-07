import asyncio
import logging
import contextlib

from collections.abc import AsyncIterator, AsyncGenerator
from surrealdb import AsyncSurreal, AsyncWsSurrealConnection, AsyncHttpSurrealConnection


logger = logging.getLogger(__name__)

class SurrealClientPool:
    """
    Connection pool manager for SurrealDB clients.

    Manages a pool of authenticated SurrealDB connections that can be
    reused across async operations. This improves performance by avoiding
    the overhead of creating new connections for each operation.

    Attributes:
        url: SurrealDB connection URL
        auth_payload: Authentication credentials dictionary
        pool_size: Number of connections to maintain in the pool
        connect_timeout: Timeout for connection attempts in seconds

    Example:
        >>> pool = SurrealClientPool(
        ...     url="ws://localhost:8000/rpc",
        ...     auth_payload={"username": "root", "password": "root"},
        ...     pool_size=5
        ... )
        >>> await pool.start()
        >>> async with pool.acquire() as client:
        ...     await client.use("mydb", "myns")
        ...     results = await client.select("person")
    """

    def __init__(
        self,
        url: str,
        auth_payload: dict,
        pool_size: int = 4,
        connect_timeout: float = 5.
    ):
        """
        Initialize the connection pool.

        Args:
            url: SurrealDB connection URL (ws:// or http://)
            auth_payload: Dictionary with authentication credentials
            pool_size: Number of connections to maintain (default: 4)
            connect_timeout: Connection timeout in seconds (default: 5.0)
        """
        self.url = url
        self.auth_payload = auth_payload
        self.pool_size = pool_size
        self.connect_timeout = connect_timeout
        self._queue: asyncio.Queue = asyncio.Queue()
        self._clients = []   # keep references for shutdown
        self._closed = False

    async def _make_one(self):
        """
        Create and authenticate a single SurrealDB client.

        Returns:
            An authenticated AsyncSurreal client ready for use

        Raises:
            Exception: If connection or authentication fails
        """
        c = AsyncSurreal(self.url)
        await c.signin(self.auth_payload)
        return c


    async def start(self):
        """
        Initialize the connection pool with authenticated clients.

        Creates the specified number of clients, authenticates them,
        and adds them to the pool queue for reuse.

        Raises:
            Exception: If unable to create the required number of clients
        """
        for i in range(self.pool_size):
            try:
                client = await self._make_one()
            except Exception as e:
                logger.exception("Failed to create surreal client #%d: %s", i, e)
                # retry/backoff before giving up; here we re-raise after a small delay
                await asyncio.sleep(0.5)
                client = await self._make_one()
            self._clients.append(client)
            self._queue.put_nowait(client)
        logger.info("SurrealDB pool started (%d clients)", len(self._clients))

    async def close(self):
        """
        Close all connections and shut down the pool.

        Drains the queue and closes all client connections gracefully.
        This should be called when the application shuts down.
        """
        if self._closed:
            return
        self._closed = True
        # drain queue so other tasks don't try to reuse
        while not self._queue.empty():
            try:
                _ = self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break
        # close actual clients
        for c in self._clients:
            try:
                await c.close()
            except Exception:
                logger.exception("Error closing surreal client")
        self._clients.clear()
        logger.info("SurrealDB pool closed")

    @contextlib.asynccontextmanager
    async def acquire(self) -> AsyncIterator[AsyncWsSurrealConnection | AsyncHttpSurrealConnection]:
        """
        Acquire a connection from the pool as a context manager.

        Gets an authenticated client from the pool, yields it for use,
        and automatically returns it to the pool when done.

        Yields:
            AsyncWsSurrealConnection | AsyncHttpSurrealConnection: An authenticated client

        Example:
            >>> async with pool.acquire() as client:
            ...     results = await client.select("person")

        Raises:
            Exception: If the acquired client encounters a fatal error
        """
        client = await self._queue.get()
        try:
            yield client
        except Exception as exc:
            # If the client had a fatal error, attempt to reconnect/replace it
            # Simple strategy: if exception looks like connection/auth error -> recreate
            if self._is_fatal_client_exc(exc):
                logger.warning("Client had fatal error, replacing: %s", exc)
                await self._replace_client(client)
                # re-raise so caller can handle retry logic
                raise
            else:
                raise
        finally:
            # If pool is closing, don't put back
            if not self._closed:
                self._queue.put_nowait(client)

    async def run_query(self, *args, retries: int = 1, backoff: float = 0.2, **kwargs):
        """
        Execute a query using a pooled connection with automatic retry.

        Acquires a client from the pool, executes the query, and handles
        retries for transient failures.

        Args:
            *args: Arguments to pass to the query method
            retries: Number of retry attempts for transient errors (default: 1)
            backoff: Base backoff time in seconds between retries (default: 0.2)
            **kwargs: Keyword arguments to pass to the query method

        Returns:
            Query results from SurrealDB

        Raises:
            Exception: If the query fails after all retry attempts
        """
        for attempt in range(retries + 1):
            async with self.acquire() as client:
                try:
                    # Replace with client's actual query/call method
                    return await client.query(*args, **kwargs)
                except Exception as exc:
                    logger.exception("Query failed on attempt %d: %s", attempt, exc)
                    if attempt < retries and self._is_retryable(exc):
                        await asyncio.sleep(backoff * (2 ** attempt))
                        continue
                    # If fatal to client, replace it so pool remains healthy
                    if self._is_fatal_client_exc(exc):
                        await self._replace_client(client)
                    raise

    async def _replace_client(self, dead_client):
        """
        Replace a failed client with a new authenticated connection.

        Closes the dead client, creates a new one, and adds it back to the pool
        to maintain the pool size.

        Args:
            dead_client: The client connection that failed
        """
        try:
            await dead_client.close()
        except Exception:
            pass
        try:
            new_client = await self._make_one()
        except Exception as e:
            logger.exception("Failed to create replacement client: %s", e)
            # If we can't create a replacement immediately, put back the old one to avoid starvation.
            # In production, you might want to implement more sophisticated retry/backoff + alerts.
            self._queue.put_nowait(dead_client)
            return
        # replace in internal list
        try:
            idx = self._clients.index(dead_client)
            self._clients[idx] = new_client
        except ValueError:
            self._clients.append(new_client)
        self._queue.put_nowait(new_client)

    def _is_retryable(self, exc: Exception) -> bool:
        """
        Determine if an exception is retryable.

        Args:
            exc: The exception to check

        Returns:
            bool: True if the error is transient and worth retrying
        """
        return isinstance(exc, (asyncio.TimeoutError, ConnectionError))

    def _is_fatal_client_exc(self, exc: Exception) -> bool:
        """
        Determine if an exception indicates a broken client connection.

        Args:
            exc: The exception to check

        Returns:
            bool: True if the client connection is likely broken and needs replacement
        """
        return isinstance(exc, (ConnectionError, RuntimeError))



def create_engine(
    url: str,
    auth_payload: dict,
    pool_size: int = 4,
    connect_timeout: float = 5.
) -> AsyncGenerator[AsyncWsSurrealConnection | AsyncHttpSurrealConnection, None]:
    """
    Create a connection pool for SurrealDB with automatic connection management.

    This function creates a pool of authenticated SurrealDB connections that can
    be reused across your application. It returns a context manager that handles
    acquiring and releasing connections automatically.

    Args:
        url: SurrealDB connection URL (e.g., "ws://localhost:8000/rpc")
        auth_payload: Dictionary with authentication credentials
            Example: {"username": "root", "password": "root"}
        pool_size: Number of connections to maintain in the pool (default: 4)
        connect_timeout: Timeout for connection attempts in seconds (default: 5.0)

    Returns:
        AsyncGenerator: A context manager for acquiring connections from the pool

    Example:
        >>> # Create an engine
        >>> engine = create_engine(
        ...     "ws://localhost:8000/rpc",
        ...     {"username": "root", "password": "root"},
        ...     pool_size=5
        ... )
        >>>
        >>> # Use the engine to get connections
        >>> async with engine() as db:
        ...     await db.use("mydatabase", "mynamespace")
        ...     people = await Person.insert(db, [
        ...         Person(name="Alice"),
        ...         Person(name="Bob")
        ...     ])

    Notes:
        - The pool is not started automatically; you need to call pool.start()
        - Connections are reused for better performance
        - Failed connections are automatically replaced
        - The pool should be closed when your application shuts down

    See Also:
        - SurrealClientPool: The underlying pool implementation
        - Node.insert(): For batch operations using pooled connections
        - Edge.relate(): For creating relationships using pooled connections
    """
    pool = SurrealClientPool(url, auth_payload, pool_size, connect_timeout)
    return pool.acquire
