"""User management service for admin operations."""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.role import Role
from app.models.user import User


async def _count_active_admins(db: AsyncSession) -> int:
    """Count the number of active admin users.
    
    Args:
        db: Database session
        
    Returns:
        Number of active (non-locked) admin users
    """
    # Get the admin role ID
    result = await db.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one_or_none()
    if not admin_role:
        return 0
    
    # Count active users with admin role
    result = await db.execute(
        select(func.count())
        .select_from(User)
        .where(User.role_id == admin_role.id)
        .where(User.locked_at.is_(None))
    )
    return result.scalar() or 0


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    role_id: int,
    lga_assignment: list[str] | None,
    created_by: UUID,
    ward_assignment: str | None = None,
) -> User:
    """Create a new user account.
    
    Args:
        db: Database session
        username: Unique username for the user
        email: User's email address
        password: Plain text password (will be hashed)
        role_id: Role ID to assign to the user
        lga_assignment: List of LGA codes assigned to the user (optional)
        ward_assignment: Ward name assigned to the user (optional)
        created_by: UUID of the admin creating the user
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If username or email already exists
    """
    # Check username uniqueness
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise ValueError("Username already exists")
    
    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise ValueError("Email already exists")
    
    # Create user
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role_id=role_id,
        lga_assignment=lga_assignment,
        ward_assignment=ward_assignment,
    )
    db.add(user)
    await db.flush()
    
    # Create audit log entry
    audit = AuditLog(
        user_id=created_by,
        operation="create_user",
        entity_type="user",
        entity_id=str(user.id),
        detail={"username": username, "email": email, "role_id": role_id},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(user)
    
    return user


async def update_user(
    db: AsyncSession,
    user_id: UUID,
    role_id: int | None,
    lga_assignment: list[str] | None,
    locked: bool | None,
    updated_by: UUID,
    ward_assignment: str | None = None,
) -> User:
    """Update user account details.
    
    Args:
        db: Database session
        user_id: UUID of the user to update
        role_id: New role ID (optional)
        lga_assignment: New LGA assignment list (optional)
        locked: Lock/unlock the user account (optional)
        updated_by: UUID of the admin performing the update
        
    Returns:
        Updated User object
        
    Raises:
        ValueError: If user not found or if attempting to remove last admin
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    
    changes = {}
    
    # Update role if provided
    if role_id is not None and user.role_id != role_id:
        # Check if this is the last admin and we're changing their role away from admin
        result = await db.execute(select(Role).where(Role.id == user.role_id))
        current_role = result.scalar_one_or_none()
        
        if current_role and current_role.name == "admin" and not user.locked_at:
            # User is currently an active admin, check if they're the last one
            admin_count = await _count_active_admins(db)
            if admin_count <= 1:
                raise ValueError("Cannot change role of the last active admin user")
        
        changes["role_id"] = {"old": user.role_id, "new": role_id}
        user.role_id = role_id
    
    # Update LGA assignment if provided
    if lga_assignment is not None and user.lga_assignment != lga_assignment:
        changes["lga_assignment"] = {"old": user.lga_assignment, "new": lga_assignment}
        user.lga_assignment = lga_assignment

    # Update ward assignment if provided (empty string clears it)
    if ward_assignment is not None and user.ward_assignment != ward_assignment:
        changes["ward_assignment"] = {"old": user.ward_assignment, "new": ward_assignment}
        user.ward_assignment = ward_assignment or None
    
    # Update locked status if provided
    if locked is not None:
        if locked and not user.locked_at:
            user.locked_at = datetime.now(timezone.utc)
            changes["locked"] = True
        elif not locked and user.locked_at:
            user.locked_at = None
            changes["locked"] = False
    
    # Update timestamp
    user.updated_at = datetime.now(timezone.utc)
    
    db.add(user)
    await db.flush()
    
    # Create audit log entry if there were changes
    if changes:
        audit = AuditLog(
            user_id=updated_by,
            operation="update_user",
            entity_type="user",
            entity_id=str(user_id),
            detail=changes,
        )
        db.add(audit)
    
    await db.commit()
    await db.refresh(user)
    
    return user


async def reset_password(
    db: AsyncSession,
    user_id: UUID,
    new_password: str,
    reset_by: UUID,
) -> None:
    """Reset user password.
    
    Args:
        db: Database session
        user_id: UUID of the user whose password to reset
        new_password: New plain text password (will be hashed)
        reset_by: UUID of the admin performing the reset
        
    Raises:
        ValueError: If user not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    
    # Update password and clear failed attempts
    user.password_hash = hash_password(new_password)
    user.failed_attempts = 0
    user.failed_attempts_window_start = None
    user.locked_at = None
    user.updated_at = datetime.now(timezone.utc)
    
    db.add(user)
    await db.flush()
    
    # Create audit log entry
    audit = AuditLog(
        user_id=reset_by,
        operation="reset_password",
        entity_type="user",
        entity_id=str(user_id),
    )
    db.add(audit)
    await db.commit()


async def list_users(
    db: AsyncSession,
    page: int,
    page_size: int,
) -> tuple[int, list[User]]:
    """List all users with pagination.
    
    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of users per page
        
    Returns:
        Tuple of (total_count, list_of_users)
    """
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar() or 0
    
    # Get paginated results
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    users = result.scalars().all()
    
    return total, list(users)


async def deactivate_user(
    db: AsyncSession,
    user_id: UUID,
    deactivated_by: UUID,
) -> None:
    """Deactivate a user account (soft delete).
    
    Args:
        db: Database session
        user_id: UUID of the user to deactivate
        deactivated_by: UUID of the admin performing the deactivation
        
    Raises:
        ValueError: If user not found or if attempting to deactivate last admin
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    
    # Check if this is the last admin
    result = await db.execute(select(Role).where(Role.id == user.role_id))
    user_role = result.scalar_one_or_none()
    
    if user_role and user_role.name == "admin" and not user.locked_at:
        # User is currently an active admin, check if they're the last one
        admin_count = await _count_active_admins(db)
        if admin_count <= 1:
            raise ValueError("Cannot deactivate the last active admin user")
    
    # Lock the user account
    user.locked_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    
    db.add(user)
    await db.flush()
    
    # Create audit log entry
    audit = AuditLog(
        user_id=deactivated_by,
        operation="deactivate_user",
        entity_type="user",
        entity_id=str(user_id),
    )
    db.add(audit)
    await db.commit()
