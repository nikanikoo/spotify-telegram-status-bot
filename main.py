import os
import sys
import json
import time
import requests
from dotenv import load_dotenv, set_key

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
TELEGRAM_MESSAGE_ID = os.getenv('TELEGRAM_MESSAGE_ID')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REFRESH_TOKEN = os.getenv('SPOTIFY_REFRESH_TOKEN')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 5))

# Language Configuration
LANGUAGE = os.getenv('LANGUAGE', 'ru').lower()

# Load Translations from JSON files
TRANSLATIONS = {}
locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
for lang_code in ['ru', 'en']:
    path = os.path.join(locales_dir, f'{lang_code}.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            TRANSLATIONS[lang_code] = json.load(f)
    except Exception as e:
        print(f"Error: Failed to load translation file '{path}': {e}")
        sys.exit(1)

if LANGUAGE not in TRANSLATIONS:
    print(f"Warning: Unsupported LANGUAGE '{LANGUAGE}' specified in .env. Defaulting to 'ru'.")
    LANGUAGE = 'ru'

missing = []
if not TELEGRAM_BOT_TOKEN: missing.append('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_CHANNEL_ID: missing.append('TELEGRAM_CHANNEL_ID')
if not SPOTIFY_CLIENT_ID: missing.append('SPOTIFY_CLIENT_ID')
if not SPOTIFY_CLIENT_SECRET: missing.append('SPOTIFY_CLIENT_SECRET')
if not SPOTIFY_REFRESH_TOKEN: missing.append('SPOTIFY_REFRESH_TOKEN')

if missing:
    print(f"Error: Missing configuration variables in .env: {', '.join(missing)}")
    print("Please make sure all required fields are filled and run auth.py first if needed.")
    sys.exit(1)

class SpotifySession:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.expires_at = 0

    def refresh(self):
        token_url = "https://accounts.spotify.com/api/token"
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        try:
            response = requests.post(
                token_url,
                data=payload,
                auth=(self.client_id, self.client_secret),
                timeout=10
            )
            if response.status_code == 200:
                res_data = response.json()
                self.access_token = res_data.get('access_token')
                self.expires_at = time.time() + res_data.get('expires_in', 3600)
                print("Spotify access token refreshed successfully.")
                return True
            else:
                print(f"Error refreshing Spotify token (HTTP {response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"Exception during Spotify token refresh: {e}")
            return False

    def get_token(self):
        if not self.access_token or time.time() > self.expires_at - 60:
            self.refresh()
        return self.access_token

def format_ms(ms):
    seconds = int(ms / 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def get_progress_bar(progress_ms, duration_ms, length=15):
    if duration_ms <= 0:
        return "─" * length
    percent = progress_ms / duration_ms
    position = int(percent * length)
    if position < 0: position = 0
    if position >= length: position = length - 1
    
    bar = ""
    for i in range(length):
        if i == position:
            bar += "●"
        elif i < position:
            bar += "▬"
        else:
            bar += "─"
    return bar

def get_current_playback(spotify_session):
    token = spotify_session.get_token()
    if not token:
        return None, "auth_error"
        
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 204:
            return None, "inactive"
        elif response.status_code == 200:
            return response.json(), "active"
        elif response.status_code == 401:
            spotify_session.access_token = None
            token = spotify_session.get_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.json(), "active"
                elif response.status_code == 204:
                    return None, "inactive"
            return None, f"error_{response.status_code}"
        else:
            return None, f"error_{response.status_code}"
    except Exception as e:
        return None, f"exception_{str(e)}"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('ok'):
                return res_data['result']['message_id']
        print(f"Failed to send Telegram message (HTTP {response.status_code}): {response.text}")
        return None
    except Exception as e:
        print(f"Exception while sending Telegram message: {e}")
        return None

def edit_telegram_message(message_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        
        res_data = response.json()
        if not res_data.get('ok') and "message is not modified" in res_data.get('description', ''):
            return True
            
        print(f"Failed to edit Telegram message (HTTP {response.status_code}): {response.text}")
        return False
    except Exception as e:
        print(f"Exception while editing Telegram message: {e}")
        return False

def format_playback_message(playback_data, status):
    lang = TRANSLATIONS[LANGUAGE]
    
    if status == "inactive":
        return f"{lang['inactive']}\n\n"
    elif status == "auth_error":
        return lang['auth_error']
    elif status.startswith("error_"):
        err_code = status.split('_')[1]
        return lang['api_error'].format(error_code=err_code)
    elif status.startswith("exception_"):
        err_msg = status.split('_', 1)[1]
        return lang['connection_error'].format(error_msg=err_msg)
        
    if not playback_data or not playback_data.get('item'):
        return lang['inactive']
        
    is_playing = playback_data.get('is_playing', False)
    item = playback_data.get('item')
        
    track_name = item.get('name', lang['unknown_track'])
    artists = ", ".join([artist.get('name', lang['unknown_artist']) for artist in item.get('artists', [])])
    album = item.get('album', {}).get('name', lang['unknown_album'])
    track_url = item.get('external_urls', {}).get('spotify', '#')
    
    progress_ms = playback_data.get('progress_ms', 0)
    duration_ms = item.get('duration_ms', 0)
    
    progress_time = format_ms(progress_ms)
    duration_time = format_ms(duration_ms)
    progress_bar = get_progress_bar(progress_ms, duration_ms)
    
    status_emoji = "▶️" if is_playing else "⏸"
    
    return (
        f"{lang['now_playing']}"
        f"<b>{lang['track']}:</b> <a href=\"{track_url}\">{track_name}</a>\n"
        f"<b>{lang['artist']}:</b> {artists}\n"
        f"<b>{lang['album']}:</b> {album}\n\n"
        f"<code>{status_emoji} {progress_bar} {progress_time} / {duration_time}</code>"
    )

def main():
    global TELEGRAM_MESSAGE_ID
    print("Starting Spotify-to-Telegram status service...")
    
    spotify_session = SpotifySession(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        refresh_token=SPOTIFY_REFRESH_TOKEN
    )
    
    # Initialize message if not set
    if not TELEGRAM_MESSAGE_ID:
        print("TELEGRAM_MESSAGE_ID is not configured. Creating a new status message in the channel...")
        initial_text = TRANSLATIONS[LANGUAGE]['initializing']
        message_id = send_telegram_message(initial_text)
        if message_id:
            TELEGRAM_MESSAGE_ID = str(message_id)
            try:
                set_key(dotenv_path, "TELEGRAM_MESSAGE_ID", TELEGRAM_MESSAGE_ID)
                print(f"Created message successfully. Message ID is: {TELEGRAM_MESSAGE_ID}")
                print("It has been saved to your .env file.")
            except Exception as e:
                print(f"Failed to automatically save message ID to .env: {e}")
                print(f"Please manually add the line: TELEGRAM_MESSAGE_ID={TELEGRAM_MESSAGE_ID}")
        else:
            print("CRITICAL: Failed to create initial message. Check your Bot Token and Channel ID.")
            print("Make sure the bot is an Administrator in the channel with permissions to post messages.")
            sys.exit(1)
            
    print(f"Tracking Spotify playback and updating message ID: {TELEGRAM_MESSAGE_ID}")
    
    last_message = None
    
    while True:
        try:
            playback_data, status = get_current_playback(spotify_session)
            message_text = format_playback_message(playback_data, status)
            
            # Send edit request only if text changed
            if message_text != last_message:
                success = edit_telegram_message(TELEGRAM_MESSAGE_ID, message_text)
                if success:
                    last_message = message_text
                    
        except Exception as e:
            print(f"Error in main loop: {e}")
            
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
