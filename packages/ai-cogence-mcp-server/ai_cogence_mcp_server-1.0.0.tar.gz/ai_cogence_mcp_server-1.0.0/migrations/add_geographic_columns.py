"""
Database migration to add geographic tracking columns to chat_sessions table
Run this script to add geographic analytics support to existing databases
"""

import asyncio
import logging
from connectors.db import db_pool

logger = logging.getLogger(__name__)

async def add_geographic_columns():
    """Add geographic columns to existing chat_sessions table"""
    try:
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Check if geographic columns already exist
                await cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'chat_sessions' 
                    AND column_name = 'country'
                """)
                
                existing_column = await cur.fetchone()
                
                if existing_column:
                    print("✅ Geographic columns already exist!")
                    return
                
                print("🔄 Adding geographic columns to chat_sessions table...")
                
                # Add geographic columns
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS client_ip VARCHAR;
                """)
                
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS country VARCHAR;
                """)
                
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS country_code VARCHAR;
                """)
                
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS region VARCHAR;
                """)
                
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS city VARCHAR;
                """)
                
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8);
                """)
                
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8);
                """)
                
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS timezone VARCHAR;
                """)
                
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS isp VARCHAR;
                """)
                
                await cur.execute("""
                    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS geo_data JSON;
                """)
                
                await conn.commit()
                
                print("✅ Geographic columns added successfully!")
                
                # Optionally populate existing sessions with default geographic data
                print("🔄 Updating existing sessions with default geographic data...")
                
                await cur.execute("""
                    UPDATE chat_sessions 
                    SET 
                        client_ip = '127.0.0.1',
                        country = 'Development',
                        country_code = 'DEV',
                        region = 'Local',
                        city = 'Development',
                        latitude = 37.7749,
                        longitude = -122.4194,
                        timezone = 'UTC',
                        isp = 'Development',
                        geo_data = '{"ip": "127.0.0.1", "country": "Development", "country_code": "DEV", "region": "Local", "city": "Development", "latitude": 37.7749, "longitude": -122.4194, "timezone": "UTC", "isp": "Development", "source": "migration"}'::json
                    WHERE country IS NULL
                """)
                
                rows_updated = cur.rowcount
                await conn.commit()
                
                print(f"✅ Updated {rows_updated} existing sessions with default geographic data")
                print("🎉 Geographic analytics migration completed successfully!")
                
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        print(f"❌ Migration failed: {str(e)}")
        raise

async def main():
    """Main migration function"""
    print("🚀 Starting geographic analytics migration...")
    
    try:
        await add_geographic_columns()
        print("✅ Migration completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # Run the migration
    success = asyncio.run(main())
    exit(0 if success else 1)