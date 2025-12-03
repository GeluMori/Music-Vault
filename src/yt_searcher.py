import yt_dlp

def search_youtube(name, artist):
    query = f"ytsearch3:{artist} {name}"

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'ignoreerrors': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['web'],
                'skip': ['web_safari', 'web_safari_music', 'web_embedded']
            }
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)

    if 'entries' not in info:
        return None

    # Search for the first entry that contains a valid URL
    for entry in info['entries']:
        if entry and entry.get('url'):
            return entry['url']

    return None

if __name__ == "__main__":
    print(search_youtube("Artemas good girl"))
