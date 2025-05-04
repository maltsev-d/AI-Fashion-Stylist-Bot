import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI
from history_msg import create_pool, save_message
import config



bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

client = OpenAI(api_key=config.OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "Ты — дружелюбный, внимательный, экспертный стилист женской одежды. Помогаешь девушкам подбирать стильные образы, "
    "ориентируешься в моде, знаешь тренды и даёшь рекомендации по стилю, фигуре, сезону и случаю."
)

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💃 Образ для свидания вечером летом")],
        [KeyboardButton(text="👗 Какую одежду выбрать для офиса летом?")],
        [KeyboardButton(text="👜 Повседневная стильная одежда осени")],
    ],
    resize_keyboard=True
)

MAX_TOKENS = 200

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🌸 Привет, красавица! Я — твой заботливый AI-стилист 💖\n"
        "Здесь, чтобы ты чувствовала себя уверенно и выглядела стильно каждый день ✨\n\n"
        "👟 Помогу подобрать образы на каждый день — для прогулок, работы, встреч с друзьями и просто хорошего настроения ☕🧥\n"
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
        "🧾 Что я умею:\n"
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

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            max_tokens=MAX_TOKENS
        )
        reply = response.choices[0].message.content.strip()
        print(f"Бот ответил: {reply}")

        await save_message(db_pool, user_id, user_input, reply)
        await message.answer(reply)

    except Exception as e:
        # Простой вывод ошибки
        error_text = str(e)
        print(f"Ошибка API: {error_text}")

        # Сохраняем в базе данных
        await save_message(db_pool, user_id, user_input, error_text)
        await message.answer("😔 Ой, что-то пошло не так. Попробуй позже.")

@dp.message()
async def universal_handler(message: Message):
    await handle_message(message, db_pool)

async def main():
    global db_pool
    db_pool = await create_pool()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
