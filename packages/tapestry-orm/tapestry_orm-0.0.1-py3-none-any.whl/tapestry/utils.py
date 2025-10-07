import types
import inspect

from enum import Enum
from more_itertools import flatten
from datetime import datetime, date, time
from typing import Any, Iterable, Mapping, get_args, get_origin, Union


def compatible_type(some: Any) -> Any:
    if isinstance(some, (str, int, bool, float)):
        return some
    if isinstance(some, Enum):
        return some.name
    if isinstance(some, date):
        return datetime.combine(some, time.min)
    if isinstance(some, Mapping):
        return {k: compatible_type(v) for k, v in some.items()}
    if isinstance(some, Iterable):
        return [compatible_type(i) for i in some]
    return some

def convert_types(some: dict[str, Any]) -> dict[str, Any]:
    return {k : compatible_type(v) for k, v in some.items()}
    
    
def flatten_type(tp: type[Any], base_type = None) -> Iterable[type]:
    # if inspect.isclass(tp):
    #     if issubclass(tp, base_type):
    #         return (tp, )
    if base_type and inspect.isclass(tp) and issubclass(tp, base_type):
        return (tp, )
    origin = get_origin(tp)
    if origin and base_type and (origin is base_type):
        return (tp, )
    args = get_args(tp)
    if args:
        return flatten(flatten_type(subt) for subt in args)
    return (tp, )
    

def replace_type(tp: type[Any], base_type: type[Any], replacement: type[Any]) -> type[Any]:
    # Handle direct class replacement
    if inspect.isclass(tp) and issubclass(tp, base_type):
        return replacement
    
    origin = get_origin(tp)
    args = get_args(tp)
    
    if args:
        replaced = tuple(replace_type(t, base_type, replacement) for t in args)
        
        # Handle Union types (both typing.Union and types.UnionType)
        if origin is Union:
            return Union[replaced]
        elif isinstance(tp, types.UnionType):
            # Reconstruct union using | operator
            result = replaced[0]
            for t in replaced[1:]:
                result = result | t
            return result
        elif origin is not None:
            # Handle other generic types (List, Dict, Optional, etc.)
            try:
                return origin[replaced]
            except TypeError:
                # If subscripting fails, return the original type
                return tp
    
    return tp