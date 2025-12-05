"""
Database initialization script.
Creates all tables defined in the models.
"""
import asyncio
from app.core.database import engine, Base
from app.models.document import Document  # Import all models here
from app.core.logger import logger

from sqlalchemy import select
from app.models.user import User
from app.core import security
from app.core.config import settings

async def init_db():
    """Initialize database tables and seed data."""
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully!")

    # Seed superuser
    async with engine.connect() as conn:
        # We need a session for ORM operations, but for simple insert we can use connection or just create a session
        # Let's use a session to be safe with ORM
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.ext.asyncio import AsyncSession
        
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            logger.info("Checking for superuser...")
            query = select(User).where(User.email == "admin@example.com")
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.info("Creating superuser admin@example.com")
                user = User(
                    email="admin@example.com",
                    hashed_password=security.get_password_hash("admin"),
                    full_name="Admin User",
                    is_superuser=True,
                    is_active=True,
                )
                session.add(user)
                await session.commit()
                logger.info("Superuser created!")
            else:
                logger.info("Superuser already exists.")

if __name__ == "__main__":
    asyncio.run(init_db())
