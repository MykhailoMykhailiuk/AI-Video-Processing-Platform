import os
import tempfile

import yt_dlp
import requests
from django.core.files.base import ContentFile
from celery import shared_task
from moviepy import VideoFileClip

from .models import Upload, Output, OutputType


@shared_task(bind=True)
def process_media_from_url(self, video_id, *args, **kwargs):
    try:
        video = Upload.objects.get(id=video_id)

        if not video.file_url:
            return 

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'noplaylist': True,
            'extract_flat': True,
            'referer': video.file_url,
            'http_headers': {'User-Agent': 'Mozilla/5.0'},
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video.file_url, download=False)

            video.file = info.get('title') or (info.get('description', '')[:100] if info.get('description') else f"video_{video.id}")

            thumbnails = info.get('thumbnail', [])
            thumbnail_url = (
                info.get('thumbnail') or
                (thumbnails[-1]['url'] if thumbnails else None) or
                (info.get('avatar', {}).get('url'))
            )

            if thumbnail_url:
                try:
                    response = requests.get(thumbnail_url, timeout=10)
                    if response.status_code == 200:
                        video.thumbnail.save(
                            f"thumb_{video.id}.jpg",
                            ContentFile(response.content),
                            save=True
                        )
                except Exception as e:
                    print(f"[Thumbnail Download Error] {e}")

            video.save()

    except Exception as e:
        print(f"[Media Processing Error for {video.file_url}] {e}")
        self.retry(exc=e, countdown=60)


@shared_task
def extract_audio_from_file(video_id):
    temp_file = None

    try:
        video = Upload.objects.get(id=video_id)

        if not video.file:
            return
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            with VideoFileClip(video.file.path) as clip:
                clip.audio.write_audiofile(temp_file.name)

            output = Output.objects.create(
                    upload=video,
                    output_type=OutputType.AUDIO
                )

            with open(temp_file.name, 'rb') as audio_file:  
                output.file.save(
                    f"audio_{video.id}.mp3",
                    ContentFile(audio_file.read()),
                )
                output.save()

    except Exception as e:
        print(f"[Media Processing Error for {video.file} {e}")

    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)


@shared_task(bind=True)
def extract_audio_from_url(self, video_id, *args, **kwargs):

    try:
        video = Upload.objects.get(id=video_id)

        if not video.file_url:
            return
        
        output_dir = tempfile.gettempdir()

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, f"audio_{video.id}.%(ext)s"),
            'ffmpeg_location': 'C:/ffmpeg/bin/ffmpeg.exe',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'quiet': True,
        }

        downloaded_file = None

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video.file_url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        if downloaded_file and os.path.exists(downloaded_file):
            output = Output.objects.create(
                    upload=video,
                    output_type=OutputType.AUDIO
                )
        
            with open(downloaded_file, 'rb') as audio_file:  
                output.file.save(
                    f"audio_{video.id}.mp3",
                    ContentFile(audio_file.read()),
                )
                output.save()
            os.remove(downloaded_file)

    except Exception as e:
        print(f"[Media Processing Error for {video.file_url} {e}")
        self.retry(exc=e, countdown=60)