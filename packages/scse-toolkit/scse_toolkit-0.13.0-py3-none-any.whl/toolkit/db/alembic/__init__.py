"""
This module provides an interface for managing database migrations using Alembic.
It includes a controller class for handling migration operations and a (typer-based)
CLI class for command-line interaction.

Minimal usage example:

.. code:: python

    from toolkit import db
    from toolkit.db.cli import AlembicCli, AlembicController


    class Model(db.BaseModel):
        id: db.types.IntegerId
        name: db.types.String


    def get_metadata():
        return db.BaseModel.metadata


    controller = AlembicController(
        "sqlite:///./sqlite.db",
        "tests.fixtures:migrations",
        f"{__name__}:{get_metadata.__name__}",
    )

    alembic_cli = AlembicCli(controller=controller)

    if __name__ == "__main__":
        alembic_cli()

"""

from .cli import AlembicCli as AlembicCli
from .controller import AlembicChanges as AlembicChanges
from .controller import AlembicController as AlembicController
