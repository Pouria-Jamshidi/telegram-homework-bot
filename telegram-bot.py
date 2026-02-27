import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
import csv
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


# ==================================== HANDLERS ====================================

async def start(update, context):
    await update.message.reply_text("""
به ربات تکالیف خوش آمدید.
برای دیدن تکالیف یا ارسال آن‌ها از دستور مربوطه استفاده کنید.
""")
    # Automatically show menu buttons after start
    await menu(update, context)

# ================================= Menu and it's button handler ================================
async def menu(update, context):
    keyboard = [
        [InlineKeyboardButton("دریافت تکالیف", callback_data='show_hw')],
        [InlineKeyboardButton("ارسال تکالیف", callback_data='send_hw')],
    ]
    r = InlineKeyboardMarkup(keyboard)

    # If called from /start (message)
    if update.message:
        await update.message.reply_text("انتخاب کنید:", reply_markup=r)
    # If called from a callback_query
    elif update.callback_query:
        await update.callback_query.message.reply_text("انتخاب کنید:", reply_markup=r)


async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "show_hw":
        await show_hw(update, context)
    elif query.data == "send_hw":
        await send_hw(update,context)

# ================================= Show Homework To Students ================================
async def show_hw(update, context):
    try:
        with open('homeworks/homework.csv', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            message_lines = [f"تمرین {row['id']} : {row['homework']}" for row in reader]

        message_text = "\n".join(message_lines) or "هیچ تکلیفی موجود نیست."

        # Use callback_query if called from inline button
        if update.callback_query:
            await update.callback_query.message.edit_text(message_text)
        elif update.message:
            await update.message.reply_text(message_text)

    except FileNotFoundError:
        if update.callback_query:
            await update.callback_query.message.edit_text("فایل تکالیف پیدا نشد!")
        else:
            await update.message.reply_text("فایل تکالیف پیدا نشد!")

# =================================== Sending homework to teacher ======================================
async def send_hw(update, context):
    message_text ="""
برای ارسال تمارین خود فایل آن را در ربات بارگزاری کنید. دقت کنید :
1. فرمت فایل باید zip باشد.
2. اسم فایل باید شامل اسم دانشجو و شماره تمرین باشد
"""
    
    if update.callback_query:
            await update.callback_query.message.edit_text(message_text)
    elif update.message:
        await update.message.reply_text(message_text)

async def send_hw_file(update,context):
    document = update.message.document
    file_id = document.file_id
    file_name = document.file_name
    
    os.makedirs("homework_submit", exist_ok=True)
    file = await context.bot.get_file(file_id)
    await file.download_to_drive(f"homework_submit/{file_name}")
    await update.message.reply_text('فایل شما با موفقیت ارسال شد.')

async def wrong_file(update, context):
    await update.message.reply_text(
        """
فرمت فایل مورد نظز اشتباه است. لطفا تکالیف را با فایل zip ارسال کنید.
"""
    )


# ========================== Non-Command Message Handler ===============================
async def reply(update, context):
    await update.message.reply_text("""
لطفاً از این ربات برای ارسال پیام استفاده نکنید.
این ربات تنها جهت مشاهده و ارسال تکالیف است
دقت کنید که فایل تمرین یک فایل فشرده شده zip باشد که اسم آن شامل اسم شما و شماره تمرین باشد
""")


# ========================== Setting menu on the chat area ===============================
async def set_menu(app):
    commands = [
        BotCommand("menu", "نمایش منو"),
        BotCommand("show_hw", "مشاهده تمارین"),
        BotCommand("send_hw", "ارسال تمارین"),
    ]
    await app.bot.set_my_commands(commands)


# ==================================== APP ====================================

# To show `set_menu` buttons in typing area
app = ApplicationBuilder().token(TOKEN).post_init(set_menu).build()

# Command handlers
app.add_handler(CommandHandler("start", start))

# Menu and CallbackQueryHandler for inline keyboard buttons
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CallbackQueryHandler(button_handler))

# Saving Student's files
app.add_handler(MessageHandler(filters.Document.FileExtension("zip") | filters.Document.FileExtension("rar"), send_hw_file)
)

app.add_handler(MessageHandler(filters.Document.ALL, wrong_file))

# Answer user's non command texts
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# Run the bot
app.run_polling()