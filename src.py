import requests
import os
import random
import string
import re
import asyncio
import time
import logging
import socks
import socket
from io import BytesIO
from io import StringIO
from uuid import uuid4
import pycountry
import json
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from pycountry import countries, currencies
from telegram.error import BadRequest
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    InputFile
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler
)
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

try:
    with open('non_rate.json', 'r') as f:
        non_rate = json.load(f)
except FileNotFoundError:
    non_rate = []
    with open('non_rate.json', 'w') as f:
        json.dump(non_rate, f)

rate_limit = {}
CHANNEL_ID = "@vaul3t"


class TiktokUserScraper:
    URI_BASE = 'https://www.tiktok.com/'

   
    def _error_response(self):
        print("DEBUG : Account not found")
        return {"error": "🚨 Account not found or unable to fetch data\n\n Make Sure to send user without (@)  \n\n If the error continues contact bot owner @kyslaw"}

TOKEN = "XXXXX-XXXXXX-XXXXXX-XXXXXX"
scraper = TiktokUserScraper()

def get_user_token(user_id):
    try:
        with open("/home/SQX/mysite/TOKEN.json", "r") as f:
            tokens = json.load(f)
        return next((t for t in tokens if t["userID"] == str(user_id)), None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def update_user_token(user_id, new_token):
    try:
        try:
            with open("/home/SQX/mysite/TOKEN.json", "r") as f:
                tokens = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            tokens = []

        tokens = [t for t in tokens if t["userID"] != str(user_id)]

        tokens.append({
            "token": new_token,
            "userID": str(user_id)
        })

        with open("/home/SQX/mysite/TOKEN.json", "w") as f:
            json.dump(tokens, f, indent=2)

        return True
    except Exception as e:
        print(f"Error updating token: {e}")
        return False

async def is_member(user_id: int, bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

async def prompt_to_join(update: Update):
    print("DEBUG : Prompt to join executed")
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
        [InlineKeyboardButton("I've Joined ✅", callback_data="check_join")],
        [InlineKeyboardButton("Issues ?", url=f"https://t.me/@kyslaw")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🚫 To use this bot, you must join our channel!\n\n"
        "👉 Join using the button below, then click 'I've Joined ✅' to verify."
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("DEBUG : Check Join")
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if await is_member(user_id, context.bot):
        try:
            await query.message.delete()
        except BadRequest:
            pass

        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Verification successful! You can now use the bot.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await query.answer("❌ You're still not in the channel! Join and try again.", show_alert=True)

USERNAME, USER_ID = range(2)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("DEBUG : /start executed")
    user = update.effective_user
    user_id = user.id
    username = user.username

    exempt = False
    if username:
        exempt = f"@{username.lower()}" in non_rate

    if not exempt:
        current_time = datetime.now(timezone.utc)

        if user_id not in rate_limit:
            rate_limit[user_id] = {}
        if 'start' not in rate_limit[user_id]:
            rate_limit[user_id]['start'] = {'count': 0, 'start_time': current_time}

        user_data = rate_limit[user_id]['start']
        elapsed = (current_time - user_data['start_time']).total_seconds()

        if elapsed > 300:
            user_data['count'] = 1
            user_data['start_time'] = current_time
        else:
            if user_data['count'] >= 15:
                remaining_time = 1800 - elapsed
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                print("DEBUG : Rate-Limit ")
                await update.message.reply_text(
                    f"🚫 Rate limit exceeded. Please wait {minutes}m {seconds}s before using /start again."
                )
                return ConversationHandler.END
            user_data['count'] += 1

    if not await is_member(user.id, context.bot):
        await prompt_to_join(update)
        return ConversationHandler.END

    await update.message.reply_text(
        r"👋 Hi Send me a TikTok username to get account details, "
        r"You can send /cancel at any time to stop",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return USERNAME

async def start_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("DEBUG : /id executed")
    user = update.effective_user
    user_id = user.id
    username = user.username

    exempt = False
    if username:
        exempt = f"@{username.lower()}" in non_rate

    if not exempt:
        current_time = datetime.now(timezone.utc)

        if user_id not in rate_limit:
            rate_limit[user_id] = {}
        if 'id' not in rate_limit[user_id]:
            rate_limit[user_id]['id'] = {'count': 0, 'start_time': current_time}

        user_data = rate_limit[user_id]['id']
        elapsed = (current_time - user_data['start_time']).total_seconds()

        if elapsed > 300:
            user_data['count'] = 1
            user_data['start_time'] = current_time
        else:
            if user_data['count'] >= 15:
                remaining_time = 1800 - elapsed
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                print("DEBUG : Rate-Limit ")
                await update.message.reply_text(
                    f"🚫 Rate limit exceeded. Please wait {minutes}m {seconds}s before using /id again."
                )
                return ConversationHandler.END
            user_data['count'] += 1

    if not await is_member(user.id, context.bot):
        await prompt_to_join(update)
        return ConversationHandler.END

    await update.message.reply_text(
        r"👋 Hi Send me a TikTok user ID to get account details, "
        r"You can send /cancel at any time to stop",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return USER_ID

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    if not await is_member(user.id, context.bot):
        await prompt_to_join(update)
        return ConversationHandler.END
    user_input = update.message.text
    result = scraper.get_user_details(user_input)

    if 'error' in result:
        await update.message.reply_text(result['error'])
        return ConversationHandler.END
    profile_pic = result.pop('Profile Picture', None)
    if profile_pic and profile_pic != 'N/A':
        try:
            await update.message.reply_photo(photo=profile_pic)
        except Exception as e:
            pass

    raw_user = result.pop('_raw_user', None)
    response = "📋 *TikTok Account Details*\n\n"
    for key, value in result.items():
        safe_key = escape_markdown(key, version=2)
        safe_value = escape_markdown(str(value), version=2)
        response += f"*{safe_key}*: {safe_value}\n"

    keyboard = [[InlineKeyboardButton("🔄 Refresh Information", callback_data=f"refresh:{user_input}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        response,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('❌ Operation cancelled')
    return ConversationHandler.END

def trigger_token_reload():
    url = "https://sqx.pythonanywhere.com/api/v0/@server/@admin/token/reload_token"
    headers = {"X-API-Key": "XXX-XXX-XXX"}
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        print(f"Token reload triggered - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Token reload failed: {str(e)}")

async def raw_data_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user
    user_id = user.id
    current_time = datetime.now(timezone.utc)
    username = user.username

    if not await is_member(user.id, context.bot):
        await prompt_to_join(update)
        return ConversationHandler.END

    exempt = any(exempt_user.lower() == f"@{username.lower()}" for exempt_user in non_rate) if username else False

    if not exempt:
        if user_id not in rate_limit:
            rate_limit[user_id] = {}
        if 'raw_data' not in rate_limit[user_id]:
            rate_limit[user_id]['raw_data'] = {'count': 0, 'start_time': current_time}

        user_data = rate_limit[user_id]['raw_data']
        elapsed = (current_time - user_data['start_time']).total_seconds()

        if elapsed > 300:
            user_data['count'] = 1
            user_data['start_time'] = current_time
        else:
            if user_data['count'] >= 4:
                remaining_time = 300 - elapsed
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                await query.answer(
                    f"⚠️ Rate Limit. Please wait {minutes}m {seconds}s.",
                    show_alert=True
                )
                return
            user_data['count'] += 1

    await query.answer()
    identifier = query.data.split(':', 1)[1]

    try:
        result = scraper.get_user_details(identifier)
        if 'error' in result:
            await query.message.reply_text(result['error'])
            return

        raw_user_data = result.get('_raw_user')
        if not raw_user_data:
            await query.message.reply_text("❌ Raw user data not available.")
            return

        date_str = datetime.now().strftime("%Y-%m-%d")
        clean_username = result.get('Username', 'unknown').replace('@', '').replace('/', '_')
        filename = f"{date_str}_{clean_username}_raw.json"

        json_data = json.dumps(raw_user_data, indent=2, ensure_ascii=False)
        bio = BytesIO(json_data.encode('utf-8'))
        bio.name = filename
        bio.seek(0)

        await query.message.reply_document(
            document=bio,
            filename=filename
        )

    except Exception as e:
        await query.message.reply_text(f"⚠️ Failed to generate raw data: {str(e)}")

async def api_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("DEBUG : API command executed")
    user = update.effective_user
    existing = get_user_token(user.id)
    user_id = user.id
    current_time = datetime.now(timezone.utc)
    username = user.username

    exempt = False
    if username:
        exempt = f"@{username.lower()}" in non_rate

    if not exempt:
        current_time = datetime.now(timezone.utc)

        if user_id not in rate_limit:
            rate_limit[user_id] = {}
        if 'id' not in rate_limit[user_id]:
            rate_limit[user_id]['id'] = {'count': 0, 'start_time': current_time}

        user_data = rate_limit[user_id]['id']
        elapsed = (current_time - user_data['start_time']).total_seconds()

        if elapsed > 300:
            user_data['count'] = 1
            user_data['start_time'] = current_time
        else:
            if user_data['count'] >= 2:
                remaining_time = 1800 - elapsed
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                print("DEBUG : Rate-Limit ")
                await update.message.reply_text(
                    f"🚫 Rate limit exceeded. Please wait {minutes}m {seconds}s before using /id again."
                )
                return ConversationHandler.END
            user_data['count'] += 1

    if not await is_member(user.id, context.bot):
        await prompt_to_join(update)
        return ConversationHandler.END

    if existing:
        token = existing["token"]
        message = (
            f"You already own a Token\n\n"
            f"`{token}`\n\n"
            "*Do NOT share or publish your token*"
        )
    else:
        new_token = generate_token()
        success = update_user_token(user.id, new_token)
        if not success:
            await update.message.reply_text("⚠️ Failed to generate token. Please try again.")
            return
        token = new_token
        message = (
            "Token Generation successful\n\n"
            f"`{token}`\n\n"
            "*Do NOT share or publish your token*"
        )
        trigger_token_reload()

    keyboard = [
        [
            InlineKeyboardButton("Validate Token", url="https://sqx.pythonanywhere.com/autho"),
            InlineKeyboardButton("Revoke Token", callback_data=f"revoke:{user.id}")
        ]
    ]

    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def revoke_token_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if ':' not in query.data:
        await query.answer("Invalid request data. Please try again.", show_alert=True)
        return

    user_id = query.data.split(":")[1]
    user = update.effective_user
    user_id_q = user.id
    current_time = datetime.now(timezone.utc)
    username = user.username

    if username and f"@{username.lower()}" in ignore:
        print(f"DEBUG : Ignoring user @{username} due to exemption")
        return ConversationHandler.END

    if not await is_member(user.id, context.bot):
        await prompt_to_join(update)
        return ConversationHandler.END

    exempt = any(exempt_user.lower() == f"@{username.lower()}" for exempt_user in non_rate) if username else False

    if not exempt:
        if user_id_q not in rate_limit:
            rate_limit[user_id_q] = {}
        if 'raw_data' not in rate_limit[user_id_q]:
            rate_limit[user_id_q]['raw_data'] = {'count': 0, 'start_time': current_time}

        user_data = rate_limit[user_id_q]['raw_data']
        elapsed = (current_time - user_data['start_time']).total_seconds()

        if elapsed > 300:
            user_data['count'] = 1
            user_data['start_time'] = current_time
        else:
            if user_data['count'] >= 1:
                remaining_time = 300 - elapsed
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                await query.answer(
                    f"⚠️ Rate Limit. Please wait {minutes}m {seconds}s.",
                    show_alert=True
                )
                return
            user_data['count'] += 1

    await query.answer()

    new_token = generate_token()
    success = update_user_token(user_id, new_token)

    if not success:
        await query.edit_message_text("⚠️ Failed to revoke token. Please try again.")
        return

    trigger_token_reload()

    new_message = (
        "Token Revoked & Regenerated\n\n"
        f"`{new_token}`\n\n"
        "*Do NOT share or publish your token*"
    )

    keyboard = [
        [
            InlineKeyboardButton("Validate Token", url="https://sqx.pythonanywhere.com/autho"),
            InlineKeyboardButton("Revoke Token", callback_data=f"revoke:{user_id}")
        ]
    ]

    await query.edit_message_text(
        new_message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("DEBUG : Refresh requested")
    query = update.callback_query
    user_id = query.from_user.id
    current_time = datetime.now(timezone.utc)
    username = query.from_user.username
    user = update.effective_user

    if not await is_member(user.id, context.bot):
        await prompt_to_join(update)
        return ConversationHandler.END

    exempt = any(exempt_user.lower() == f"@{username.lower()}"
               for exempt_user in non_rate) if username else False

    if not exempt:
        user_data = rate_limit.setdefault(user_id, {}).setdefault(
            'refresh', {'count': 0, 'start_time': current_time}
        )

        user_data = rate_limit[user_id]['refresh']
        elapsed = (current_time - user_data['start_time']).total_seconds()

        if elapsed > 300:
            user_data['count'] = 0
            user_data['start_time'] = current_time
        else:
            if user_data['count'] >= 4:
                remaining_time = 300 - elapsed
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                await query.answer(
                    f"⚠️ Rate Limit. Please wait {minutes}m {seconds}s.",
                    show_alert=True
                )
                return
            user_data['count'] += 1

    await query.answer()
    identifier = query.data.split(':', 1)[1]

    try:
        result = scraper.get_user_details(identifier)

        if 'error' in result:
            await query.edit_message_text(text=result['error'])
            return

        raw_user = result.pop('_raw_user', None)
        response = "📋 *TikTok Account Details*\n\n"
        for key, value in result.items():
            if key == 'Profile Picture':
                continue
            safe_key = escape_markdown(key, version=2)
            safe_value = escape_markdown(str(value), version=2)
            response += f"*{safe_key}*: {safe_value}\n"

        keyboard = [
            [InlineKeyboardButton("🔄 Refresh Information", callback_data=f"refresh:{identifier}")],
            [InlineKeyboardButton("📁 Raw Data", callback_data=f"raw_data:{identifier}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await query.edit_message_text(
                text=response,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
        except BadRequest as br:
            if "Message is not modified" in str(br):
                await query.answer("✅ Information is already up to date")

    except Exception as e:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"⚠️ Refresh failed: {str(e)}"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    error_msg = "⚠️ An error occurred while processing your request\n\nIf error continues contact owner"
    print(f"Error found : {context.error}")
    try:
        if update.message:
            await update.message.reply_text(error_msg)
        elif update.callback_query:
            await update.callback_query.message.reply_text(error_msg)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_msg
            )
    except Exception as e:
        print(f"Error handling failed: {str(e)}")

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_error_handler(error_handler)

    application.add_handler(CommandHandler('api', api_command))

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('id', start_id),
        ],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
            USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)

    application.add_handler(CallbackQueryHandler(revoke_token_callback, pattern="^revoke:"))
    application.add_handler(CallbackQueryHandler(refresh_callback, pattern="^refresh:"))
    application.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    application.add_handler(CallbackQueryHandler(raw_data_callback, pattern="^raw_data:"))

    print("DEBUG : Bot running")
    application.run_polling()

if __name__ == '__main__':
    main()
