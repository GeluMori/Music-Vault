import yt_dlp
import os

yt_dlp.utils.std_headers['User-Agent'] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

def download_audio(url, output_path, filename):
    #Prep: Create Folder
    os.makedirs(output_path, exist_ok=True)
    #Prep: yt_dlp config
    ydl_opts = {
        'format': 'bestaudio/best[ext=webm]/bestaudio/best',
        'outtmpl': os.path.join(output_path, filename),
        
        # Silence warnings & progress spam
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'ignoreerrors': True,

        # Force YouTube to behave properly
        'extractor_args': {
            'youtube': {
                'player_client': ['web'],  # Prevents SABR streaming issues
                'skip': [
                    'web_safari',
                    'web_safari_music',
                    'web_embedded'
                ]
            }
        },

        # Convert downloaded audio to MP3 via ffmpeg
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    #Drive: Download
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=TTDC92sKcoc"
    download_audio(test_url, "./test_music", "test_song.mp3")