import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session", autouse=True)
async def cleanup_test_data():
    """Clean up stale test data from previous runs before the test session starts."""
    from app.db.session import AsyncSessionLocal
    from app.models.user import User
    from app.models.building import Building
    from app.models.street import Street
    from sqlalchemy import select, delete, text

    # Usernames created by tests that may persist across runs
    test_usernames = [
        "newuser123", "duplicate_test", "update_test_user", "deactivate_test_user",
        "reset_pwd_user", "test_user_for_role_change", "test_user_for_deactivation",
        "test_user_for_deactivation2", "admin_to_change", "admin_to_deactivate",
        "second_admin", "test_enumerator2", "test_supervisor", "stronguser",
        # test_password_and_rate_limiting.py
        "ratelimituser", "windowresetuser", "resetcounteruser",
        "adminuser", "qauser", "enumuser",
        # test_user_management_endpoints.py
        "updatetest", "deletetest", "resettest", "weakresettest",
        "secondadmin", "thirdadmin",
    ]
    # Building IDs created by tests
    test_building_prefixes = [
        "BLD-PENDING-", "BLD-APPROVED-", "BLD-REJECTED-",
        "BLD-TEST-", "TEST-BLD-", "STAT-BLD-",
        "BLD-ADMIN-APPROVED-", "BLD-ADMIN-REJECTED-",
        "BLD-ENUM-APPROVED-", "BLD-ENUM-REJECTED-",
        "BLD-REVIEW-", "BLD-DAY", "BLD-JAN",
        "TEST-BLD-APPROVE-", "TEST-BLD-REJECT-",
    ]
    test_street_prefixes = ["STR-PENDING-", "STR-TEST-", "STAT-STR-", "STR-REVIEW-", "TEST-STR-"]

    try:
        async with AsyncSessionLocal() as db:
            # Disable immutability triggers for cleanup (re-enabled after commit)
            await db.execute(text("SET session_replication_role = replica"))

            # Delete buildings first (they reference streets via FK)
            for prefix in test_building_prefixes:
                await db.execute(
                    delete(Building).where(Building.building_id.like(f"{prefix}%"))
                )
            # Also delete any buildings that reference test streets
            for prefix in test_street_prefixes:
                result = await db.execute(
                    select(Street.street_id).where(Street.street_id.like(f"{prefix}%"))
                )
                street_ids = [row[0] for row in result.fetchall()]
                if street_ids:
                    await db.execute(
                        delete(Building).where(Building.street_id.in_(street_ids))
                    )
            await db.flush()

            # Now delete test streets
            for prefix in test_street_prefixes:
                await db.execute(
                    delete(Street).where(Street.street_id.like(f"{prefix}%"))
                )
            await db.flush()

            # Delete audit logs for test users (triggers disabled)
            from app.models.audit_log import AuditLog
            for username in test_usernames:
                result = await db.execute(select(User).where(User.username == username))
                user = result.scalar_one_or_none()
                if user:
                    await db.execute(
                        delete(AuditLog).where(AuditLog.user_id == user.id)
                    )
            await db.flush()

            # Delete test users
            for username in test_usernames:
                result = await db.execute(select(User).where(User.username == username))
                user = result.scalar_one_or_none()
                if user:
                    await db.delete(user)
            await db.flush()

            # Reset failed_attempts for test users to clear rate limiting
            for username in ["test_admin", "test_qa", "test_enumerator", "admin", "testuser"]:
                result = await db.execute(select(User).where(User.username == username))
                user = result.scalar_one_or_none()
                if user and user.failed_attempts > 0:
                    user.failed_attempts = 0
                    user.failed_attempts_window_start = None
                    user.locked_at = None

            await db.commit()
            # Restore trigger behavior
            await db.execute(text("SET session_replication_role = DEFAULT"))
            await db.commit()
    except Exception as e:
        # Don't block tests if cleanup fails — just warn
        import warnings
        warnings.warn(f"Test data cleanup failed (non-fatal): {e}")

    yield


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac



