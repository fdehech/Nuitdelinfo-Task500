"""
Script to create default users for the application.
Run this script after database initialization to create test accounts.

Default accounts created:
- Admin: admin@example.com / admin123
- User: user@example.com / user123
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User


async def create_default_users():
    """Create default admin and user accounts if they don't exist."""
    async with AsyncSessionLocal() as db:
        # Default users to create
        default_users = [
            {
                "email": "admin@example.com",
                "password": "admin123",
                "full_name": "Admin User",
                "is_superuser": True,
                "is_active": True,
            },
            {
                "email": "user@example.com",
                "password": "user123",
                "full_name": "Regular User",
                "is_superuser": False,
                "is_active": True,
            },
        ]

        for user_data in default_users:
            # Check if user already exists
            query = select(User).where(User.email == user_data["email"])
            result = await db.execute(query)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"✓ User {user_data['email']} already exists, skipping...")
                continue

            # Create new user
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                is_superuser=user_data["is_superuser"],
                is_active=user_data["is_active"],
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

            role = "Admin" if user.is_superuser else "User"
            print(f"✓ Created {role}: {user.email}")

        print("\n✓ Default users setup complete!")
        print("\nTest Accounts:")
        print("  Admin: admin@example.com / admin123")
        print("  User:  user@example.com / user123")


if __name__ == "__main__":
    print("Creating default users...\n")
    asyncio.run(create_default_users())
