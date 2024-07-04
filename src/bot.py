import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube, exceptions
from youtube_downloader import download_video, download_playlist, download_channel

BOT_TOKEN = os.getenv('BOT_TOKEN')
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Hi! Send me a YouTube link to get started.')


async def choose_download_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    context.user_data['url'] = url
    try:
        if 'playlist' in url:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Downloading Playlist...')
            download_paths = await download_playlist(url, update, context)
            await send_downloaded_files(update, context, download_paths)
        elif 'channel' in url:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Downloading Channel...')
            download_paths = await download_channel(url, update, context)
            await send_downloaded_files(update, context, download_paths)
        else:
            yt = YouTube(url)
            buttons = [
                [InlineKeyboardButton("Video", callback_data='video')],
                [InlineKeyboardButton("Audio", callback_data='audio')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Choose type to download:',
                                           reply_markup=reply_markup)
    except exceptions.VideoUnavailable:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The video is unavailable.")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    choice = query.data
    context.user_data['choice'] = choice

    url = context.user_data['url']
    try:
        yt = YouTube(url)

        if choice == 'video':
            streams = yt.streams.filter(file_extension='mp4').order_by('resolution').desc()
        else:
            streams = yt.streams.filter(only_audio=True).order_by('abr').desc()

        buttons = []
        for stream in streams:
            quality = f"{stream.resolution or stream.abr} - {stream.mime_type.split('/')[1]}"
            buttons.append([InlineKeyboardButton(quality, callback_data=str(stream.itag))])

        reply_markup = InlineKeyboardMarkup(buttons)

        # Send an informative message after choosing the type
        type_text = "video" if choice == 'video' else "audio"
        await context.bot.send_message(chat_id=query.message.chat_id,
                                       text=f"You chose {type_text}. Now, select the quality:")

        # Check if the new reply markup differs from the current one
        if query.message.reply_markup != reply_markup:
            await query.edit_message_text('Choose quality:', reply_markup=reply_markup)
    except exceptions.VideoUnavailable:
        await context.bot.send_message(chat_id=query.message.chat_id, text="The video is unavailable.")
    except Exception as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"Error: {e}")


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    itag = int(query.data)
    url = context.user_data['url']
    choice = context.user_data['choice']

    try:
        download_path = await download_video(url, choice, itag, update, context)
        if os.path.getsize(download_path) > MAX_FILE_SIZE:
            await context.bot.send_message(chat_id=query.message.chat_id,
                                           text=f"File is too large to send via Telegram. Please download it from the link below.")
            await context.bot.send_message(chat_id=query.message.chat_id,
                                           text=f"[Download {os.path.basename(download_path)}](file://{os.path.abspath(download_path)})",
                                           parse_mode="Markdown")
        else:
            await send_downloaded_file(query, context, download_path, choice)
    except Exception as e:
        await query.edit_message_text(f"Error: {e}")


async def send_downloaded_files(update: Update, context: ContextTypes.DEFAULT_TYPE, download_paths):
    for download_path in download_paths:
        if os.path.getsize(download_path) > MAX_FILE_SIZE:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"File is too large to send via Telegram. Please download it from the link below.")
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"[Download {os.path.basename(download_path)}](file://{os.path.abspath(download_path)})",
                                           parse_mode="Markdown")
        else:
            with open(download_path, 'rb') as file:
                await context.bot.send_video(chat_id=update.effective_chat.id, video=file)
        os.remove(download_path)  # Delete the file after sending it


async def send_downloaded_file(query, context: ContextTypes.DEFAULT_TYPE, download_path, choice):
    if os.path.getsize(download_path) > MAX_FILE_SIZE:
        await context.bot.send_message(chat_id=query.message.chat_id,
                                       text=f"File is too large to send via Telegram. Please download it from the link below.")
        await context.bot.send_message(chat_id=query.message.chat_id,
                                       text=f"[Download {os.path.basename(download_path)}](file://{os.path.abspath(download_path)})",
                                       parse_mode="Markdown")
    else:
        with open(download_path, 'rb') as file:
            if choice == 'video':
                await context.bot.send_video(chat_id=query.message.chat_id, video=file)
            else:
                await context.bot.send_audio(chat_id=query.message.chat_id, audio=file)
    os.remove(download_path)  # Delete the file after sending it


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, choose_download_type))
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^(video|audio)$'))
    application.add_handler(CallbackQueryHandler(download_handler, pattern='^\d+$'))

    application.run_polling()


if __name__ == '__main__':
    main()
