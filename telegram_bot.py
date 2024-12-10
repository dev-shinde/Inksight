import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import jenkins
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram bot token
TELEGRAM_TOKEN = "7615186502:AAERfajBvWWX6SxL8dI6efA4ijSSgSGuIvQ"

# Your Jenkins details
JENKINS_URL = "http://10.0.2.15/:8080"  # Update this
JENKINS_USER = "admin"         # Update this
JENKINS_PASS = "1123b299fdb4b76cac12d59ab71ccbf9fb"        # Update this with token from step 1

# Your Telegram chat ID
ALLOWED_CHAT_ID = 997388436

def start(update, context):
    update.message.reply_text('Hi! Use /build to trigger the InkSight pipeline.')

def trigger_build(update, context):
    chat_id = update.message.chat_id
    
    if chat_id != ALLOWED_CHAT_ID:
        update.message.reply_text("You're not authorized to trigger builds.")
        return
    
    try:
        server = jenkins.Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_PASS)
        server.build_job('InkSight-Pipeline')
        update.message.reply_text("🚀 Build triggered! I'll notify you when it's complete.")
        
    except Exception as e:
        logger.error(f"Error triggering build: {str(e)}")
        update.message.reply_text(f"❌ Failed to trigger build: {str(e)}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("build", trigger_build))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print("Bot is starting...")
    main()