@pytest.fixture
async def async_client() -> AsyncClient:
    """Async client fixture for async tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def admin_user(async_db_session):
    """Get or create an admin user for testing."""
    from app.models.user import User
    from app.models.role import Role
    from app.core.security import hash_password
    from sqlalchemy import select

    # Get or create admin role
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one_or_none()
    if not admin_role:
        admin_role = Role(id=1, name="admin")
        async_db_session.add(admin_role)
        await async_db_session.flush()

    # Get or create admin user
    result = await async_db_session.execute(select(User).where(User.username == "test_admin"))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            username="test_admin",
            email="admin@test.com",
            password_hash=hash_password("admin123"),
            role_id=admin_role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        await async_db_session.refresh(user)
    else:
        # Ensure the user has the correct admin role and password
        needs_update = False
        if user.role_id != admin_role.id:
            user.role_id = admin_role.id
            needs_update = True
        from app.core.security import verify_password
        if not verify_password("admin123", user.password_hash):
            user.password_hash = hash_password("admin123")
            needs_update = True
        if needs_update:
            await async_db_session.commit()
        await async_db_session.refresh(user)

    return user


@pytest.fixture
async def qa_user(async_db_session):
    """Get or create a QA officer user for testing."""
    from app.models.user import User
    from app.models.role import Role
    from app.core.security import hash_password
    from sqlalchemy import select

    # Get or create qa_officer role
    result = await async_db_session.execute(select(Role).where(Role.name == "qa_officer"))
    qa_role = result.scalar_one_or_none()
    if not qa_role:
        qa_role = Role(id=4, name="qa_officer")
        async_db_session.add(qa_role)
        await async_db_session.flush()

    # Get or create QA user
    result = await async_db_session.execute(select(User).where(User.username == "test_qa"))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            username="test_qa",
            email="test_qa@test.com",
            password_hash=hash_password("testpass123"),
            role_id=qa_role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        await async_db_session.refresh(user)
    else:
        # Ensure the user has the correct qa_officer role
        if user.role_id != qa_role.id:
            user.role_id = qa_role.id
            await async_db_session.commit()
        await async_db_session.refresh(user)

    return user


@pytest.fixture
async def enumerator_user(async_db_session):
    """Get or create an enumerator user for testing."""
    from app.models.user import User
    from app.models.role import Role
    from app.core.security import hash_password
    from sqlalchemy import select

    # Get or create enumerator role
    result = await async_db_session.execute(select(Role).where(Role.name == "enumerator"))
    enum_role = result.scalar_one_or_none()
    if not enum_role:
        enum_role = Role(id=2, name="enumerator")
        async_db_session.add(enum_role)
        await async_db_session.flush()

    # Get or create enumerator user
    result = await async_db_session.execute(select(User).where(User.username == "test_enumerator"))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            username="test_enumerator",
            email="enumerator@test.com",
            password_hash=hash_password("testpass123"),
            role_id=enum_role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        await async_db_session.refresh(user)
    else:
        # Ensure the user has the correct enumerator role
        if user.role_id != enum_role.id:
            user.role_id = enum_role.id
            await async_db_session.commit()
        await async_db_session.refresh(user)

    return user


@pytest.fixture
async def admin_token(admin_user):
    """Generate an access token for the admin user."""
    from app.core.security import create_access_token

    return create_access_token(
        {"sub": str(admin_user.id), "role": "admin"}
    )


@pytest.fixture
async def qa_token(qa_user):
    """Generate an access token for the QA user."""
    from app.core.security import create_access_token

    return create_access_token(
        {"sub": str(qa_user.id), "role": "qa_officer"}
    )


@pytest.fixture
async def enumerator_token(enumerator_user):
    """Generate an access token for the enumerator user."""
    from app.core.security import create_access_token

    return create_access_token(
        {"sub": str(enumerator_user.id), "role": "enumerator"}
    )


@pytest.fixture
async def async_db_session():
    """Create an async database session for testing."""
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        yield session
        try:
            await session.rollback()
        except Exception:
            pass


@pytest.fixture
async def db(async_db_session):
    """Alias for async_db_session for convenience."""
    return async_db_session


@pytest.fixture
async def test_admin(admin_user):
    """Alias for admin_user for convenience."""
    return admin_user


@pytest.fixture
async def test_qa_officer(qa_user):
    """Alias for qa_user for convenience."""
    return qa_user


@pytest.fixture
async def test_enumerator(enumerator_user):
    """Alias for enumerator_user for convenience."""
    return enumerator_user


@pytest.fixture
def qa_officer_token(qa_token):
    """Alias for qa_token for convenience."""
    return qa_token
