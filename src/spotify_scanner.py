import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="4c19f178e9754337bdd96da2914226f1",
        client_secret="53c97e2fc4ce42208af6996edd80acb1",
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="user-library-read"
    )
)
def get_saved_tracks(sp, limit=50):
    print("Pulling songs from Spotify...")

    results = []
    offset = 0

    while True:
        response = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = response.get("items", [])
        
        if not items:
            break

        for item in items:
            track = item["track"]
            artist = track["artists"][0]["name"]
            title = track["name"]
            results.append((artist, title))

        offset += limit
        print(f"📥 Pulled {len(results)} songs so far...")

    print(f"Total songs pulled: {len(results)}")
    return results

if __name__ == "__main__":
    #Test printing
    for t in get_saved_tracks():
        print(t)