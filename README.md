# 📱 Telegram Number Info Bot

A powerful Telegram bot that fetches detailed information about any Indian mobile number using an external API.

## ✨ Features

- 🔍 Get detailed information about any 10-digit Indian mobile number
- 📊 Beautiful formatted output with emojis
- 🎯 Simple and user-friendly interface
- ⚡ Fast response with error handling
- 🔒 Secure and reliable

## 🚀 Deployment

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/p86187076-cell/telegram-number-bot.git
cd telegram-number-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your bot token in `bot.py`:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```

4. Run the bot:
```bash
python bot.py
```

## 📝 Configuration

- **BOT_TOKEN**: Your Telegram bot token from BotFather
- **API_URL**: The API endpoint for fetching number information

## 🤖 Bot Commands

- `/start` - Start the bot and see welcome message
- `🔍 Get Info` - Button to initiate number lookup

## 📱 How to Use

1. Start the bot with `/start`
2. Press the "🔍 Get Info" button
3. Send a valid 10-digit Indian mobile number
4. Get detailed information instantly

## 📦 Dependencies

- `pyTelegramBotAPI==4.16.0` - Telegram bot API wrapper
- `requests==2.31.0` - HTTP library for API calls

## ⚠️ Important Notes

- This bot requires a valid Telegram Bot Token
- The API endpoint must be accessible from your network
- Ensure you have Python 3.7+ installed

## 📄 License

MIT License - Feel free to use this project for your own purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to fork and submit pull requests.
