# This version asks for the Artist, Track, And the Album (optional).

import aiohttp
import hashlib
import time
import asyncio
import os
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
        "format": "json"
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
    print("Please authorize this app by visiting:")
    print(f"https://www.last.fm/api/auth/?api_key={API_KEY}&token={token}\n")
    input("Press ENTER after you have authorized... ")
    session_key = await get_session(token)
    with open(SESSION_FILE, "w") as f:
        f.write(session_key)
    print("Session key saved to", SESSION_FILE)
    return session_key

async def scrobble(session_key: str, artist: str, track: str, timestamp: int, album: str = None):
    params = {
        "method": "track.scrobble",
        "api_key": API_KEY,
        "sk": session_key,
        "artist": artist,
        "track": track,
        "timestamp": str(timestamp),
        "format": "json"
    }
    if album:
        params["album"] = album
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

    count = int(input("How many times do you want to scrobble? "))
    artist = input("Artist: ")
    track = input("Track: ")
    album = input("Album (optional): ") or None

    print(f"Scrobbling '{track}' by {artist} {count} times...")

    for i in range(count):
        timestamp = int(time.time()) - (count - i) * 60
        response = await scrobble(session_key, artist, track, timestamp, album)
        print(f"Scrobble {i+1}/{count} → {response}")
        await asyncio.sleep(0.1)

asyncio.run(main())