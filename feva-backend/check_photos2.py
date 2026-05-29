import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

DATABASE_URL = 'postgresql+asyncpg://feva:feva_dev_pass@localhost:5433/feva'

async def check():
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as db:
        # Check device_local_id on streets
        r = await db.execute(text("""
            SELECT id, street_id, device_local_id, device_id
            FROM streets
            WHERE street_id LIKE 'STR-Asaba%'
            ORDER BY created_at DESC
        """))
        print('=== STREETS device_local_id ===')
        for row in r.fetchall():
            print(row)

        # Check device_local_id on buildings
        r2 = await db.execute(text("""
            SELECT id, building_id, device_local_id, device_id
            FROM buildings
            WHERE building_id LIKE 'BLD-Asaba%'
            ORDER BY created_at DESC
        """))
        print('\n=== BUILDINGS device_local_id ===')
        for row in r2.fetchall():
            print(row)

        # Check if any photos have record_id matching these streets/buildings
        r3 = await db.execute(text("""
            SELECT p.photo_id, p.record_type, p.record_id, p.storage_path
            FROM photos p
            WHERE p.record_id IN (
                SELECT id FROM streets WHERE street_id LIKE 'STR-Asaba%'
                UNION
                SELECT id FROM buildings WHERE building_id LIKE 'BLD-Asaba%'
            )
        """))
        print('\n=== PHOTOS for Asaba records ===')
        rows = r3.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print('NO PHOTOS FOUND')

asyncio.run(check())
