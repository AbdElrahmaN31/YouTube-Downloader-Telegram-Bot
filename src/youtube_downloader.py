from pytube import YouTube, Playlist, Channel
import os
import subprocess
import re
from tqdm import tqdm


def sanitize_title(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)


async def download_video(url, choice, itag, update, context):
    yt = YouTube(url)
    video_stream = yt.streams.get_by_itag(itag)
    video_title = sanitize_title(yt.title)

    # Select the corresponding audio stream
    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

    # Download the video stream
    video_path = video_stream.download(filename=f'{video_title}_video.mp4')

    # Download the audio stream
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
    pbar = tqdm(total=100, desc='Merging video and audio')

    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            pbar.update(1)
    pbar.close()

    # Clean up temporary files
    os.remove(video_path)
    os.remove(audio_path)

    return output_path


async def download_playlist(url, update, context):
    playlist = Playlist(url)
    download_paths = []
    for video_url in playlist.video_urls:
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        video_title = sanitize_title(yt.title)

        # Download the video stream
        video_path = video_stream.download(filename=f'{video_title}_video.mp4')

        # Download the audio stream
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
        pbar = tqdm(total=100, desc='Merging video and audio')

        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                pbar.update(1)
        pbar.close()

        # Clean up temporary files
        os.remove(video_path)
        os.remove(audio_path)

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

        # Download the video stream
        video_path = video_stream.download(filename=f'{video_title}_video.mp4')

        # Download the audio stream
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
        pbar = tqdm(total=100, desc='Merging video and audio')

        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                pbar.update(1)
        pbar.close()

        # Clean up temporary files
        os.remove(video_path)
        os.remove(audio_path)

        download_paths.append(output_path)

    return download_paths
