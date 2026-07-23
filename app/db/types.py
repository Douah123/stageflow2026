import json

from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator


class JSONEncodedList(TypeDecorator):
    """Stocke une liste Python en JSON dans une colonne TEXT."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)
