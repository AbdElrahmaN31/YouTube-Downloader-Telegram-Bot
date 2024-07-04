module.exports = {
    apps: [
        {
            name: 'youtube-telegram-bot',
            script: 'src/bot.py',
            interpreter: 'python3',
            env: {
                BOT_TOKEN: 'YOUR_TELEGRAM_BOT_TOKEN',
                API_ID: 'YOUR_TELEGRAM_API_ID',
                API_HASH: 'YOUR_TELEGRAM_API_HASH',
            },
        },
    ],
};
