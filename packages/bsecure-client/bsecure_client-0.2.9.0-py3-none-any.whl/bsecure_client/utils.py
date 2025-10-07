import datetime as dt
import enum
from copy import deepcopy
from io import BytesIO
from typing import Any
from uuid import UUID


class File:
    """Bsecure `File` type"""

    def __init__(self, content: BytesIO, filename: str | None = None):
        self.filename = filename or content.name
        self.content = content


class FileID:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return self.id


def remove_trailing_slash(path: str) -> str:
    if path and path[-1] == "/":
        path = path[:-1]
    return path


def make_timestamp(value: dt.datetime | dt.date | None) -> str | None:
    if isinstance(
        value,
        (dt.datetime | dt.date),
    ):
        return value.isoformat()
    else:
        return None


def to_serializable(val: Any):
    """JSON serializer for objects not serializable by default"""
    if isinstance(val, (dt.datetime | dt.date | dt.time)):
        return val.isoformat()
    elif isinstance(val, enum.Enum):
        return val.value
    elif isinstance(val, UUID):
        return str(val)
    elif hasattr(val, "__dict__"):
        return val.__dict__
    else:
        return val


def make_serializeable(dictionary: dict) -> dict:
    new_dict = deepcopy(dictionary)

    for k, v in new_dict.items():
        if isinstance(v, dict):
            new_dict[k] = make_serializeable(v)
        else:
            new_dict[k] = to_serializable(v)
    return new_dict
