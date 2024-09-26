from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

from app.config import REAL_DATABASE_URL


print(REAL_DATABASE_URL)
engine = create_async_engine(REAL_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
