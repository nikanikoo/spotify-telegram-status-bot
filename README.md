<div align="center">
  <h1>Spotify to Telegram Status Bot</h1>
  <p><b>A Python script to broadcast your currently playing Spotify track directly to a Telegram channel message in real-time.</b></p>
  <div>
	  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
	  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-red.svg?style=flat-square"></a>
  </div>
</div>

---

[RU](README_RU.md)

**Spotify to Telegram Status Bot** is a lightweight Python script that broadcasts your current Spotify playback status to a Telegram channel message, updating it dynamically with a progress bar, timing details, and a direct link to the track.

> [!NOTE]
> The bot will automatically publish a status message to your channel upon its first run, capture the Message ID, save it to your configuration, and update it dynamically every few seconds.

## 🚀 Features

- **Real-time updates**: Synchronizes playback progress and tracks state automatically.
- **Dynamic progress bar**: Displays tracks playback position and time tracking.
- **Direct Spotify URLs**: Links track titles to their official Spotify pages.
- **Multi-language support**: Easily switch languages (`en` / `ru`) in `.env`, loaded from separate JSON locale configuration files in `/locales`.

---

## 🛠 Installation & Setup

### Step 1. Telegram Bot Setup
1. Message **@BotFather** in Telegram and create a new bot using `/newbot`.
2. Copy your bot's **API Token**.
3. Create a Telegram channel (or use an existing one) and add the bot as an **Administrator** with **Post Messages** and **Edit Messages** permissions.
4. Copy the channel identifier (e.g. public handle `@my_channel` or channel ID `-1001234567890`).

### Step 2. Spotify Application Configuration
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and log in.
2. Click **Create App** and configure:
   - **App name**: `Telegram Status Bot`
   - **Redirect URIs**: Must add exactly `http://localhost:8888/callback`
3. Save changes, click **Settings**, and retrieve your **Client ID** and **Client Secret**.

### Step 3. Project Configuration
1. Clone the repository or navigate to its directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the `.env.example` template to `.env`:
   ```bash
   # On macOS/Linux/Git Bash:
   cp .env.example .env
   # On Windows PowerShell:
   Copy-Item .env.example .env
   ```
5. Open the `.env` file and populate:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot API token.
   - `TELEGRAM_CHANNEL_ID`: Channel ID or username.
   - `SPOTIFY_CLIENT_ID`: Your Spotify App client ID.
   - `SPOTIFY_CLIENT_SECRET`: Your Spotify App client secret.
   - `LANGUAGE`: Select `ru` (Russian) or `en` (English) locales.

   *Note: Leave `TELEGRAM_MESSAGE_ID` and `SPOTIFY_REFRESH_TOKEN` empty, they will be auto-generated.*

---

## 🔑 Spotify Authorization
Authorize the application to access your playing state by running:
```bash
python auth.py
```
A browser tab will open automatically. Grant permission (click **Authorize**). Once authorization is complete, the `SPOTIFY_REFRESH_TOKEN` will be saved to your `.env` file automatically.

---

## 📈 Running the Bot
Launch the main tracking service:
```bash
python main.py
```
The script will post the initial status message, record the `TELEGRAM_MESSAGE_ID` in your `.env` file, and keep editing the message as you listen to Spotify. 

> [!TIP]
> Pin the status message in your channel for high visibility!

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
