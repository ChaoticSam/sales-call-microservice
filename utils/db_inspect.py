# inspect.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.models import Call

from app.db import DATABASE_URL

async def inspect():
    engine = create_async_engine(DATABASE_URL, echo=True)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        result = await session.execute(select(Call).limit(5))
        rows = result.scalars().all()
        print("Rows:", rows)

if __name__ == "__main__":
    asyncio.run(inspect())
