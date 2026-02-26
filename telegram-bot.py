import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("""
به ربات تکالیف خوش آمدید.
برای دیدن تکالیف یا ارسال آن‌ها از دستور مربوطه استفاده کنید.
""")
    
async def menu(update,context):
    options = [
        [InlineKeyboardButton("دربافت تکالیف",callback_data='')]
        [InlineKeyboardButton("ارسال تکالیف",callback_data='')]
    ]
    
    output = InlineKeyboardMarkup(options)
    await update.message.reply_text("Choose : ", reply_markup = output)

async def replay(update, context):
    # text = update.message.text
    await update.message.reply_text("""
لطفاً از این ربات برای ارسال پیام استفاده نکنید.
این ربات تنها جهت مشاهده و ارسال تکالیف است
""")
    
async def show_homework(update, context):
    pass

    




app = ApplicationBuilder().token(TOKEN).build() # Always at the end of our application/program

# ==================================== START OF OUR HANDLERS ====================================

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, replay))
# app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, remember))



# ===================================== END OF OUR HANDLERS =====================================

app.run_polling() # Always at the end of our application/program
