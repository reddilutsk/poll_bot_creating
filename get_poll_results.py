from telegram import Bot
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
import asyncio
import json
import os

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

def load_poll_data():
    filename = 'poll_data.json'
    
    # Перевіряємо, чи файл взагалі існує, щоб скрипт не "впав" при першому запуску
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return data
    else:
        print("Файл poll_data.json не знайдено. Можливо, це перший запуск?")
        return None

def extract_wed_thu(meta):
    wed = None
    thu = None

    for key in meta.keys():
        if "Середа" in key:
            wed = key
        elif "Четвер" in key:
            thu = key

    return wed, thu

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TABLE_NAME = 'Telegram Poll Results'

POLL_META = load_poll_data()
_, wed = extract_wed_thu(POLL_META)

bot = Bot(token=TOKEN)

async def main():
    await bot.delete_webhook(drop_pending_updates=False)
    results = {}

    updates = await bot.get_updates(timeout=10)

    for u in updates:
        if not u.poll_answer:
            continue

        pa = u.poll_answer

        poll_id = pa.poll_id
        if poll_id not in POLL_META[wed].get("poll_id"):
            continue

        user = pa.user
        user_id = user.id

        answers = [POLL_META[wed].get("options")[i] for i in pa.option_ids]

        results[user_id] = {"Full_Name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                            "Username": user.username,
                            wed: ", ".join(answers)}
        
    new_df = pd.DataFrame.from_dict(results, orient='index')
    # await bot.stop_poll(chat_id=CHAT_ID,
    #                     message_id=POLL_META[wed]['message_id'])

    gc = gspread.service_account(filename='credentials.json')

    sh = gc.open(TABLE_NAME)
    worksheet = sh.get_worksheet(0)

    data = worksheet.get_all_values()

    old_df = pd.DataFrame(data[1:], columns=data[0])
    if len(old_df) > 0:
        old_df.set_index("User_ID", inplace=True)

    df = update_table(old_df, new_df)
    worksheet.clear()
    set_with_dataframe(worksheet, df, row=1, col=1, include_index=True)

if __name__ == "__main__":
    asyncio.run(main())