"""
various miscellaneous utility functions
"""

from typing import Any, Type

def normalise_synfig_layer_type_name(s:str) -> str:
    """
    Changes a value of the "name" attribuyte on a <layer> tag
    into its normal form.

    Args:
        s: the name
    """
    return s.lower().replace('_', '')

def type_and_value_to_str(t:Type, v:Any) -> (str|None):
    """
    Returns a serialisation of `v`.

    Args:
        v: the value
        t: a type. If this is `bool`, or
            any subclass, the result will be `"false"`
            or `"true"` (note lowercase).

            This argument is less mysterious if you
            consider the parallel function
            `type_and_str_to_value()`.
    """
    if v is None:
        return None
    elif issubclass(t, bool):
        return str(bool(v)).lower()
    else:
        return str(v)

def type_and_str_to_value(t:Type, s:str) -> Any:
    """
    Returns a value deserialised from a string.

    Arguments:
        t (type): the type to return
        s (str): the value to deserialise

    Returns:
        a value of type `t`, or None
    """
    if v is None:
        return None
    elif issubclass(t, bool):
        return v.lower()=='true'
    else:
        return t(v)
