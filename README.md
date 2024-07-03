# YouTube Telegram Bot

This is a Telegram bot that allows users to download videos, audio, playlists, or channels from YouTube.

## Features

- Download YouTube videos
- Download YouTube audio
- Choose the quality of the download
- Download entire playlists
- Download all videos from a channel
- Receive informative messages throughout the download process

## Requirements

- Python 3.8+
- [Telegram Bot Token](https://core.telegram.org/bots#6-botfather)
- [FFmpeg](https://ffmpeg.org/download.html)
- PM2 (optional, for deployment)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AbdElrahmaN31/youtube-downloader-telegram-bot.git
   cd youtube-downloader-telegram-bot
    ```
   
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
    ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
    ```

## Setting Up the Bot

1. Create a new bot on Telegram by talking to [BotFather](https://core.telegram.org/bots#6-botfather).
2. Follow the instructions to get the bot token.
3. Set the bot token as an environment variable:
   - On Linux or macOS:
     ```bash
     export BOT_TOKEN='YOUR_TELEGRAM_BOT_TOKEN'
     ```
   - On Windows:
     ```bash
     set BOT_TOKEN=your_telegram_bot_token
     ```


## Running the Bot

1. Ensure you have set the environment variable for your bot token as shown above.
2. Run the bot:
   ```bash
   python bot.py
    ```
   
## Running with PM2

1. Ensure you have set the environment variable for your bot token as shown above.
2. Install PM2:
   ```bash
   npm install pm2 -g
    ```
3. Start the bot with PM2:
   ```bash
   pm2 start ecosystem.config.js
    ```
4. Check the status of the bot:
    ```bash
    pm2 status
     ```

## Usage

1. Open Telegram and start a chat with your bot.
2. Send a YouTube link (video, playlist, or channel).
3. Follow the prompts to select the type (video or audio) and quality.
4. The bot will download the content and send it back to you.
   
## Project Structure
    youtube-telegram-bot/
    ├── src/
    │   ├── bot.py
    │   └── youtube_downloader.py
    ├── README.md
    ├── requirements.txt
    └── .gitignore

## Contributing

    Contributions are welcome! Please feel free to submit a Pull Request.

## License
    
        This project is licensed under the MIT License.



