"""Serialization module.

This module provides functions to serialize and deserialize data structures to
and from JSON and Cap'n Proto."""

from __future__ import annotations
import typing
import zhinst.comms._comms

__all__ = ["from_dict", "from_json", "from_packed_capnp", "to_json", "to_packed_capnp"]

def from_dict(
    input_value: dict, schema: zhinst.comms._comms.SchemaLoader, struct_id: int
) -> typing.Any:
    """Convert a python dictionary to a dynamic struct.

    The dictionary must match the schema defined in the SchemaLoader.
    If the format is not valid, an Exception is raised.

    Args:
        input_value: The dictionary to convert.
        schema: The schema loader.
        struct_id: The id of the struct to convert.

    Returns:
        The dynamic struct.
    """

def from_json(
    input_value: str, schema: zhinst.comms._comms.SchemaLoader, struct_id: int
) -> typing.Any:
    """Convert a json string to a dynamic struct

    The content must match the schema defined in the SchemaLoader. If
    the format is not valid, an Exception is raised.

    Args:
        input_value: The JSON message to convert.
        schema: The schema loader.
        struct_id: The id of the struct to convert.

    Returns:
        The dynamic struct.
    """

def from_packed_capnp(
    input_value: bytes, schema: zhinst.comms._comms.SchemaLoader, struct_id: int
) -> zhinst.comms._comms.DynamicStruct:
    """Convert a packed Cap'n Proto message to a dynamic struct.

    The packed message must match the schema defined in the SchemaLoader. If
    the format is not valid, an Exception is raised.

    Args:
        input_value: The packed Cap'n Proto message to convert.
        schema: The schema loader.
        struct_id: The id of the struct to convert.

    Returns:
        The dynamic struct.
    """

@typing.overload
def to_json(
    input_value: dict, schema: zhinst.comms._comms.SchemaLoader, struct_id: int
) -> str:
    """Convert a python dictionary to a JSON string.

    Note that since the Cap'n Proto JSON codec is used the result may
    differ compared to the native python JSON format. The advantage is that
    the result can be directly used be used by any other Cap'n Proto logic.

    The dictionary must match the schema defined in the SchemaLoader. If the
    format is not valid, an Exception is raised.

    Args:
        input: The dictionary to convert.
        schema: The schema loader.
        struct_id: The id of the struct to convert.

    Returns:
        The JSON string.
    """

@typing.overload
def to_json(
    input_value: bytes, schema: zhinst.comms._comms.SchemaLoader, struct_id: int
) -> str:
    """Convert a packed Cap'n Proto message to a JSON string.

    The packed message must match the schema defined in the SchemaLoader. If
    the format is not valid, an Exception is raised.

    Args:
        input: The packed Cap'n Proto message to convert.
        schema: The schema loader.
        struct_id: The id of the struct to convert.

    Returns:
        The JSON string.
    """

def to_json(
    input_value: bytes | dict, schema: zhinst.comms._comms.SchemaLoader, struct_id: int
) -> str:
    """Convert a python dict or packed Cap'n Porto message to a JSON string.

    Note that since the Cap'n Proto JSON codec is used the result may
    differ compared to the native python JSON format. The advantage is that
    the result can be directly used be used by any other Cap'n Proto logic.

    The dictionary must match the schema defined in the SchemaLoader. If the
    format is not valid, an Exception is raised.

    Args:
        input: The dictionary or packed Cap'n Proto message to convert.
        schema: The schema loader.
        struct_id: The id of the struct to convert.

    Returns:
        The JSON string.
    """

@typing.overload
def to_packed_capnp(
    input_value: dict, schema: zhinst.comms._comms.SchemaLoader, struct_id: int
) -> bytes:
    """Convert a python dictionary to a packed Cap'n Proto message.

    The dictionary must match the schema defined in the SchemaLoader. If the
    format is not valid, an Exception is raised.

    Args:
        input: The dictionary to convert.
        schema: The schema loader.
        struct_id: The id of the struct to convert.

    Returns:
        The packed Cap'n Proto message.
    """

@typing.overload
def to_packed_capnp(
    input_value: str, schema: zhinst.comms._comms.SchemaLoader, struct_id: int
) -> bytes:
    """Convert a json string to a packed Cap'n Proto message.

    The content must match the schema defined in the SchemaLoader. If the
    format is not valid, an Exception is raised.

    Args:
        input: The json string to convert.
        schema: The schema loader.
        struct_id: The id of the struct to convert.

    Returns:
        The packed Cap'n Proto message.
    """

def to_packed_capnp(
    input_value: str | dict, schema: zhinst.comms._comms.SchemaLoader, struct_id: int
) -> bytes:
    """Convert a json string or python dict to a packed Cap'n Proto message.

    The content must match the schema defined in the SchemaLoader. If the
    format is not valid, an Exception is raised.

    Args:
        input: The json string or python dict to convert.
        schema: The schema loader.
        struct_id: The id of the struct to convert.

    Returns:
        The packed Cap'n Proto message.
    """
