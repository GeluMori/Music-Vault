# =====================================================
# MusicVault — Automated Offline Music Library Tool
# Downloads + Tags + Organizes Spotify Liked Songs
# Multi-threaded YouTube audio extraction
# =====================================================

from pathlib import Path
from spotify_scanner import get_saved_tracks, sp
from yt_searcher import search_youtube
from downloader import download_audio
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def safe_filename(s: str) -> str:
    # Remove illegal characters for Windows filenames + trim spaces
    return re.sub(r'[\\/*?:"<>|]', "", s).strip()

# =====================================================
# Worker: Download audio + Embed Metadata & Album Art
# =====================================================
def download_audio_with_metadata(yt_url, artist, name, artist_dir, file_path):
    try:
        # --- Step 1: Download MP3 from YouTube ---
        download_audio(yt_url, artist_dir, f"{artist} - {name}.mp3")

        # --- Step 2: Fetch metadata from Spotify ---
        query = f"{artist} {name}"
        track_info = sp.search(q=query, limit=1, type="track")

        if track_info["tracks"]["items"]:
            track_data = track_info["tracks"]["items"][0]
            album = track_data["album"]["name"]
            album_art_url = track_data["album"]["images"][0]["url"]

            # --- Download album art ---
            art = requests.get(album_art_url).content

            audio = MP3(file_path)
            if audio.tags is None:
                audio.add_tags()

            # --- Embed ID3 Tags ---
            audio.tags["TIT2"] = TIT2(encoding=3, text=name)     # Title
            audio.tags["TPE1"] = TPE1(encoding=3, text=artist)   # Artist
            audio.tags["TALB"] = TALB(encoding=3, text=album)    # Album

            # --- Album Cover Art ---
            audio.tags["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=art
            )

            audio.save()
            return f"{artist} - {name}"

        else:
            return f"No Spotify metadata: {artist} - {name}"

    except Exception as e:
        return f"Metadata Error: {artist} - {name} | {e}"


# =====================================================
# UI: Ask User Where to Store the Music Library
# =====================================================
def choose_output_location():
    print("\nWhere should MusicVault store files?")
    print("1️⃣  Home folder")
    print("2️⃣  Desktop")
    print("3️⃣  Custom path")
    
    choice = input("\nSelect option (default: 1): ").strip()

    if choice == "2":
        output_path = Path.home() / "Desktop" / "MusicVault"
    elif choice == "3":
        custom_path = input("Enter full folder path: ").strip('"')
        output_path = Path(custom_path)
    else:
        output_path = Path.home() / "MusicVault"

    output_path.mkdir(parents=True, exist_ok=True)
    print(f"\nMusic will be saved to:\n{output_path}")
    return output_path


# =====================================================
# Main Program Execution — Downloader Engine
# =====================================================
def main():
    print("Welcome to MusicVault")

    # Output location selection
    output_path = choose_output_location()

    print("\nFetching your Spotify liked songs...")
    tracks = get_saved_tracks(sp)
    total_songs = len(tracks)
    failed_downloads = []
    print(f"Retrieved {total_songs} songs\n")

    print("Starting 6-thread download queue...\n")
    futures = []

    # --- Thread pool for parallel downloads ---
    with ThreadPoolExecutor(max_workers=6) as executor:
        for i, (artist, name) in enumerate(tracks, start=1):
            safe_artist = safe_filename(artist)
            safe_name = safe_filename(name)

            artist_dir = output_path / safe_artist
            artist_dir.mkdir(parents=True, exist_ok=True)

            file_path = artist_dir / f"{safe_artist} - {safe_name}.mp3"

            # Skip if already downloaded
            if file_path.exists():
                print(f"Already downloaded: {artist} - {name}")
                continue

            # Search YouTube for best match
            yt_url = search_youtube(name, artist)

            if yt_url:
                print(f"[{i}/{total_songs}] Queued: {artist} - {name}")
                futures.append(executor.submit(
                    download_audio_with_metadata,
                    yt_url, artist, name, file_path.parent, file_path
                ))
            else:
                print(f"No YouTube match: {artist} - {name}")
                failed_downloads.append(f"{artist} - {name}")

        # --- Collect results from threads ---
        for future in as_completed(futures):
            print(future.result())

    # ==============================================
    # Summary Report
    # ==============================================
    print("\nDownload Summary")
    print(f"Successfully downloaded: {total_songs - len(failed_downloads)} songs")
    print(f"Failed: {len(failed_downloads)} songs")

    if failed_downloads:
        print("\nThese songs failed:")
        for song in failed_downloads:
            print(f" - {song}")

        # Save failed list for retrying
        log_path = output_path / "failed_downloads.log"
        with open(log_path, "w", encoding="utf-8") as f:
            for song in failed_downloads:
                f.write(song + "\n")

        print(f"\nError log saved → {log_path}")
    else:
        print("All songs downloaded successfully!")


    input("\nPress ENTER to exit...")


if __name__ == "__main__":
    main()