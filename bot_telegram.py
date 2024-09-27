import asyncio
from telegram import Bot

TOKEN = '7533715892:AAEznW0oScW2u5_tYIsYxGpppwdwJ4QS_AU'
CHAT_ID = '-4570371594'


async def send_message(token, chat_id, message):
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    message = "Phát hiện có người bị ngã trong khung hình!"
    asyncio.run(send_message(TOKEN, CHAT_ID, message))
