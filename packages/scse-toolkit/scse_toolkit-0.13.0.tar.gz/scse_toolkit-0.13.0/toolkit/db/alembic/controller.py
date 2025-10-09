from typing import Callable, cast

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import Script, ScriptDirectory
from sqlalchemy import Engine, MetaData, create_engine

from toolkit.utils import import_member

from .. import sqla as sqla

ruff_is_installed = False

try:
    import ruff  # type: ignore  # noqa: F401

    ruff_is_installed = True
except ImportError:
    pass


AlembicChanges = list[tuple[object, ...]]


class AlembicController(object):
    """Wraps the alembic config and migration APIs for easier use
    (especially using multiple databases)."""

    alembic_config: Config
    db_dsn: str
    engine: Engine | None = None
    get_metadata: Callable[..., MetaData]

    def __init__(
        self,
        db_dsn: str,
        script_location: str,
        metadata_getter: str,
        use_ruff: bool = True,
    ) -> None:
        self.db_dsn = db_dsn

        get_metadata, _ = import_member(metadata_getter)

        if get_metadata is None:
            raise ValueError(f"Could not import '{metadata_getter}'.")

        self.get_metadata = get_metadata

        self.alembic_config = Config()
        self.alembic_config.set_main_option("script_location", script_location)
        self.alembic_config.set_main_option("sqlalchemy.url", db_dsn)
        self.alembic_config.set_main_option("metadata_getter", metadata_getter)
        self.alembic_config.set_main_option("file_template", "%%(rev)s_%%(slug)s")

        if use_ruff and ruff_is_installed:
            self.set_ruff_cfg()

    def set_ruff_cfg(self) -> None:
        section = "post_write_hooks"
        self.alembic_config.set_section_option(section, "hooks", "ruff")
        self.alembic_config.set_section_option(section, "ruff.type", "exec")
        self.alembic_config.set_section_option(section, "ruff.executable", "ruff")
        self.alembic_config.set_section_option(
            section, "ruff.options", "format REVISION_SCRIPT_FILENAME"
        )

    def get_engine(self) -> Engine:
        """Returns a database engine for the configured dsn."""
        if self.engine is None:
            self.engine = create_engine(self.db_dsn)

        return self.engine

    def get_database_revision(self) -> str | None:
        """Returns the current revision hash of a given database.
        To do this a connection to the database and a call to alembic are required."""

        engine = self.get_engine()

        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()

    def get_head_revision(self) -> str | tuple[str, ...] | None:
        """Returns the revision hash of the newest migration
        in the alembic `versions/` directory."""
        script_directory = ScriptDirectory.from_config(self.alembic_config)

        return script_directory.as_revision_number("head")

    def list_revisions(self) -> list[Script]:
        """Returns the currently available revisions."""
        script_directory = ScriptDirectory.from_config(self.alembic_config)

        return list(script_directory.walk_revisions())

    def upgrade_database(self, revision: str = "head") -> None:
        """Uses alembic to upgrade the given database.
        Optionally a desired revision can be supplied instead
        of the default `head` (newest) revision."""

        command.upgrade(self.alembic_config, revision)

    def downgrade_database(self, revision: str = "-1") -> None:
        """Like `upgrade_database` but in reverse."""
        command.downgrade(self.alembic_config, revision)

    def stamp_database(self, revision: str) -> None:
        """Uses alembic to stamp the given database with the given revision.
        Only touches the `alembic_version` table, nothing else."""

        command.stamp(self.alembic_config, revision, purge=True)

    def compare_metadata(self, metadata: MetaData) -> AlembicChanges:
        """Compares the current database structure against an sqlalchemy `MetaData` object
        and returns the differences.
        Uses :func:`alembic.autogenerate.compare_metadata` for the diffing. More info:
        https://alembic.sqlalchemy.org/en/latest/api/autogenerate.html#alembic.autogenerate.compare_metadata"""
        engine = self.get_engine()

        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            # `alembic`s types are kind of whack
            # so i have to do this, smh
            return cast(AlembicChanges, compare_metadata(context, metadata))

    def autogenerate_revision(
        self, message: str, rev_id: str | None = None
    ) -> Script | list[Script | None] | None:
        """Automatically generates a new database revision using alembics autogenerate features."""
        return command.revision(
            self.alembic_config, message, autogenerate=True, rev_id=rev_id
        )
