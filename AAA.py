from datetime import datetime, timedelta
from telegram import BotCommand, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import BadRequest
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("BOT_TOKEN")

BAD_WORDS = ["كحبة","منيوج","كس","طيز","طي ز","اغتصبك","انيجك","كحبه","كواد","گواد","گحبة","گحبه","منيوچ","كص"]

# ---------- الدوال ----------

async def start(update, context):
    await update.message.reply_text("مرحباً, اني امسح اي رسالة بذيئة و اكتم الاعضاء الادبسزية")




async def mute(update, context):
    target_id = None

    # الطريقة الأولى: رد على رسالة
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id

    # الطريقة الثانية: @username
    elif context.args:
        username = context.args[0]
        try:
            chat = await context.bot.get_chat(username)
            target_id = chat.id
        except BadRequest:
            await update.message.reply_text("ما گدرت الگه اليوزر مال هذا العضو")
            return

    # ولا رد ولا يوزرنيم
    if target_id is None:
        await update.message.reply_text("رد على رسالة العضو، أو اكتب /mute @username")
        return

    # تنفيذ الكتم
    try:
        until = datetime.now() + timedelta(minutes=1)
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until
        )
        await update.message.reply_text("تم الكتم لمدة دقيقة")
    except BadRequest as e:
        await update.message.reply_text(f"فشل الكتم: {e}")




async def set_commands(app):
    commands = [
        BotCommand("start", "رسالة ترحيب"),
        BotCommand("mute", "كتم عضو"),
    ]
    await app.bot.set_my_commands(commands)

def contains_bad_word(text):
    words = text.split()
    for word in words:
        if word in BAD_WORDS:
            return True
    return False

async def filter_messages(update, context):
    if update.message.from_user is None:
        return  # رسالة من أدمن مجهول, ما نكدر نتعامل معها

    text = update.message.text
    if contains_bad_word(text):
        try:
            await update.message.delete()

            user_id = update.message.from_user.id
            until = datetime.now() + timedelta(minutes=1)
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until
            )
        except BadRequest as e:
            print(f"فشل الإجراء: {e}")

# ---------- بناء البوت ----------

app = Application.builder().token(TOKEN).post_init(set_commands).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(MessageHandler(filters.TEXT, filter_messages))

app.run_polling()