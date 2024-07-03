module.exports = {
    apps: [
        {
            name: 'youtube-telegram-bot',
            script: 'src/bot.py',
            interpreter: 'python3',
            env: {
                BOT_TOKEN: 'YOUR_TELEGRAM_BOT_TOKEN',
            },
        },
    ],
};
