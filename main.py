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

def next_week_wed_thu(today=None):
    if today is None:
        today = date.today()

    # Понеділок наступного тижня
    next_monday = today + timedelta(days=(7 - today.weekday()))

    wednesday = next_monday + timedelta(days=2)
    thursday  = next_monday + timedelta(days=3)

    wed_str = f"{UA_WEEKDAYS[wednesday.weekday()]}, {wednesday.strftime('%d.%m')}"
    thu_str = f"{UA_WEEKDAYS[thursday.weekday()]}, {thursday.strftime('%d.%m')}"

    return wed_str, thu_str

def update_table(df_old, df_new):

  df_old.index = df_old.index.astype(int)
  df_new.index = df_new.index.astype(int)

  df_combined = df_old.combine_first(df_new)  # залишає старі значення, якщо нових немає
  df_combined.update(df_new)  # оновлюємо значення для існуючих рядків

  # --- Додаємо нові колонки справа ---
  old_cols = list(df_old.columns)
  new_cols = [col for col in df_combined.columns if col not in old_cols]
  ordered_cols = old_cols + new_cols
  df_combined = df_combined[ordered_cols]

  # Замінити NaN та нескінченність на пустий рядок
  df_clean = df_combined.replace([float('inf'), float('-inf')], None).fillna('')
  df_clean.index.name = "User_ID"

  return df_clean

# TOKEN = '7770236578:AAGrkL_bDEq9N6NLsKYTePL8Ac6XglN4t10'
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

CHAT_ID = '-1002643965663'
THREAD_ID = '16'

# Параметри опитування
QUESTION_W = ", 20:00, чисто тренування, Ерідон"
QUESTION_T = ", 20:00, тренування/спаринг, Ерідон"
OPTIONS = ["󠀼✅👟", "󠀼✅🧤", "󠀭️❌", "🧠"]

wed, thu = next_week_wed_thu(today=None)

QUESTION = wed + QUESTION_W

async def main():
    bot = Bot(token=TOKEN)
    
    # Надсилаємо опитування
    await bot.send_poll(
        chat_id=CHAT_ID,
        question=QUESTION,
        options=OPTIONS,
        is_anonymous=False,      # Щоб ви могли бачити результати
        allows_multiple_answers=False
    )
    print("Опитування надіслано успішно!")

if __name__ == "__main__":
    asyncio.run(main())

# poll_message = await bot.send_poll(
#                 chat_id=CHAT_ID,
#                 message_thread_id=THREAD_ID,
#                 question=QUESTION,
#                 options=OPTIONS,
#                 is_anonymous=False)

# poll_id = poll_message.poll.id

# POLL_META = {"poll_id": poll_id,
#              "date": wed,
#              "mesg_id": poll_message.message_id,
#              "options": OPTIONS}