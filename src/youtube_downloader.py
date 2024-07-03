from pytube import YouTube, Playlist, Channel
import os
import subprocess
import re
import time


def sanitize_title(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)


async def download_video(url, choice, itag, update, context):
    yt = YouTube(url)
    video_stream = yt.streams.get_by_itag(itag)
    video_title = sanitize_title(yt.title)

    # Select the corresponding audio stream
    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

    # Update the user about the start of the download
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Downloading {video_title}...")

    last_percentage = 0

    def progress_callback(stream, chunk, bytes_remaining):
        nonlocal last_percentage
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = bytes_downloaded / total_size * 100
        if int(percentage) > last_percentage:
            last_percentage = int(percentage)
            text = f"Downloading {video_title}... {percentage:.2f}%"
            context.application.create_task(
                context.bot.edit_message_text(text=text, chat_id=message.chat_id, message_id=message.message_id))

    yt.register_on_progress_callback(progress_callback)
    video_path = video_stream.download(filename=f'{video_title}_video.mp4')
    audio_path = audio_stream.download(filename=f'{video_title}_audio.mp4')

    # Merge video and audio using ffmpeg
    output_path = f'{video_title}.mp4'
    command = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_path
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    merge_message = None
    while process.poll() is None:
        time.sleep(1)
        if not merge_message or merge_message != f"Merging video and audio... {video_title}":
            merge_message = f"Merging video and audio... {video_title}"
            await context.bot.edit_message_text(text=merge_message, chat_id=message.chat_id,
                                                message_id=message.message_id)

    # Clean up temporary files
    os.remove(video_path)
    os.remove(audio_path)

    await context.bot.edit_message_text(text=f"Downloaded {video_title}!", chat_id=message.chat_id,
                                        message_id=message.message_id)
    return output_path


async def download_playlist(url, update, context):
    playlist = Playlist(url)
    download_paths = []
    for video_url in playlist.video_urls:
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        video_title = sanitize_title(yt.title)

        message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Downloading {video_title}...")

        last_percentage = 0

        def progress_callback(stream, chunk, bytes_remaining):
            nonlocal last_percentage
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage = bytes_downloaded / total_size * 100
            if int(percentage) > last_percentage:
                last_percentage = int(percentage)
                text = f"Downloading {video_title}... {percentage:.2f}%"
                context.application.create_task(
                    context.bot.edit_message_text(text=text, chat_id=message.chat_id, message_id=message.message_id))

        yt.register_on_progress_callback(progress_callback)
        video_path = video_stream.download(filename=f'{video_title}_video.mp4')
        audio_path = audio_stream.download(filename=f'{video_title}_audio.mp4')

        output_path = f'{video_title}.mp4'
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_path
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        merge_message = None
        while process.poll() is None:
            time.sleep(1)
            if not merge_message or merge_message != f"Merging video and audio... {video_title}":
                merge_message = f"Merging video and audio... {video_title}"
                await context.bot.edit_message_text(text=merge_message, chat_id=message.chat_id,
                                                    message_id=message.message_id)

        os.remove(video_path)
        os.remove(audio_path)

        await context.bot.edit_message_text(text=f"Downloaded {video_title}!", chat_id=message.chat_id,
                                            message_id=message.message_id)
        download_paths.append(output_path)

    return download_paths


async def download_channel(url, update, context):
    channel = Channel(url)
    download_paths = []
    for video_url in channel.video_urls:
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        video_title = sanitize_title(yt.title)

        message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Downloading {video_title}...")

        last_percentage = 0

        def progress_callback(stream, chunk, bytes_remaining):
            nonlocal last_percentage
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage = bytes_downloaded / total_size * 100
            if int(percentage) > last_percentage:
                last_percentage = int(percentage)
                text = f"Downloading {video_title}... {percentage:.2f}%"
                context.application.create_task(
                    context.bot.edit_message_text(text=text, chat_id=message.chat_id, message_id=message.message_id))

        yt.register_on_progress_callback(progress_callback)
        video_path = video_stream.download(filename=f'{video_title}_video.mp4')
        audio_path = audio_stream.download(filename=f'{video_title}_audio.mp4')

        output_path = f'{video_title}.mp4'
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_path
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        merge_message = None
        while process.poll() is None:
            time.sleep(1)
            if not merge_message or merge_message != f"Merging video and audio... {video_title}":
                merge_message = f"Merging video and audio... {video_title}"
                await context.bot.edit_message_text(text=merge_message, chat_id=message.chat_id,
                                                    message_id=message.message_id)

        os.remove(video_path)
        os.remove(audio_path)

        await context.bot.edit_message_text(text=f"Downloaded {video_title}!", chat_id=message.chat_id,
                                            message_id=message.message_id)
        download_paths.append(output_path)

    return download_paths
