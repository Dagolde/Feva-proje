#!/usr/bin/env python3
"""Update supervisor password with correct bcrypt hash."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select


async def main():
    """Update supervisor password."""
    password = "Test@2026!"
    hashed = hash_password(password)
    
    print(f"Generated hash: {hashed}")
    
    async with AsyncSessionLocal() as db:
        # Find supervisor user
        result = await db.execute(
            select(User).where(User.username == "supervisor")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("Supervisor user not found!")
            return
        
        # Update password
        user.password_hash = hashed
        await db.commit()
        
        print(f"Updated password for user: {user.username}")
        print(f"User ID: {user.id}")
        print(f"Role ID: {user.role_id}")


if __name__ == "__main__":
    asyncio.run(main())
