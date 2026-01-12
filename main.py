import json
import asyncio
from telegram import Bot
from datetime import date, timedelta
import os


UA_WEEKDAYS = {
    0: "Понеділок",
    1: "Вівторок",
    2: "Середа",
    3: "Четвер",
    4: "Пʼятниця",
    5: "Субота",
    6: "Неділя",
}

def next_week_wed_thu(today: date | None = None):
    if today is None:
        today = date.today()

    # weekday(): Monday=0 ... Sunday=6
    WEDNESDAY = 2
    THURSDAY = 3

    days_until_wed = (WEDNESDAY - today.weekday()) % 7
    days_until_thu = (THURSDAY - today.weekday()) % 7

    # Якщо сьогодні середа або пізніше — беремо наступний тиждень
    if today.weekday() >= WEDNESDAY:
        days_until_wed += 7
        days_until_thu += 7

    wednesday = today + timedelta(days=days_until_wed)
    thursday = today + timedelta(days=days_until_thu)

    wed_str = f"{UA_WEEKDAYS[wednesday.weekday()]}, {wednesday.strftime('%d.%m')}"
    thu_str = f"{UA_WEEKDAYS[thursday.weekday()]}, {thursday.strftime('%d.%m')}"

    return wed_str, thu_str

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
THREAD_ID = os.environ.get('TELEGRAM_THREAD_ID')

wed, thu = next_week_wed_thu(today=None)

# Параметри опитування
QUESTION_W = wed + ", 20:00, чисто тренування, Ерідон"
QUESTION_T = thu + ", 20:00, тренування/спаринг, Ерідон"
OPTIONS = ["󠀼✅👟", "󠀼✅🧤", "󠀭️❌", "🧠"]

async def main():
    bot = Bot(token=TOKEN)
    
    # Надсилаємо опитування
    w_poll_message = await bot.send_poll(
                    chat_id=CHAT_ID,
                    message_thread_id=THREAD_ID,
                    question=QUESTION_W,
                    options=OPTIONS,
                    is_anonymous=False,      # Щоб ви могли бачити результати
                    allows_multiple_answers=False)

    # Надсилаємо опитування
    t_poll_message = await bot.send_poll(
                    chat_id=CHAT_ID,
                    message_thread_id=THREAD_ID,
                    question=QUESTION_T,
                    options=OPTIONS,
                    is_anonymous=False,      # Щоб ви могли бачити результати
                    allows_multiple_answers=False)

    # Формуємо дані для збереження
    data_to_save = { wed:{"poll_id": w_poll_message.poll.id,
                          "message_id": w_poll_message.message_id,
                          "options": OPTIONS},
                     thu:{"poll_id": t_poll_message.poll.id,
                          "message_id": t_poll_message.message_id,
                          "options": OPTIONS},}

    # Записуємо у файл
    with open('poll_data.json', 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(main())