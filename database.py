"""Sqlite3 Wrapper for the sqlite3 package for Python"""
from aiosqlite import connect
from typing import Optional, Tuple

DATABASE_URL = r"bot.db"

@staticmethod
async def execute_query(query: str, parameters: Optional[Tuple]):
    """A high level, all round query executor designed to modify the database to anything."""
    async with connect(DATABASE_URL) as conn:
        async with conn.cursor() as c:
            if parameters is not None:
                await c.execute(query, parameters)
            elif parameters is None:
                await c.execute(query)
            if "SELECT" in query:
                if "*" in query:
                    return await c.fetchall()
                else:
                    return await c.fetchone()
            elif "CREATE" in query or "INSERT" in query:
                await conn.commit()
        await conn.close()
    return "Error! the database connection was not created."
