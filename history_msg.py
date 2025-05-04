import asyncpg
import config

# Создание пула соединений
async def create_pool():
    return await asyncpg.create_pool(dsn=config.DATABASE_URL)

# Сохранить сообщение в таблицу messages
async def save_message(pool, user_id, user_msg, bot_msg):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO messages (userid, usermsg, botmsg, datemsg)
            VALUES ($1, $2, $3, NOW())
            """,
            user_id, user_msg, bot_msg
        )
