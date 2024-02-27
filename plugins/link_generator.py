from datetime import datetime, timedelta
import requests

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
serializer = Serializer(SECRET_KEY, expires_in=3600)  # Token expires in 1 hour

def generate_token(user_id):
    return serializer.dumps({'user_id': user_id}).decode('utf-8')

def validate_token(token):
    try:
        data = serializer.loads(token)
        return data.get('user_id')
    except:
        return None
import secrets
import string

SECRET_KEY = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(32))


API_KEY = "85d2cf5838d6c742c6a855eb514af076ea5c3790"

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

    # Generate token
    user_id = message.from_user.id
    token = generate_token(user_id)

    if use_api:
        base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
        link = f"https://t.me/{client.username}?start={base64_string}&token={token}"
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
        link = f"https://t.me/{client.username}?start={base64_string}&token={token}"

    # Verify the token using the API
    verify_api_url = f"https://publicearn.com/api/verify?api={API_KEY}&token={token}"
    verify_response = requests.get(verify_api_url)
    verify_response_data = verify_response.json()
    if verify_response_data["status"] != "success":
        await channel_message.reply_text("❌ Error\n\nToken verification failed. Link cannot be accessed.", quote=True)
        return

    # If token verification is successful, send the link to the user
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)
