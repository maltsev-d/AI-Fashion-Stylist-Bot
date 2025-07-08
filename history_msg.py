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
            INSERT INTO user_bot_dialog (userid, usermsg, botmsg, datemsg)
            VALUES ($1, $2, $3, NOW())
            """,
            user_id, user_msg, bot_msg
        )

# Получить последние N сообщений для пользователя
async def get_last_messages(pool, user_id, limit=5):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT usermsg, botmsg FROM user_bot_dialog
            WHERE userid = $1
            ORDER BY datemsg DESC
            LIMIT $2
            """,
            user_id, limit
        )
        return rows
