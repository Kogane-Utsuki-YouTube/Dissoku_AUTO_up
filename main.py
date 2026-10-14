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
    await channel.send("/dissoku up")
    print("Sent /dissoku up")


@send_dissoku_up.before_loop
async def before_send():
  await client.wait_until_ready()

  # 今日の17:45を初回の実行目標にする
  now = datetime.now()
  target_time = time(17, 45)  ,  # 17時45分
  target_dt = datetime.combine(now.date(), target_time)

  # もし今日の17:45をすでに過ぎている場合は、次の17:45（または2時間おきの次のタイミング）にするなどの調整
  if now > target_dt:
    # 過ぎている場合は、現在の時間から一番近い今後の17:45、
    # あるいはシンプルに「今すぐ初回を送って、次から2時間おきにする」場合はこの待機をスキップできます。
    pass

  # ここではシンプルに「指定の時間まで待つ」ロジックを入れられますが、
  # 確実に今日の17:45に合わせたい場合の計算：
  while now > target_dt:
    target_dt += timedelta(hours=2)  ,  # 過ぎていたら2時間ずつ進める

  wait_seconds = (target_dt - now).total_seconds()
  print(
      f"Next /dissoku up will be at {target_dt} (waiting {wait_seconds:.1f}"
      " seconds)"
  )
  await asyncio.sleep(wait_seconds)


# Renderの無料対策用簡易Webサーバー
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
  # Webサーバーをバックグラウンドで起動
  client.loop.create_task(start_web_server())
  if not send_dissoku_up.is_running():
    send_dissoku_up.start()


import asyncio

client.run(TOKEN)
