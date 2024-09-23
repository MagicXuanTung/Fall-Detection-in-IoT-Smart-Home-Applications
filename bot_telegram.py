import asyncio
from telegram import Bot

# Thay thế bằng token của bot của bạn
TOKEN = '7533715892:AAEznW0oScW2u5_tYIsYxGpppwdwJ4QS_AU'
# Thay thế bằng ID chat của bạn hoặc ID nhóm bạn muốn gửi tin nhắn
CHAT_ID = '-4570371594'


async def send_message(token, chat_id, message):
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    message = "có người bị ngã ở đây nhé đến đây"
    asyncio.run(send_message(TOKEN, CHAT_ID, message))
