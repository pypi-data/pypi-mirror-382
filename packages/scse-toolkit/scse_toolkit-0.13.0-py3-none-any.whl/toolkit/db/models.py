from typing import ClassVar

from sqlalchemy.orm import DeclarativeBase as DeclarativeBase
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql.schema import MetaData


class HasTablename(object):
    """ORM base model class. All database models should inherit from here."""

    table_prefix: ClassVar[str] = ""

    @classmethod
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generates the models' `__tablename__` using the class' name
        and the class attribute `table_prefix`."""
        return str(cls.table_prefix + cls.__name__.lower())

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"


class HasConventionalMetadata(object):
    metadata: ClassVar[MetaData]

    @classmethod
    def reset_metadata(cls) -> None:
        """Resets the models `metadata`, erasing all currently registered child models from it.
        Usually only called once directly after this class' definition."""
        cls.metadata = MetaData(
            # explicit naming conventions for consitency
            # especially in alembic migrations
            naming_convention={
                "ix": "ix_%(column_0_label)s",
                "uq": "uq_%(table_name)s_%(column_0_N_name)s",
                "ck": "ck_%(table_name)s_%(constraint_name)s",
                "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
                "pk": "pk_%(table_name)s",
            }
        )
