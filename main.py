import os
import discord
from discord.ext import tasks

TOKEN = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@tasks.loop(seconds=7200)  # 2時間（7200秒）おきに実行
async def send_dissoku_up():
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("/dissoku up")
        print("Sent /dissoku up")

@send_dissoku_up.before_loop
async def before_send():
    await client.wait_until_ready()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    if not send_dissoku_up.is_running():
        send_dissoku_up.start()

client.run(TOKEN)