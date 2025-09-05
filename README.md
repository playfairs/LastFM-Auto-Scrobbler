# LastFM Auto Scrobbler

> [!IMPORTANT]
> This tool is NOT made for farming scrobbles, using it as such will get your account, API Key and IP Rate Limited (Speaking from experience 😭), additionally, LastFM's API is not designed for such abuse and it **WILL** slow down or even crash the API, I know this because I crashed the API on 09/03/2025 3:54 PM - 09/03/2025 4:10 PM GMT-5, please don't make the same mistake as I did 😭

## Installation

```bash
git clone https://github.com/playfairs/LastFM-Auto-Scrobbler.git
cd LastFM-Auto-Scrobbler
pip install -r requirements.txt
```

## Usage

```bash
python v1.py
or 
python v2.py
```

## Environment Variables

```bash
API_KEY = "REPLACE WITH YOUR API KEY"
API_SECRET = "REPLACE WITH YOUR API SECRET"
```

Place the environment variables in a file named `example.env` and rename it to `.env`.

## v1.py

This version asks for the Artist, Track, And the Album (optional). (It also returns the response from the API, this is useful incase you want to check if the scrobble was successful or not.)

## v2.py

This version only asks for the Artist, it does tracks and albums randomly.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change, honestly, I don't see any reason to make this tool better considering what it is..

> [!NOTE]
> If for some reason the warning at the top didn't convince you enough to back away, I do not recommend doing this on your primary account, this includes both running it ON your account, but also using the API Key from your primary account, if you want to first test it, I suggest making a new LastFM account and a new LastFM Developer Account, just to be safe.