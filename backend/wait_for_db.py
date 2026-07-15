import asyncio
import sys
import os
import time

# Add current directory to path to allow importing app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_connection():
    # Mask database password in console output for security
    url_parts = settings.DATABASE_URL.split("@")
    host_info = url_parts[-1] if len(url_parts) > 1 else settings.DATABASE_URL
    print(f"Connecting to database at {host_info} ...")
    
    engine = create_async_engine(settings.DATABASE_URL)
    
    for attempt in range(1, 31):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("Database connection verified successfully!")
            await engine.dispose()
            return True
        except Exception as e:
            print(f"Attempt {attempt}/30: Database is not ready yet. Retrying in 2 seconds... (Error: {e})")
            await asyncio.sleep(2)
            
    await engine.dispose()
    return False

if __name__ == "__main__":
    success = asyncio.run(check_connection())
    if not success:
        print("Could not connect to database after 30 attempts. Exiting.")
        sys.exit(1)
