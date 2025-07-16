from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
import requests
from django.core.files.base import ContentFile
from celery import shared_task

from .models import Upload


@shared_task
def process_media_from_url(video_id):
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

