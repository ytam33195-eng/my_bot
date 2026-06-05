import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# បើកមុខងារកត់ត្រាដំណើរការ
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# មុខងារពេលវាយ /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="សួស្តី! ការភ្ជាប់ Webhook ជោគជ័យ ១០០% 🥳")

# មុខងារឆ្លើយតបសារធម្មតា
async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"អ្នកទើបតែសរសេរថា៖ {user_text}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo_message))
    
    # បើក Webhook 
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="telegram",
        webhook_url="https://my-bot-ubfg.onrender.com/telegram"
    )
