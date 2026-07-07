import os
import sys
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv, set_key

# Load existing environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')

if not CLIENT_ID or not CLIENT_SECRET:
    print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in your .env file.")
    print("Please fill them in before running this authorization script.")
    sys.exit(1)

# Parse Redirect URI
try:
    parsed_redirect = urllib.parse.urlparse(REDIRECT_URI)
    PORT = parsed_redirect.port or 8888
    HOST = parsed_redirect.hostname or 'localhost'
    PATH = parsed_redirect.path or '/callback'
except Exception as e:
    print(f"Error parsing SPOTIFY_REDIRECT_URI: {e}")
    sys.exit(1)

# Spotify authorization settings
# We need scopes: user-read-currently-playing and user-read-playback-state
SCOPES = "user-read-currently-playing user-read-playback-state"

auth_code = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Check if this matches the redirect URI path
        if parsed_path.path == PATH:
            query = urllib.parse.parse_qs(parsed_path.query)
            if 'code' in query:
                auth_code = query['code'][0]
                
                # Respond with a successful page
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                success_html = """
                <html>
                <head>
                    <title>Spotify Auth Successful</title>
                    <style>
                        body {
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                            background-color: #121212;
                            color: #ffffff;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            height: 100vh;
                            margin: 0;
                        }
                        .container {
                            text-align: center;
                            background-color: #181818;
                            padding: 40px;
                            border-radius: 12px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                            border: 1px solid #282828;
                        }
                        h1 { color: #1DB954; font-size: 28px; margin-bottom: 10px; }
                        p { font-size: 16px; color: #b3b3b3; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Authorization Successful!</h1>
                        <p>Spotify has been authorized. You can close this window now.</p>
                        <p>Check the console/terminal window for details.</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode('utf-8'))
            else:
                error_msg = query.get('error', ['Unknown error'])[0]
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                error_html = f"""
                <html>
                <body style="background-color: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 50px;">
                    <h1 style="color: #ff3333;">Authorization Failed</h1>
                    <p>Error: {error_msg}</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode('utf-8'))
        else:
            # Not found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    # Mute log messages in console to keep it clean
    def log_message(self, format, *args):
        pass

def run_server():
    # Allow binding to '' which stands for INADDR_ANY, or local interface HOST
    # We will use host parsed from REDIRECT_URI
    server = HTTPServer((HOST, PORT), OAuthCallbackHandler)
    server.timeout = 120 # 2 minutes timeout
    
    # Construct Spotify Auth URL
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'show_dialog': 'true'
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    
    print("\n-------------------------------------------------------")
    print("Spotify Authorization Helper")
    print("-------------------------------------------------------")
    print("Opening your browser to authorize the app...")
    print(f"If the page doesn't open automatically, visit this link:\n{auth_url}\n")
    
    webbrowser.open(auth_url)
    
    # Handle exactly one request
    server.handle_request()
    server.server_close()

def main():
    run_server()
    
    if not auth_code:
        print("Error: Authentication timed out or was cancelled by user.")
        sys.exit(1)
        
    print("Received authorization code. Requesting tokens...")
    
    # Request Refresh Token
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI
    }
    
    # Spotify requires standard basic auth headers using client ID and secret
    response = requests.post(
        token_url,
        data=payload,
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    
    if response.status_code != 200:
        print(f"Error requesting token (HTTP {response.status_code}):")
        print(response.text)
        sys.exit(1)
        
    res_data = response.json()
    refresh_token = res_data.get('refresh_token')
    
    if not refresh_token:
        print("Error: Could not retrieve refresh token from response.")
        print(res_data)
        sys.exit(1)
        
    # Save refresh token back to .env
    try:
        set_key(dotenv_path, "SPOTIFY_REFRESH_TOKEN", refresh_token)
        print("\nSuccess!")
        print("-------------------------------------------------------")
        print("Your Spotify Refresh Token has been retrieved and saved to .env")
        print(f"Saved token prefix: {refresh_token[:10]}...")
        print("-------------------------------------------------------")
    except Exception as e:
        print(f"\nAuthorization succeeded, but failed to save token to .env: {e}")
        print(f"Please manually add this line to your .env file:\n")
        print(f"SPOTIFY_REFRESH_TOKEN={refresh_token}")
        print("-------------------------------------------------------")

if __name__ == "__main__":
    main()
