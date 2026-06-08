import os
import telebot
from flask import Flask, request
from anthropic import Anthropic

# ទាញយក Keys ពី Render Environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
RENDER_APP_URL = os.environ.get("RENDER_APP_URL") # យើងនឹងបង្កើតវានៅជំហានទី ៣

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Anthropic(api_key=CLAUDE_API_KEY)
app = Flask(__name__)

# ផ្នែកទី១៖ ទទួលសារពី Telegram
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# ផ្នែកទី២៖ ទំព័រដើមសម្រាប់ Setup Webhook
@app.route("/")
def webhook_setup():
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_APP_URL + '/' + TELEGRAM_TOKEN)
    return "Bot is running and Webhook is active!", 200

# ផ្នែកទី៣៖ ការគិតរបស់ Claude ពេលមានគេឆាតមក
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": message.text}]
        )
        bot.reply_to(message, response.content[0].text)
    except Exception as e:
        bot.reply_to(message, f"បញ្ហាគឺ Error: {str(e)}")

# ចាប់ផ្តើម Web Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
