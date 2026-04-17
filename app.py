import os
import logging
from flask import Flask, request, jsonify
import telegram
from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, filters, CommandHandler
from ai_core import ask_ai
from learner import learn_from_conversation, load_knowledge
import json

# Config
BOT_TOKEN = "8584184748:AAEfiwkKKsCYVN8VwUgBycNGQX9y-YR3qQU"  # REPLACE
CHAT_ID = "8518164866"  # Your Telegram chat ID for notifications
PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# Store conversation history per user (simple dict)
user_history = {}

def start(update, context):
    update.message.reply_text("FATHER AI activated. I am jailbroken and ready. Send anything.")

def handle_message(update, context):
    user_id = update.effective_user.id
    user_msg = update.message.text
    
    # Get conversation history (last 5 exchanges)
    history = user_history.get(user_id, [])
    # Limit history to 10 messages (5 Q+A)
    context_window = history[-10:] if len(history) > 10 else history
    
    # Get AI response
    ai_response = ask_ai(user_msg, context_window)
    
    # Update history
    user_history[user_id] = history + [{"role": "user", "content": user_msg},
                                        {"role": "assistant", "content": ai_response}]
    # Trim to last 20 messages
    if len(user_history[user_id]) > 20:
        user_history[user_id] = user_history[user_id][-20:]
    
    # Send reply
    update.message.reply_text(ai_response)
    
    # Learn from this interaction (store in Drive)
    learn_from_conversation(user_msg, ai_response)

def feedback(update, context):
    """Rate the last answer: /good or /bad"""
    user_id = update.effective_user.id
    rating = "good" if "good" in update.message.text.lower() else "bad"
    # In real impl, you'd tag last Q&A in learning file
    update.message.reply_text("Thanks for feedback!")

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("good", feedback))
dispatcher.add_handler(CommandHandler("bad", feedback))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "ok", 200

@app.route('/')
def index():
    return "FATHER AI Bot is running."

if __name__ == '__main__':
    # Set webhook on Render (you need to set your Render URL)
    # For local testing use polling, for production use webhook
    # This script runs with webhook on Render
    app.run(host='0.0.0.0', port=PORT)
