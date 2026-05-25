import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config


from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

from api.user.models import User
from workflow.models import Note
from api.core.config import DB_ASYNC_CONNECTION_STR

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

def run_migrations_offline():
   url = DB_ASYNC_CONNECTION_STR
   context.configure(
       url=url,
       target_metadata=target_metadata,
       literal_binds=True,
       dialect_opts={"paramstyle": "named"},
       include_object=filter_db_objects
   )

   with context.begin_transaction():
       context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
       context.configure(
           connection=connection,
           target_metadata=target_metadata
       )
       context.run_migrations()


async def run_migrations_online():
   config_section = config.get_section(config.config_ini_section)
   url = DB_ASYNC_CONNECTION_STR
   config_section["sqlalchemy.url"] = url

   connectable = AsyncEngine(
       engine_from_config(
           config_section,
           prefix="sqlalchemy.",
           poolclass=pool.NullPool,
           future=True,
       )
   )

   async with connectable.connect() as connection:
       await connection.run_sync(do_run_migrations)

   await connectable.dispose()


if context.is_offline_mode():
   run_migrations_offline()
else:
   asyncio.run(run_migrations_online())
