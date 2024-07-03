from pytube import YouTube, Playlist, Channel
import os

async def download_video(url, choice, itag, update, context):
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)

    # Update the user about the start of the download
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Downloading {yt.title}...")

    last_percentage = 0

    def progress_callback(stream, chunk, bytes_remaining):
        nonlocal last_percentage
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = bytes_downloaded / total_size * 100
        if int(percentage) > last_percentage:
            last_percentage = int(percentage)
            text = f"Downloading {yt.title}... {percentage:.2f}%"
            context.application.create_task(context.bot.edit_message_text(text=text, chat_id=message.chat_id, message_id=message.message_id))

    yt.register_on_progress_callback(progress_callback)
    download_path = stream.download()

    # Notify the user about the completion
    await context.bot.edit_message_text(text=f"Downloaded {yt.title}!", chat_id=message.chat_id, message_id=message.message_id)

    return download_path

async def download_playlist(url, update, context):
    playlist = Playlist(url)
    download_paths = []
    for video_url in playlist.video_urls:
        yt = YouTube(video_url)
        stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()

        # Update the user about the start of the download
        message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Downloading {yt.title}...")

        last_percentage = 0

        def progress_callback(stream, chunk, bytes_remaining):
            nonlocal last_percentage
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage = bytes_downloaded / total_size * 100
            if int(percentage) > last_percentage:
                last_percentage = int(percentage)
                text = f"Downloading {yt.title}... {percentage:.2f}%"
                context.application.create_task(context.bot.edit_message_text(text=text, chat_id=message.chat_id, message_id=message.message_id))

        yt.register_on_progress_callback(progress_callback)
        download_path = stream.download()
        download_paths.append(download_path)

        # Notify the user about the completion
        await context.bot.edit_message_text(text=f"Downloaded {yt.title}!", chat_id=message.chat_id, message_id=message.message_id)

    return download_paths

async def download_channel(url, update, context):
    channel = Channel(url)
    download_paths = []
    for video_url in channel.video_urls:
        yt = YouTube(video_url)
        stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()

        # Update the user about the start of the download
        message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Downloading {yt.title}...")

        last_percentage = 0

        def progress_callback(stream, chunk, bytes_remaining):
            nonlocal last_percentage
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage = bytes_downloaded / total_size * 100
            if int(percentage) > last_percentage:
                last_percentage = int(percentage)
                text = f"Downloading {yt.title}... {percentage:.2f}%"
                context.application.create_task(context.bot.edit_message_text(text=text, chat_id=message.chat_id, message_id=message.message_id))

        yt.register_on_progress_callback(progress_callback)
        download_path = stream.download()
        download_paths.append(download_path)

        # Notify the user about the completion
        await context.bot.edit_message_text(text=f"Downloaded {yt.title}!", chat_id=message.chat_id, message_id=message.message_id)

    return download_paths
