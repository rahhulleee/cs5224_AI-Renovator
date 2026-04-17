#!/usr/bin/env python3
"""
Database schema synchronization script for AWS RDS.
This script creates all tables defined in the SQLAlchemy models.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from app.db import Base, _engine
import app.models.orm  # Important: import models so they are registered with Base
def sync_schema():
    """Create all tables in the database based on SQLAlchemy models."""
    print("Connecting to database...")
    engine = _engine()

    print("Creating tables...")
    # This will create all tables defined in the models
    Base.metadata.create_all(bind=engine)

    print("Schema synchronization complete!")
    print("Tables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    if "DATABASE_URL" not in os.environ:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Make sure your .env file contains the DATABASE_URL")
        sys.exit(1)

    sync_schema()