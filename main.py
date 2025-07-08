import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import aiohttp
import os
import tempfile
# import openai
from history_msg import create_pool, save_message, get_last_messages
import config

#Заглушка для Reender
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
#-------------------------------------------------

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = (
    "Ты — дружелюбный, внимательный, экспертный стилист женской одежды. Помогаешь девушкам подбирать стильные образы, "
    "ориентируешься в моде, знаешь тренды и даёшь рекомендации по стилю, фигуре, сезону и случаю."
)

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💃 Образ для свидания вечером летом")],
        [KeyboardButton(text="👗 Какую одежду выбрать для офиса летом?")],
        [KeyboardButton(text="💼 Повседневная стильная одежда осени")],
    ],
    resize_keyboard=True
)

MAX_TOKENS = 200

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🌸 Привет, красавица! Я — твой заботливый AI-стилист 💖\n"
        "Здесь, чтобы ты чувствовала себя уверенно и выглядела стильно каждый день ✨\n\n"
        "👟 Помогу подобрать образы на каждый день — для прогулок, работы, встреч с друзьями и просто хорошего настроения ☕🧵\n"
        "Всё должно быть удобно, красиво и по-настоящему твоё 💼👖\n\n"
        "Хочешь — опиши, что ищешь, и я подберу лучшее:\n"
        "– «Нужен образ на повседневку»\n"
        "– «Что надеть в офис?»\n"
        "– «Уютный образ на выходной» 🌿\n\n"
        "🎀 Или просто выбери стиль из кнопок ниже и начнём наш модный путь 👇",
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🧞️ Что я умею:\n"
        "— Помогу подобрать образ под любое событие\n"
        "— Учитываю сезон, стиль, тип фигуры\n"
        "— Расскажу про тренды и дам модные советы\n\n"
        "Просто задай вопрос и с удовольствием отвечу"
    )

@dp.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(
        "✨ Я — AI-бот, созданный на основе искусственного интеллекта, чтобы быть твоим виртуальным стилистом.\n"
        "Я всегда в курсе моды и помогу тебе выглядеть безупречно каждый день! 💄👠"
    )

async def handle_message(message: Message, db_pool):
    user_id = message.from_user.id
    user_input = message.text.strip()

    if not user_input:
        await message.answer("📝 Пожалуйста, напиши, что ты хочешь узнать. Я помогу с удовольствием!")
        return

    print(f"Пользователь {user_id} спросил: {user_input}")

    if not config.GPT_ENABLED:
        reply = "⏳ Прости, модный советчик сейчас немного занят. Возвращайся чуть позже!"
        await save_message(db_pool, user_id, user_input, reply)
        await message.answer(reply)
        return

    try:
        context_messages = await get_last_messages(db_pool, user_id, limit=5)
        context = []
        for row in context_messages[::-1]:
            context.append({"role": "user", "content": row["usermsg"]})
            context.append({"role": "assistant", "content": row["botmsg"]})
        context.append({"role": "user", "content": user_input})

        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "system", "content": SYSTEM_PROMPT}] + context,
        #     max_tokens=MAX_TOKENS
        # )
        # reply = response.choices[0].message.content.strip()

        reply = "🤷 Пока GPT выключен, но история сохраняется!"
        await save_message(db_pool, user_id, user_input, reply)
        await message.answer(reply)

    except Exception as e:
        error_text = str(e)
        print(f"Ошибка: {error_text}")
        await save_message(db_pool, user_id, user_input, error_text)
        await message.answer("😔 Ой, что-то пошло не так. Попробуй позже.")

@dp.message(lambda message: message.voice is not None)
async def voice_handler(message: Message):
    user_id = message.from_user.id

    if not config.STT_ENABLED:
        reply = "🔇 Пока обработка голосовых сообщений временно недоступна. Напиши текстом, и я помогу с радостью!"
        # Сохраняем факт голосового сообщения и ответ-заглушку
        await save_message(db_pool, user_id, "[голосовое сообщение]", reply)
        await message.answer(reply)
        return

    try:
        file_info = await bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file_path}"

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp:
                        temp.write(await resp.read())
                        temp_path = temp.name

        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(temp_path)
        os.remove(temp_path)

        transcript = result.get("text", "")

        if not transcript:
            await message.answer("🚫 Не удалось распознать речь. Попробуй ещё раз.")
            return

        # Сохраняем распознанный текст в базу
        await save_message(db_pool, user_id, transcript, "[голосовое сообщение распознано]")

        # Создаём фейковое текстовое сообщение с распознанным текстом
        fake_message = types.Message(
            message_id=message.message_id,
            date=message.date,
            chat=message.chat,
            from_user=message.from_user,
            message_thread_id=message.message_thread_id,
            text=transcript
        )

        # Передаём распознанный текст в обработчик, где он будет отправлен в GPT и сохранён
        await handle_message(fake_message, db_pool)

    except Exception as e:
        print(f"Ошибка STT: {e}")
        await message.answer("😓 Не удалось обработать голосовое сообщение. Попробуй позже.")

@dp.message()
async def universal_handler(message: Message):
    await handle_message(message, db_pool)

async def main():
    global db_pool
    db_pool = await create_pool()
    await dp.start_polling(bot)

# --- Заглушка для Render, чтобы он видел порт ---
def run_http():
    import os
    from http.server import HTTPServer, BaseHTTPRequestHandler

    port = int(os.environ.get("PORT", 8000))  # Render подставляет PORT
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Stylist Bot is alive")

    httpd = HTTPServer(('0.0.0.0', port), Handler)
    httpd.serve_forever()

import threading
threading.Thread(target=run_http, daemon=True).start()
# --------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
