#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of AsyncPostgresMixin.

This example demonstrates how to use the AsyncPostgresMixin for async database operations.
"""

import asyncio
import os

os.environ.setdefault("DATABASE_HOST", "harpua.ornl.gov")
os.environ.setdefault("DATABASE_PORT", "5435")
os.environ.setdefault("DATABASE_USER", "vaadmin")
os.environ.setdefault("DATABASE_PW", "eTWJheGXWCwf")
os.environ.setdefault("DATABASE_DB", "vadb")

from pygarden.database import Database
from pygarden.mixins import AsyncPostgresMixin


class AsyncDatabaseExample(AsyncPostgresMixin, Database):
    """Example class that uses AsyncPostgresMixin."""


async def main():
    """Example usage of AsyncPostgresMixin."""
    try:
        async with AsyncDatabaseExample() as db:
            # Example queries
            print("Creating test table...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    value INTEGER
                )
            """)

            # Insert data
            print("Inserting data...")
            await db.execute("INSERT INTO test_table (name, value) VALUES ($1, $2)", "test_item", 42)

            # Query data
            print("Querying data...")
            results = await db.query("SELECT * FROM test_table")
            print(f"Query results: {results}")

            # Query with parameters
            print("Querying with parameters...")
            results = await db.query("SELECT * FROM test_table WHERE value > $1", 40)
            print(f"Parameterized query results: {results}")

            # Fetch single value
            print("Fetching single value...")
            count = await db.fetchval("SELECT COUNT(*) FROM test_table")
            print(f"Total records: {count}")

            # Fetch single row
            print("Fetching single row...")
            row = await db.fetchrow("SELECT * FROM test_table WHERE name = $1", "test_item")
            print(f"Single row: {row}")

            # Query as dictionary
            print("Querying as dictionary...")
            dict_results = await db.query("SELECT * FROM test_table", as_dict=True)
            print(f"Dictionary results: {dict_results}")

            # Clean up
            print("Cleaning up...")
            await db.execute("DROP TABLE IF EXISTS test_table")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())
