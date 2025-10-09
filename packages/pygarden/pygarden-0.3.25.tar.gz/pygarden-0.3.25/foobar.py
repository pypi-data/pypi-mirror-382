#!/usr/bin/env -S uv run --script
# -*- coding: utf-8 -*-
# /// script
# requires-python = "==3.11.*"
# dependencies = [
#    "python-dotenv",
#    "pygarden[postgres]",
# ]
# ///
from dotenv import load_dotenv
load_dotenv()
from pygarden.logz import create_logger
from pygarden.database import Database
from pygarden.mixins.postgres import PostgresMixin
logger = create_logger()
logger.info('Successfully imported pygarden with the PostgresMixin.')

class MyDatabase(PostgresMixin, Database):
    """
    Custom database class that uses PostgresMixin for PostgreSQL operations.
    """


with MyDatabase() as db:
    # Example usage of the database
    results = db.query("SELECT * FROM securenet.usa_road_network LIMIT 10")
    for row in results:
        print(row)