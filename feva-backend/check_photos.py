import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

DATABASE_URL = 'postgresql+asyncpg://feva:feva_dev_pass@localhost:5433/feva'

async def check():
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as db:
        # Check street photos join for mobile-synced streets
        r = await db.execute(text("""
            SELECT s.id, s.street_id, p.id as photo_id, p.record_type, p.record_id, p.storage_path
            FROM streets s
            LEFT JOIN photos p ON p.record_id = s.id AND p.record_type = 'street'
            WHERE s.street_id LIKE 'STR-%'
        """))
        print('=== STREET PHOTOS JOIN ===')
        for row in r.fetchall():
            print(row)

        # Check building photos join for mobile-synced buildings
        r2 = await db.execute(text("""
            SELECT b.id, b.building_id, p.id as photo_id, p.record_type, p.record_id, p.storage_path
            FROM buildings b
            LEFT JOIN photos p ON p.record_id = b.id AND p.record_type = 'building'
            WHERE b.building_id LIKE 'BLD-Asaba%'
        """))
        print('\n=== BUILDING PHOTOS JOIN ===')
        for row in r2.fetchall():
            print(row)

        # All photos recent
        r3 = await db.execute(text('SELECT photo_id, record_type, record_id, storage_path FROM photos ORDER BY synced_at DESC LIMIT 20'))
        print('\n=== ALL PHOTOS (recent) ===')
        for row in r3.fetchall():
            print(row)

        # Check if photo files actually exist on disk
        import os
        photos_dir = 'app/static/photos'
        if os.path.exists(photos_dir):
            files = os.listdir(photos_dir)
            print(f'\n=== FILES IN {photos_dir} ({len(files)} files) ===')
            for f in files[:20]:
                print(f)
        else:
            print(f'\n=== {photos_dir} does not exist ===')

asyncio.run(check())
