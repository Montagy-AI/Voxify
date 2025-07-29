#!/usr/bin/env python3
"""
Recreate test user after database reset
"""

import os
import sys

sys.path.insert(0, ".")

from dotenv import load_dotenv


def recreate_test_user():
    """Recreate test user in fresh database"""
    print("👤 Recreating Test User After Database Reset")
    print("=" * 50)

    load_dotenv()

    try:
        from database import get_database_manager
        from database.models import User
        from api.utils.password import hash_password
        import uuid
        from datetime import datetime

        # Initialize database
        db_manager = get_database_manager()

        email = "nnnnnjun.yang@gmail.com"

        with db_manager.get_session() as session:
            # Check if user already exists
            existing_user = session.query(User).filter(User.email == email).first()

            if existing_user:
                print(f"✅ User already exists: {email}")
                return True

            # Create new user
            print(f"🆕 Creating new user: {email}")

            user = User(
                id=str(uuid.uuid4()),
                email=email,
                password_hash=hash_password("testpassword123"),  # Default password
                first_name="Test",
                last_name="User",
                is_active=True,
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(user)
            session.commit()

            print(f"✅ User recreated successfully!")
            print(f"  Email: {email}")
            print(f"  Password: testpassword123")
            print(f"  🎯 Ready for password reset testing!")

            return True

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    recreate_test_user()
