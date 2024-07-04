import time

from pytube import YouTube, Playlist, Channel
import os
import subprocess
import re
import math


def sanitize_title(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)


async def send_progress_bar(chat_id, message_id, percentage, context):
    bar_length = 20  # Length of the progress bar
    block = int(round(bar_length * percentage / 100))
    progress_bar = "▰" * block + "▱" * (bar_length - block)
    text = f"Downloading: [{progress_bar}] {percentage:.2f}%"
    await context.bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id)


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
        if int(percentage) >= last_percentage + 5:  # Update only if the progress changes by 5%
            last_percentage = int(percentage)
            context.application.create_task(
                send_progress_bar(update.effective_chat.id, message.message_id, percentage, context))

    yt.register_on_progress_callback(progress_callback)
    video_path = video_stream.download(filename=f'{video_title}_video.mp4')
    audio_path = audio_stream.download(filename=f'{video_title}_audio.mp4')

    try:
        # Merge video and audio using ffmpeg
        output_path = f'{video_title}.mp4'
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'libx264',  # Ensure the video codec is H.264
            '-c:a', 'aac',  # Ensure the audio codec is AAC
            '-strict', 'experimental',
            '-movflags', '+faststart',  # Ensure the video is streamable
            output_path
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        merge_percentage = 0
        while process.poll() is None:
            merge_percentage += 1
            if merge_percentage > 100:
                merge_percentage = 100
            await send_progress_bar(update.effective_chat.id, message.message_id, merge_percentage, context)
            time.sleep(1)

        await context.bot.edit_message_text(text=f"Downloaded {video_title}!", chat_id=message.chat_id,
                                            message_id=message.message_id)
        return output_path
    finally:
        # Clean up temporary files
        os.remove(video_path)
        os.remove(audio_path)


def split_video_by_size(file_path, part_size=49 * 1024 * 1024):
    output_files = []
    part_index = 1

    while os.path.getsize(file_path) > part_size:
        output_file = f"{file_path.rsplit('.', 1)[0]}_part{part_index}.mp4"
        command = [
            'ffmpeg',
            '-i', file_path,
            '-c', 'copy',
            '-fs', str(part_size),
            output_file
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_files.append(output_file)
        part_index += 1
        # Remove the processed part to avoid duplication
        file_path = output_file

    output_files.append(file_path)  # Add the last part

    return output_files


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
            if int(percentage) >= last_percentage + 5:  # Update only if the progress changes by 5%
                last_percentage = int(percentage)
                context.application.create_task(
                    send_progress_bar(update.effective_chat.id, message.message_id, percentage, context))

        yt.register_on_progress_callback(progress_callback)
        video_path = video_stream.download(filename=f'{video_title}_video.mp4')
        audio_path = audio_stream.download(filename=f'{video_title}_audio.mp4')

        try:
            output_path = f'{video_title}.mp4'
            command = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'libx264',  # Ensure the video codec is H.264
                '-c:a', 'aac',  # Ensure the audio codec is AAC
                '-strict', 'experimental',
                '-movflags', '+faststart',  # Ensure the video is streamable
                output_path
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            merge_percentage = 0
            while process.poll() is None:
                merge_percentage += 1
                if merge_percentage > 100:
                    merge_percentage = 100
                await send_progress_bar(update.effective_chat.id, message.message_id, merge_percentage, context)
                time.sleep(1)

            await context.bot.edit_message_text(text=f"Downloaded {video_title}!", chat_id=message.chat_id,
                                                message_id=message.message_id)
            download_paths.append(output_path)
        finally:
            os.remove(video_path)
            os.remove(audio_path)

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
            if int(percentage) >= last_percentage + 5:  # Update only if the progress changes by 5%
                last_percentage = int(percentage)
                context.application.create_task(
                    send_progress_bar(update.effective_chat.id, message.message_id, percentage, context))

        yt.register_on_progress_callback(progress_callback)
        video_path = video_stream.download(filename=f'{video_title}_video.mp4')
        audio_path = audio_stream.download(filename=f'{video_title}_audio.mp4')

        try:
            output_path = f'{video_title}.mp4'
            command = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'libx264',  # Ensure the video codec is H.264
                '-c:a', 'aac',  # Ensure the audio codec is AAC
                '-strict', 'experimental',
                '-movflags', '+faststart',  # Ensure the video is streamable
                output_path
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            merge_percentage = 0
            while process.poll() is None:
                merge_percentage += 1
                if merge_percentage > 100:
                    merge_percentage = 100
                await send_progress_bar(update.effective_chat.id, message.message_id, merge_percentage, context)
                time.sleep(1)

            await context.bot.edit_message_text(text=f"Downloaded {video_title}!", chat_id=message.chat_id,
                                                message_id=message.message_id)
            download_paths.append(output_path)
        finally:
            os.remove(video_path)
            os.remove(audio_path)

    return download_paths
