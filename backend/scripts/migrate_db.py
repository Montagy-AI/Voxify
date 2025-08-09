#!/usr/bin/env python3
"""
Voxify Database Migration Script
Add missing columns to existing database tables
"""
import os
import sys
import sqlite3
from datetime import datetime

# Add the project root directory to the Python path
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SCRIPT_DIR)


def migrate_database():
    """Migrate the database to add missing columns"""
    print("🚀 Starting Voxify database migration...")

    # Database file path
    db_path = os.path.join(SCRIPT_DIR, "data", "voxify.db")

    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        print("Please run the database initialization script first.")
        return False

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        print(f"📋 Current columns in users table: {columns}")

        # Add missing columns if they don't exist
        if "reset_token" not in columns:
            print("➕ Adding reset_token column...")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
            print("✅ reset_token column added")

        if "reset_token_expires_at" not in columns:
            print("➕ Adding reset_token_expires_at column...")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires_at TIMESTAMP")
            print("✅ reset_token_expires_at column added")

        # Commit changes
        conn.commit()

        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Updated columns in users table: {updated_columns}")

        # Update schema version
        cursor.execute(
            """
            INSERT OR REPLACE INTO schema_version (version, applied_at, description)
             VALUES (?, ?, ?)
        """,
            ("1.0.1", datetime.now().isoformat(), "Added password reset token columns"),
        )

        conn.commit()
        print("✅ Database migration completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

    finally:
        if "conn" in locals():
            conn.close()


def main():
    """Execute the database migration"""
    if migrate_database():
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
