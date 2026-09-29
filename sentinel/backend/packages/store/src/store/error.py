from collections.abc import Iterator
from contextlib import contextmanager

from pymongo.errors import PyMongoError


class StoreError(Exception):
    pass


@contextmanager
def guarded() -> Iterator[None]:
    """Any Mongo error leaves the package as a StoreError."""
    try:
        yield
    except PyMongoError as e:
        raise StoreError(str(e)) from e
