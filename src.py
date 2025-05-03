import requests
import os
import re
import logging
from io import BytesIO
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

    def __init__(self):
        self.doxx_data = self._load_doxx_data()
        self.blacklist = self._load_blacklist()

    def _load_doxx_data(self):
        try:
            with open('doxx.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

        # Connections with server(VPS server)

        username_key = user['uniqueId'].lower()
        if username_key in self.doxx_data:
            print("DEBUG : Doxx data found")
            output["Doxx"] = self.doxx_data[username_key]

        output['_raw_user'] = user
        print("DEBUG : user info grabbing completed")

        return output

    def _convert_timestamp(self, ts):
        if not ts: return 'N/A'
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%d %b %Y %H:%M')

    def _error_response(self):
        return {"error": "🚨 Account not found or unable to fetch data\n\n Make Sure to send user without (@)  \n\n If the error continues contact bot owner @sqzxzp"}

TOKEN = "XXX-XXX-XXX-XX-XXX-XXX-XXX-XXX"
scraper = TiktokUserScraper()

async def is_member(user_id: int, bot) -> bool:
    try:
        print("DEBUG : is_member executed")
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

async def prompt_to_join(update: Update):
    print("DEBUG : prompt_to_join executed")
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
        [InlineKeyboardButton("I've Joined ✅", callback_data="check_join")],
        [InlineKeyboardButton("Issues ?", url=f"https://t.me/@sqzxzp")]
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
    print("DEBUG : check_join executed")
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
    print("DEBUG : /cancel executed")
    await update.message.reply_text('❌ Operation cancelled')
    return ConversationHandler.END

async def raw_data_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("DEBUG : raw-data requested")
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
            print("DEBUG : no raw data avaiable")
            return

        print("DEBUG : gen json file")
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
        print("DEBUG : raw data file generation failed")
        await query.message.reply_text(f"⚠️ Failed to generate raw data: {str(e)}")

async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("DEBUG : refresh requested")
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
            [InlineKeyboardButton("📁 Raw Data", callback_data=f"raw_data:{identifier}")]
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
    logging.debug("DEBUG : user ran into an error , please check server logs")
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

    application.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    application.add_handler(CallbackQueryHandler(raw_data_callback, pattern="^raw_data:"))

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

    application.add_handler(CallbackQueryHandler(refresh_callback, pattern="^refresh:"))
    application.run_polling()

if __name__ == '__main__':
    main()
