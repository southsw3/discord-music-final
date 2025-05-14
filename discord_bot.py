import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv  # .env 파일을 읽기 위해 필요

# .env 파일에서 환경변수 로드
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 봇 로그인 완료: {bot.user}")

# 음성 채널 접속
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("✅ 음성 채널에 접속했어요!")
    else:
        await ctx.send("❌ 먼저 음성 채널에 접속해주세요.")

# 노래 재생
@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.invoke(bot.get_command('join'))

    voice = ctx.voice_client

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_options)
    voice.stop()
    voice.play(source, after=lambda e: print(f"재생 종료: {e}"))

    await ctx.send(f"🎶 재생 중: **{info['title']}**")

# 노래 중지
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ 재생 중지했어요.")
    else:
        await ctx.send("❌ 현재 재생 중인 음악이 없어요.")

# 음성 채널 퇴장
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 음성 채널에서 나갔어요.")
    else:
        await ctx.send("❌ 음성 채널에 연결되어 있지 않아요.")

# ✅ 봇 실행
bot.run(TOKEN)
