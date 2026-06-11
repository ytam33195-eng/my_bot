import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
from anthropic import Anthropic

# ទាញយក Keys ពី Render Environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
RENDER_APP_URL = os.environ.get("RENDER_APP_URL") 

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Anthropic(api_key=CLAUDE_API_KEY)
app = Flask(__name__)

# បង្កើត Dictionary ដើម្បីចងចាំថា User ម្នាក់ៗកំពុងប្រើ Option មួយណា
user_modes = {}

# កំណត់ System Prompts សម្រាប់បែងចែកតួនាទី Bot អោយចំគោលដៅ
SYSTEM_PROMPTS = {
    "society": "អ្នកគឺជាអ្នកជំនាញផ្នែកសង្គមទូទៅ។ សូមឆ្លើយសំណួរទាក់ទងនឹងសង្គម ប្រវត្តិសាស្ត្រ វប្បធម៌ ឬព័ត៌មានទូទៅ។",
    "student": "អ្នកគឺជាគ្រូបង្រៀននិងជាទីប្រឹក្សាសិក្សាដ៏ពូកែ។ សូមពន្យល់មេរៀន វិធីសាស្ត្ររៀន ឬផ្តល់ដំបូន្មានដល់សិស្សានុសិស្ស។",
    "code": "អ្នកគឺជា Senior Software Developer។ សូមឆ្លើយសំណួរទាក់ទងនឹងការសរសេរកូដ ផ្តល់ឧទាហរណ៍កូដច្បាស់លាស់ និងពន្យល់ពី Logic កូដ។",
    "tech": "អ្នកគឺជាអ្នកជំនាញបច្ចេកវិទ្យា។ សូមពន្យល់ពីគន្លឹះបច្ចេកវិទ្យា ឧបករណ៍ទំនើបៗ (Gadgets) AI ឬនិន្នាការថ្មីៗ (Tech Trends)។"
}

# ច្បាប់ទូទៅសម្រាប់ការរៀបចំទម្រង់ចម្លើយ (Formatting & Emojis)
FORMATTING_RULES = """
ច្បាប់នៃការឆ្លើយ: 
១. ត្រូវរៀបចំចម្លើយឲ្យមានរបៀបរៀបរយ ងាយអាន។
២. ប្រើប្រាស់ចំណុច (Bullet points / Numbering) និងបន្លិចអត្ថបទសំខាន់ៗ (Bold text)។
៣. បន្ថែម Emoji ឲ្យបានសមរម្យទៅតាមបរិបទនៃសំណួរ (កុំប្រើច្រើនពេកទាល់តែរញ៉េរញ៉ៃ)។
៤. ឆ្លើយជាភាសាខ្មែរឲ្យបានច្បាស់លាស់និងធម្មជាតិ លើកលែងតែពាក្យបច្ចេកទេស។
"""

# Function សម្រាប់បង្កើតប៊ូតុង Menu ជម្រើស
def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🌍 សង្គមទូទៅ", callback_data="mode_society"),
        InlineKeyboardButton("📚 សិក្សានុសិស្ស", callback_data="mode_student")
    )
    markup.row(
        InlineKeyboardButton("💻 កូដ (Code)", callback_data="mode_code"),
        InlineKeyboardButton("🚀 បច្ចេកវិទ្យា", callback_data="mode_tech")
    )
    return markup

# ផ្នែកទី១៖ ទទួលសារពី Telegram Webhook
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

# ផ្នែកទី៣៖ បង្ហាញ Menu ពេល User ចុច /start ឬ /menu
@bot.message_handler(commands=['start', 'menu'])
def send_menu(message):
    welcome_text = "សួស្តី! 👋 សូមជ្រើសរើសប្រធានបទដែលអ្នកចង់សួរខាងក្រោម ដើម្បីឲ្យខ្ញុំអាចឆ្លើយតបបានចំគោលដៅបំផុត៖"
    bot.reply_to(message, welcome_text, reply_markup=get_main_menu())

# ផ្នែកទី៤៖ ចាប់យកពេល User ចុចរើស Option ណាមួយ
@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def handle_category_selection(call):
    mode = call.data.replace('mode_', '')
    user_modes[call.from_user.id] = mode # ចងចាំជម្រើសរបស់ User
    
    mode_names = {
        "society": "🌍 សង្គមទូទៅ",
        "student": "📚 សិក្សានុសិស្ស",
        "code": "💻 កូដ (Code)",
        "tech": "🚀 បច្ចេកវិទ្យា"
    }
    
    # លុបសញ្ញា Loading លើប៊ូតុង
    bot.answer_callback_query(call.id, f"អ្នកបានជ្រើសរើស {mode_names[mode]}")
    # ប្តូរអត្ថបទចាស់ទៅជាការបញ្ជាក់ជម្រើស
    bot.edit_message_text(
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id,
        text=f"✅ អ្នកកំពុងស្ថិតក្នុងផ្នែក **{mode_names[mode]}** ។\n\nតើអ្នកមានសំណួរអ្វីទាក់ទងនឹងប្រធានបទនេះដែរ? \n*(វាយ /menu ប្រសិនបើអ្នកចង់ប្តូរផ្នែក)*",
        parse_mode='Markdown'
    )

# ផ្នែកទី៥៖ ការគិតរបស់ Claude ពេលមានគេឆាតមក
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    # បើ User មិនទាន់រើស Option ទេ តម្រូវឲ្យរើសសិន
    if user_id not in user_modes:
        bot.reply_to(message, "⚠️ សូមជ្រើសរើសប្រធានបទជាមុនសិន ដោយចុចទីនេះ 👉 /menu")
        return

    # ទាញយកតួនាទី (System Prompt) ទៅតាមជម្រើសដែល User បានរើស
    current_mode = user_modes[user_id]
    final_system_prompt = SYSTEM_PROMPTS[current_mode] + "\n" + FORMATTING_RULES

    # បង្ហាញសញ្ញា Typing... ឲ្យ User ដឹងថា Bot កំពុងគិត
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022", # ប្រើ Model ត្រឹមត្រូវ
            max_tokens=2048, # បង្កើន Token ឲ្យអាចឆ្លើយបានវែងជាងមុនបន្តិច
            system=final_system_prompt, # បញ្ចូលច្បាប់ឲ្យ AI អនុវត្ត
            messages=[{"role": "user", "content": message.text}]
        )
        # ប្រើ parse_mode='Markdown' ដើម្បីឲ្យ Telegram ស្គាល់អក្សរដិត និង Bullet points
        bot.reply_to(message, response.content[0].text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ មានបញ្ហាបច្ចេកទេស (Error): {str(e)}")

# ចាប់ផ្តើម Web Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
