#!/usr/bin/env python3
"""
Reset Voxify Database
Delete existing database and create new table structure
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def reset_database():
    """Reset and reinitialize the database"""
    print("🚀 Starting Voxify database reset...")

    # Database file path
    db_path = Path("data/voxify.db")

    # Delete existing database file
    if db_path.exists():
        print(f"🗑️  Removing existing database file: {db_path}")
        try:
            os.remove(db_path)
            print("✅ Database file removed successfully")
        except Exception as e:
            print(f"❌ Failed to remove database file: {e}")
            return False

    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    try:
        # Import database modules
        from database.models import get_database_manager
        from database.vector_config import create_vector_db

        print("🔧 Creating new database tables...")

        # Initialize SQLite database
        db_manager = get_database_manager("sqlite:///data/voxify.db")
        db_manager.create_tables()
        db_manager.init_default_data()

        print("✅ SQLite database tables created successfully")

        # Initialize vector database
        print("🔧 Initializing vector database...")
        create_vector_db()
        print("✅ Vector database initialized successfully")

        print("🎉 Database reset completed successfully!")
        print("You can now register users normally.")

        return True

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = reset_database()
    if not success:
        sys.exit(1)
