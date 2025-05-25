# 👗 Stylist Telegram Bot

AI-стилист на базе OpenAI GPT, который помогает подбирать модные образы для девушек, учитывая сезон, стиль, тип фигуры и событие. Бот работает через Telegram, сохраняет историю сообщений в PostgreSQL и использует OpenAI API для генерации ответов.

---

## 🚀 Возможности

- Подбор образов по заданному описанию
- Встроенные кнопки с популярными стилями
- Сохранение истории диалогов в базе данных
- Быстрый запуск и кастомизация через `.env`

---

## 🛠 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/stylist_bot.git
cd stylist_bot
```

### 2. Установка зависимостей

Установите зависимости с помощью `pip`:

```bash
pip install -r requirements.txt
```

Если файла `requirements.txt` нет, используйте:

```bash
pip install aiogram openai asyncpg python-dotenv
```

---

### 3. Создание файла `.env`

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
BOT_TOKEN=ваш_токен_бота
OPENAI_API_KEY=ваш_openai_api_ключ
DATABASE_URL=postgresql://user:password@host:port/database
```

❗ Никогда не коммитьте `.env` в Git!

---

## ▶️ Запуск

Запустите бота командой:

```bash
python main.py
```

Убедитесь, что база данных доступна, и переменные окружения настроены правильно.

---

## 🧠 Работа OpenAI

Используется модель `gpt-4.1-mini`. Контекст — дружелюбный женский стилист. Вызов API осуществляется через библиотеку `openai`:

```python
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ],
    max_tokens=MAX_TOKENS
)
```

---

## 🗃 База данных

Используется PostgreSQL для хранения истории сообщений. Таблица `messages` создаётся следующим SQL-запросом:

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    user_message TEXT,
    bot_reply TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

Работа с базой реализована в `history_msg.py` через библиотеку `asyncpg`.

---

## 🧾 Структура проекта

```plaintext
stylist_bot/
├── .env                # Секреты (ключи, токены)
├── .gitignore          # Исключения из git
├── README.md           # Документация проекта
├── main.py             # Главный файл бота
├── config.py           # Переменные окружения
└── history_msg.py      # Работа с PostgreSQL
```

---

## ⛔ .gitignore

```gitignore
__pycache__/
*.pyc
.env
.vscode/
.idea/
.DS_Store
```

---

## 📌 TODO

- [ ] Добавить логирование ошибок
- [ ] Реализовать кастомные стили и типы фигур
- [ ] Автоматический деплой на Railway или Render
- [ ] Поддержка голосовых и изображений (в будущем)
- [ ] Интеграция с Google Sheets или Notion (для стилистов)

---

## 📞 Обратная связь

По любым вопросам и предложениям пиши: [@dmitriimaltsev](https://t.me/dmitriimaltsev)

---

## 💡 Лицензия

Проект распространяется по лицензии MIT — можно использовать, изменять и распространять в любых целях.