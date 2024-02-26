from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

API_KEY = "your_publicearn_api_key_here"

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    now = datetime.now()
    last_api_call = client.get_last_api_call()
    if last_api_call is None or now - last_api_call > timedelta(hours=24):
        use_api = True
        client.set_last_api_call(now)
    else:
        use_api = False

    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return

        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel",
                                         quote=True)
            continue

    if use_api:
        base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        alias = "CustomAlias"
        format_type = "text"
        api_url = f"https://publicearn.com/api?api={API_KEY}&url={link}&alias={alias}&format={format_type}"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "success":
            link = data["shortenedUrl"]
    else:
        base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)
