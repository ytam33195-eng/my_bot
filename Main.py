import os
import telebot
from anthropic import Anthropic

# ទាញយក Token និង Key ពី Render Environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Anthropic(api_key=CLAUDE_API_KEY)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    
    try:
        # ប្រើប្រាស់ Claude ដើម្បឆ្លើយតប
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620", 
            max_tokens=1024,
            messages=[
                {"role": "user", "content": user_input}
            ]
        )
        
        reply_text = response.content[0].text
        bot.reply_to(message, reply_text)
        
    except Exception as e:
        bot.reply_to(message, "សុំទោស! មានបញ្ហាក្នុងការគិតបន្តិច។")
        print(f"Error: {e}")

bot.polling()
