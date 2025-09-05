# This version only asks for the Artist, it randomizes tracks by 50.

import aiohttp
import hashlib
import time
import asyncio
import os
import random
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
LASTFM_API = "https://ws.audioscrobbler.com/2.0/"
SESSION_FILE = "lastfm_session.txt"


def generate_api_sig(params: dict) -> str:
    sig_str = ""
    for k in sorted(params.keys()):
        if k in ["format", "callback"]:
            continue
        sig_str += f"{k}{params[k]}"
    sig_str += API_SECRET
    return hashlib.md5(sig_str.encode("utf-8")).hexdigest()


async def get_token():
    params = {"method": "auth.getToken", "api_key": API_KEY, "format": "json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(LASTFM_API, params=params) as resp:
            return (await resp.json())["token"]


async def get_session(token: str):
    params = {
        "method": "auth.getSession",
        "api_key": API_KEY,
        "token": token,
        "format": "json",
    }
    params["api_sig"] = generate_api_sig(params)
    async with aiohttp.ClientSession() as session:
        async with session.get(LASTFM_API, params=params) as resp:
            data = await resp.json()
            if "session" not in data:
                raise Exception(f"Failed to get session. Response: {data}")
            return data["session"]["key"]


async def auth_flow():
    token = await get_token()
    print("\nPlease authorize this app by visiting:")
    print(f"https://www.last.fm/api/auth/?api_key={API_KEY}&token={token}\n")
    input("Press ENTER after you have authorized... ")
    session_key = await get_session(token)
    with open(SESSION_FILE, "w") as f:
        f.write(session_key)
    print("Session key saved to", SESSION_FILE)
    return session_key


async def get_top_tracks(artist: str, limit: int = 20):
    params = {
        "method": "artist.getTopTracks",
        "artist": artist,
        "api_key": API_KEY,
        "format": "json",
        "autocorrect": "1",
        "limit": str(min(limit, 1000)),
    }

    print(f"\nFetching top tracks for artist: {artist}")
    print(
        f"API Request: {LASTFM_API}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(LASTFM_API, params=params) as resp:
                data = await resp.json()

                if "error" in data:
                    print(
                        f"Last.fm API Error ({data.get('error')}): {data.get('message')}"
                    )
                    return []

                if "toptracks" not in data or "track" not in data["toptracks"]:
                    print(
                        "Unexpected API response format. Could not find 'toptracks.track' in response."
                    )
                    return []

                tracks = [t["name"] for t in data["toptracks"]["track"]]
                print(f"Found {len(tracks)} tracks for artist: {artist}")
                return tracks

    except Exception as e:
        print(f"Error fetching top tracks: {str(e)}")
        return []


async def scrobble(session_key: str, artist: str, track: str, timestamp: int):
    params = {
        "method": "track.scrobble",
        "api_key": API_KEY,
        "sk": session_key,
        "artist": artist,
        "track": track,
        "timestamp": str(timestamp),
        "format": "json",
    }
    params["api_sig"] = generate_api_sig(params)

    async with aiohttp.ClientSession() as session:
        async with session.post(LASTFM_API, data=params) as resp:
            return await resp.json()


async def main():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_key = f.read().strip()
        print("Loaded saved session key.")
    else:
        session_key = await auth_flow()

    artist = input("Artist: ")
    count = int(input("How many scrobbles? "))

    top_tracks = await get_top_tracks(artist, limit=50)
    if not top_tracks:
        print("Could not find top tracks for that artist.")
        return

    print(f"Found {len(top_tracks)} tracks for {artist}. Scrobbling {count} times...")

    for i in range(count):
        track = random.choice(top_tracks)
        timestamp = int(time.time()) - (count - i) * 60
        response = await scrobble(session_key, artist, track, timestamp)
        print(f"{i+1}/{count}: {artist} - {track}")
        # await asyncio.sleep(0.2) # Un-comment this if you want to slow down the scrobbles, recommended for not getting rate limited as quickly.


asyncio.run(main())

