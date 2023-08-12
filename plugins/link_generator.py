import aiohttp
import base64
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot  # Assuming this is properly imported
from config import ADMINS, API_KEY
from helper_func import encode, get_message_id



# Your function to get a shortened link using ClicksFly API
async def get_shortlink(link):
    url = 'https://clicksfly.com/api'
    params = {'api': API_KEY, 'url': link}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, raise_for_status=True) as response:
            data = await response.json()
            return data["shortenedUrl"]

# Your handler function for the "genlink" and "batch" commands
@app.on_message(filters.private & filters.user(ADMINS) & filters.command(['genlink', 'batch']))
async def link_handler(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from the DB Channel (with Quotes)..\n"
                     "or Send the DB Channel Post link",
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
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote=True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"

    try:
        short_link = await get_shortlink(link)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={short_link}')]
        ])
        await channel_message.reply_text(f"<b>Here is your link</b>\n\n{short_link}", quote=True, reply_markup=reply_markup)
    except Exception as e:
        await channel_message.reply(f'Error: {e}', quote=True)


