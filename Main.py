import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

logging.basicConfig(level=logging.INFO)

# ទាញយក Keys ពី Render
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')

# URL របស់ Render 
RENDER_URL = "https://my-bot-ubfg.onrender.com"

# កំណត់ Agent សម្រាប់ស្វែងរក
search = TavilySearchResults(tavily_api_key=TAVILY_API_KEY)
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", api_key=ANTHROPIC_API_KEY)
agent_executor = create_react_agent(llm, [search])

# មុខងារសម្រាប់ឆ្លើយតបពេលចុច /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="សួស្តី! ខ្ញុំជាជំនួយការ AI របស់អ្នក។ តើមានអ្វីឱ្យខ្ញុំជួយស្វែងរកព័ត៌មានដែរឬទេ?")

# មុខងារសម្រាប់ឆ្លើយសំណួរទូទៅ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    prompt = f"សំណួរ៖ {user_text}។ សូមឆ្លើយដោយស្វែងរកព័ត៌មានពីអ៊ីនធឺណិត និងដាក់លីងយោងឱ្យបានច្បាស់លាស់។"
    
    try:
        response = agent_executor.invoke({"messages": [("user", prompt)]})
        final_answer = response["messages"][-1].content
        await context.bot.send_message(chat_id=update.effective_chat.id, text=final_answer)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="សូមទោស មានបញ្ហាបច្ចេកទេសបន្តិចបន្តួចពេលស្វែងរកព័ត៌មាន។")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # ប្រាប់ Bot ឱ្យស្គាល់ពាក្យ /start និង សារធម្មតា
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # បើកទ្វារចាំទទួលសារពី Telegram ឱ្យបានត្រឹមត្រូវ
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="telegram",  # <--- នេះជាចំណុចសំខាន់ដែលខ្វះកាលពីមុន!
        webhook_url=f"{RENDER_URL}/telegram"
    )
