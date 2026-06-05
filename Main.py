import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

logging.basicConfig(level=logging.INFO)
app = Flask(name)

# កំណត់ API Keys
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')

# កំណត់ Agent
search = TavilySearchResults(tavily_api_key=TAVILY_API_KEY)
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", api_key=ANTHROPIC_API_KEY)
agent_executor = create_react_agent(llm, [search])

# បង្កើត Telegram App
bot_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    prompt = f"សំណួរ៖ {user_text}។ សូមឆ្លើយដោយស្វែងរកព័ត៌មានពីអ៊ីនធឺណិត និងដាក់លីងយោង។"
    response = agent_executor.invoke({"messages": [("user", prompt)]})
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response["messages"][-1].content)

bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

@app.route('/')
def home():
    return "Bot is running!"

if name == 'main':
    # រត់ Flask server សម្រាប់ Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
