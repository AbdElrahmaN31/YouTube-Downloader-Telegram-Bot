import os

import ntplib
import requests
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtube_downloader import download_video, download_playlist, download_channel, split_video_by_size
from pytube import exceptions, YouTube
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()


def sync_time():
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        ntp_time = response.tx_time

        current_time = time.time()
        if abs(ntp_time - current_time) > 5:  # If time difference is more than 5 seconds
            print("Time difference detected. Syncing time...")
            # Set the system time
            new_time = datetime.fromtimestamp(ntp_time).strftime('%m%d%H%M%Y.%S')
            os.system(f'date {new_time}')
    except Exception as e:
        print(f"Failed to sync time: {e}")


# Sync system time
sync_time()

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Initialize the Pyrogram Client
app = Client("youtube_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to store user sessions
user_sessions = {}


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hi! Send me a YouTube link to get started.")


@app.on_message(filters.text & ~filters.command(["start"]))
async def choose_download_type(client, message):
    url = message.text  # The URL sent by the user
    chat_id = message.chat.id
    user_sessions[chat_id] = url  # Store the URL in the user session

    try:
        if 'playlist' in url:
            await message.reply("Downloading Playlist...")
            download_paths = await download_playlist(client, message.chat.id, url)
            await send_downloaded_files(client, message.chat.id, download_paths)
        elif 'channel' in url:
            await message.reply("Downloading Channel...")
            download_paths = await download_channel(client, message.chat.id, url)
            await send_downloaded_files(client, message.chat.id, download_paths)
        else:
            yt = YouTube(url)
            buttons = [
                [InlineKeyboardButton("Video", callback_data='video')],
                [InlineKeyboardButton("Audio", callback_data='audio')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply("Choose type to download:", reply_markup=reply_markup)
    except exceptions.VideoUnavailable:
        await message.reply("The video is unavailable.")
    except Exception as e:
        await message.reply(f"Error: {e}")


@app.on_callback_query(filters.regex("^(video|audio)$"))
async def button_handler(client, callback_query):
    choice = callback_query.data
    chat_id = callback_query.message.chat.id

    url = user_sessions.get(chat_id)
    if url:
        try:
            yt = YouTube(url)
            if choice == 'video':
                streams = yt.streams.filter(file_extension='mp4').order_by('resolution').desc()
            else:
                streams = yt.streams.filter(only_audio=True).order_by('abr').desc()

            buttons = []
            for stream in streams:
                quality = f"{stream.resolution or stream.abr} - {stream.mime_type.split('/')[1]}"
                buttons.append([InlineKeyboardButton(quality, callback_data=f"{choice}_{stream.itag}")])

            reply_markup = InlineKeyboardMarkup(buttons)

            # Send an informative message after choosing the type
            type_text = "video" if choice == 'video' else "audio"
            await client.edit_message_text(chat_id, callback_query.message.id,
                                           f"You chose {type_text}. Now, select the quality:",
                                           reply_markup=reply_markup)
        except exceptions.VideoUnavailable:
            await client.edit_message_text(chat_id, callback_query.message.id, "The video is unavailable.")
        except Exception as e:
            await client.edit_message_text(chat_id, callback_query.message.id, f"Error: {e}")
    else:
        await client.edit_message_text(chat_id, callback_query.message.id, "Error: Original message not found.")


@app.on_callback_query(filters.regex("^(video|audio)_\d+$"))
async def download_handler(client, callback_query):
    data = callback_query.data.split('_')
    choice = data[0]
    itag = int(data[1])
    chat_id = callback_query.message.chat.id

    url = user_sessions.get(chat_id)
    if url:
        try:
            download_path = await download_video(client, chat_id, url, choice, itag)
            if os.path.getsize(download_path) > MAX_FILE_SIZE:
                # Split the video into parts if it is too large
                split_paths = split_video_by_size(download_path, part_size=MAX_FILE_SIZE - 1024 * 1024)
                await send_downloaded_files(client, chat_id, split_paths)
            else:
                await send_downloaded_file(client, chat_id, download_path, choice)
        except Exception as e:
            await client.edit_message_text(chat_id, callback_query.message.id, f"Error: {e}")
        finally:
            if 'download_path' in locals() and os.path.exists(download_path):
                os.remove(download_path)
    else:
        await client.edit_message_text(chat_id, callback_query.message.id, "Error: Original message not found.")


async def send_downloaded_files(client, chat_id, download_paths):
    for download_path in download_paths:
        try:
            await client.send_video(chat_id, video=download_path)
        finally:
            if os.path.exists(download_path):
                os.remove(download_path)


async def send_downloaded_file(client, chat_id, download_path, choice):
    try:
        if choice == 'video':
            await client.send_video(chat_id, video=download_path)
        else:
            await client.send_audio(chat_id, audio=download_path)
    finally:
        if os.path.exists(download_path):
            os.remove(download_path)


app.run()
