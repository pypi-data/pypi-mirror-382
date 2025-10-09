from datetime import datetime
from typing import Annotated

from sqlalchemy import Identity
from sqlalchemy import types as sqlatypes
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped as Mapped

from . import sqla

Boolean = Mapped[bool]
DateTime = Mapped[datetime]
Float = Mapped[float]
Integer = Mapped[int]
String = Mapped[str]


_int_id_column = sqla.Column(
    server_default=Identity(always=False, on_null=True, start=1, increment=1),
    primary_key=True,
)

IntegerId = Mapped[Annotated[int, _int_id_column]]

_json_column = sqla.Column(sqlatypes.JSON().with_variant(JSONB(), "postgresql"))

JsonValue = float | int | str | bool | dict[str, "JsonValue"] | list["JsonValue"] | None
Json = Mapped[Annotated[JsonValue, _json_column]]
JsonList = Mapped[Annotated[list[JsonValue], _json_column]]
JsonDict = Mapped[Annotated[dict[str, JsonValue], _json_column]]
