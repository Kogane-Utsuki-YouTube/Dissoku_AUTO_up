import asyncio
from datetime import datetime, time, timedelta
import os
from aiohttp import web
import discord
from discord.ext import tasks

TOKEN = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@tasks.loop(hours=2)
async def send_dissoku_up():
  channel = client.get_channel(CHANNEL_ID)
  if channel:
    await channel.send("/up")  # コマンドを /up に修正
    print(f"[{datetime.now()}] Sent /up")


@send_dissoku_up.before_loop
async def before_send():
  await client.wait_until_ready()

  now = datetime.now()
  # 初回の目標時刻：本日の 17:45
  target_dt = datetime.combine(now.date(), time(17, 45))

  # 既に17:45を過ぎてしまっている場合は、2時間ずつ進めて次の実行タイミングを求める
  while now > target_dt:
    target_dt += timedelta(hours=2)

  wait_seconds = (target_dt - now).total_seconds()
  print(f"初回実行予定時刻: {target_dt} (あと {wait_seconds:.1f} 秒待機します)")

  # 目標時刻まで待機
  await asyncio.sleep(wait_seconds)


# Renderの無料枠スリープ防止用Webサーバー
async def handle(request):
  return web.Response(text="Bot is running!")


async def start_web_server():
  app = web.Application()
  app.add_routes([web.get("/", handle)])
  runner = web.AppRunner(app)
  await runner.setup()
  port = int(os.environ.get("PORT", 10000))
  site = web.TCPSite(runner, "0.0.0.0", port)
  await site.start()


@client.event
async def on_ready():
  print(f"Logged in as {client.user}")
  client.loop.create_task(start_web_server())
  if not send_dissoku_up.is_running():
    send_dissoku_up.start()


client.run(TOKEN)
