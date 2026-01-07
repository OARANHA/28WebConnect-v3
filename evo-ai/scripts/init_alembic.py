#!/usr/bin/env python3
"""
Initialize Alembic for existing databases.

This script checks if the database has tables but no alembic_version table,
and stamps it with the appropriate migration version.
"""
import sys
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from src.config.settings import settings


async def check_and_stamp_alembic():
    """Check database state and stamp Alembic if needed."""
    # Convert to async connection string
    db_url = settings.POSTGRES_CONNECTION_STRING.replace(
        "postgresql://", "postgresql+asyncpg://"
    )

    engine = create_async_engine(db_url)

    async with engine.begin() as conn:
        # Check if alembic_version table exists
        def get_tables(sync_conn):
            from sqlalchemy import inspect
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        tables = await conn.run_sync(get_tables)
        print(f"Existing tables: {tables}")

        if "alembic_version" not in tables:
            print("\nalembic_version table not found!")

            # Check if channels table exists (means add_channels_table migration was applied)
            if "channels" in tables:
                print("channels table exists, stamping with 'add_channels_table' revision...")
                # Create alembic_version table and stamp with add_channels_table
                await conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"))
                await conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('add_channels_table')"))
                print("Stamped with 'add_channels_table'")
            else:
                print("channels table does not exist, stamping with '6db4a526335b' (initial) revision...")
                # Create alembic_version table and stamp with initial migration
                await conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"))
                await conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('6db4a526335b')"))
                print("Stamped with '6db4a526335b'")
        else:
            print("\nalembic_version table exists, checking current version...")
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            print(f"Current Alembic version: {version}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_and_stamp_alembic())