<div align="center">
    <img src="image/IMG_0288.jpeg" width="32%">
    <h1>UserInfo (VAUL3T)</h1>
    <a href="https://www.gnu.org/licenses/gpl-3.0.html">
  <img src="https://img.shields.io/badge/license-GPLv3-blue.svg" alt="License: GPL v3">
</a>
</div>
<br>

UserInfo is a free open-source scraper with easy interface and no confusing bullshit 

Copyright (C) 2025 VAUL3T
VAUL3T@proton.me

VAUL3T is an open source project dedicated to developing OSINT tools. We provide full access to the source code to support bug hunting and to demonstrate our strict zero
knowledge policy.

We guarantee that we do not collect any data that can be linked back to you.

Only in rare cases such as when enabling anti–rate limiting features we may require your Telegram username.

Please note: All our projects are licensed under (GPLv3) 

> [!NOTE]
> We are not responsible for any damange done by this programm or modified versions, 
> We only offer support and guarantee for our ORIGINAL service.

Table of Contents
------------------

1. [Further Documentation](#further-documentation)
2. [How To Use](#how-to-use)
3. [Rate Limit](#rate-limit)
4. [Member Check](#member-check)
5. [Raw Data](#raw-data-function)
6. [Handle Input](#handle-input)
7. [Error System](#error-system)
8. [Info Grabbing](#info-grabbing-function)
9. [What do we offer](#what-user-infos-do-we-offer)
10. [Report Bugs](#reporting-bugs)
11. [Want to help ?](#want-to-help-)
12. [GNU (General public license)](#license)

Further documentation
----------------------
- Website: - 
- Telegram: https://t.me/vaul3t
- GitHub: https://github.com/VAUL3T/TiktokUserInfoBot

How to use
----------------------

* `/start` - Search for a user by username . E.g. `@tiktok`.

* `/id` - Search for user by user ID. E.g. `107955`.


## How is your informaion managed 

As we said we do not collect any data , but if you are being rate limited or request an anti rate limit you are still ram-saved 

| Saved | Time  |
|----------|------|
| rate limit  | `until rate limit is over` |
| anti rate  | `user saved until you request an removal` |
| blacklist | `user saved until you request an removal` |


#### Logs

we have a small debug system that logs things like "/start executed" for debug reasons 

in these logs no data is displayed 

|                               | Displayed ? | Stored ? | How long ? |
|-------------------------------|:-------:|:-----:|:-----:|
| Who you searched              |   🔴    |   🔴   |   -   |  
| When you searched             |   🔴    |   🔴   |   -   | 
| What command                  |   🟢    |   🔴   |   Server Shutdown   | 
| Who you are                   |   🔴    |   🔴   |   -   |    
| Username                      |   🔴    |   🔴   |   -   |     
| User ID                       |   🔴    |   🔴   |   -   |     
| How many searches             |   🔴    |   🔴   |   -   |  
| TimeStamp                     |   🔴    |   🔴   |   -   | 
| Errors                        |   🟢    |   🔴   |   Server Shutdown   |    
| What functions called         |   🟢    |   🔴   |   Server Shutdown   |   

unlike other services we dont log any user data at all 

we dont know who you are searching , who you are and when you searched 

> [!NOTE]
> Logs are only visible until server shutdown , no logfile is created everything is only printed into the console 

## Name and Background 
TikTok user info started as a personal project to help me improve my skills , now it has over 20 daily users and is hosted and managed by VAUL3T 

## Rate Limit

Users that are rate-limited are saved in this variable

```python
rate_limit = {}
```
Depeding on the command/function the user was spamming he is timeouted 
5-30m

/start rate-limiting 
```python
  if elapsed > 300:
            user_data['count'] = 1
            user_data['start_time'] = current_time
        else:
            if user_data['count'] >= 15:
                remaining_time = 1800 - elapsed  #1800 are 30m
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                await update.message.reply_text(
                    f"🚫 Rate limit exceeded. Please wait {minutes}m {seconds}s before using /id again."
                )
                return ConversationHandler.END
            user_data['count'] += 1
```
If less than 5 minutes have passed and the count is already 15 or more, the remaining_time is calculated
```python
remaining_time = 1800 - elapsed
```
/id rate-limiting is exact the same 

before the script checks the rate-limiting it checks if the user is in the anti_rate file 
```python
    exempt = False
    if username:
        exempt = f"@{username.lower()}" in non_rate
```
after that it will check if the user is already rate-limited 
```python
        if user_id not in rate_limit:
            rate_limit[user_id] = {}
        if 'id' not in rate_limit[user_id]:
            rate_limit[user_id]['id'] = {'count': 0, 'start_time': current_time}
```
This code measures how many seconds have passed since the start_time.
```python
  user_data = rate_limit[user_id]['id']
  elapsed = (current_time - user_data['start_time']).total_seconds()
```
## Member Check 

> [!NOTE]
> The bot does not store if you are a member or not ,
> everytime you execute a command ur membership gets checked

as yall know the bot requires to join the channel before you can use it 
and this happens with exactly this lines in every function
```python
user = update.effective_user
user_id = user.id
username = user.username

if not await is_member(user.id, context.bot):
    await prompt_to_join(update)
    return ConversationHandler.END
```

prompt_to_join is the UI where yall had to verify 
```python
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
```
and then the bot checks your membership 
```python
async def is_member(user_id: int, bot) -> bool:
    try:
        print("DEBUG : is_member executed")
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False
```
and if your found as a member you can use the bot 
```python
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
```

## Raw Data function
this function is pretty new and has nothing crazy 
```python
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
```

## Handle input 

here is the handle-input function 
responsible for scraping and displaying the user info

```python
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
```
this is needed so the raw_data is not displayed , this would look pretty ugly 
```python
raw_user = result.pop('_raw_user', None)
```
and this handles the profile picture
```python
  profile_pic = result.pop('Profile Picture', None)
    if profile_pic and profile_pic != 'N/A':
        try:
            await update.message.reply_photo(photo=profile_pic)
        except Exception as e:
            pass
```

## Error system
```python
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
```

## Info grabbing function 
this is not open sorce yet since its ServerSided and not fully implemeted into the bot 
```python
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

    def _load_blacklist(self):
        try:
            with open('blacklist.json', 'r') as f:
                data = json.load(f)
                return {
                    "usernames": set(data.get("usernames", [])),
                    "user_ids": set(data.get("user_ids", []))
                }
        except FileNotFoundError:
            return {"usernames": set(), "user_ids": set()}

        # here it starts calling the server to grab everything
        # it sends all the users in the blacklist data

       
```

after a valid server response the script checks if doxx data exist for the user and converts the timestamps into readable dates 
```python
        username_key = user['uniqueId'].lower()
        if username_key in self.doxx_data:
            print("DEBUG : Doxx data found")
            output["Doxx"] = self.doxx_data[username_key]

        output['_raw_user'] = user
```

```python
    def _convert_timestamp(self, ts):
        if not ts: return 'N/A'
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%d %b %Y %H:%M')
```
if server response invalid or anything else fails we get an error message 
```python
    def _error_response(self):
        return {"error": "🚨 Account not found or unable to fetch data\n\n Make Sure to send user without (@)  \n\n If the error continues contact bot owner @sqzxzp"}
```


## What user infos do we offer 

|                               | Telegram Bot | PyPi (soon) | Website (soon) | Discord Bot (soon) 
|-------------------------------|:-------:|:-----:|:-----:|:-------:|
| Username                      |    ✓    |   ✓   |   ✓   |    ✓    |  
| User ID                       |    ✓    |   ✓   |   ✓   |    ✓    |  
| Display Name                  |    ✓    |   ✓   |   ✓   |    ✓    |  
| Bio                           |    ✓    |   ✓   |   ✓   |    ✓    |  
| Bio Link                      |    ✓    |   ✓   |   ✓   |    ✓    |  
| Country                       |    ✓    |   ✓   |   ✓   |    ✓    |  
| Account Language              |    ✓    |   ✓   |   ✓   |    ✓    |  
| Verified/Private/Secret       |    ✓    |   ✓   |   ✓   |    ✓    |   
| Suggest account bind          |    ✓    |   ✓   |   ✓   |    ✓    |    
| Organisation/Ad/Seller        |    ✓    |   ✓   |   ✓   |    ✓    |  
| AccountCreated/UsernameUpdate |    ✓    |   ✓   |   ✓   |    ✓    |  
| Family Paring                 |    ✓    |   ✓   |   ✓   |    ✓    |  
| Live Status                   |    ✓    |   ✓   |   ✓   |    ✓    |  
| Following Visibillity         |    ✓    |   ✓   |   ✓   |    ✓    | 
| New Account                   |    ✓    |   ✓   |   ✓   |    ✓    | 
| Following/Followers           |    ✓    |   ✓   |   ✓   |    ✓    | 
| Firends                       |    ✓    |   ✓   |   ✓   |    ✓    | 
| Videos/Likes                  |    ✓    |   ✓   |   ✓   |    ✓    | 
| Profile Link                  |    ✓    |   ✓   |   ✓   |    ✓    | 
| Direct Profile Picture        |    ✓    |       |   ✓   |    ✓    | 
| Diff ProfilePic Sizes         |         |   ✓   |       |         | 


## Reporting Bugs  
> Please report Bugs via [`Telegram`](https://t.me/vaul3t) or github issues

## Want to help ?
You can help us by joining our [`Telegram`](https://t.me/vaul3t)

Joining our Bug search programm 

or by just liking this 

# Image 
> 📷 The profile image is used for illustrative purposes only. All rights belong to the original owner.

# License

Copyright (C) 2025  VAUL3T

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

For the full license agreement, see the LICENSE.md file

