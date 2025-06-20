#!/bin/bash

# Telegram Domain Checker Bot Setup Script

echo "🤖 Setting up Telegram Domain Checker Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run this script from the project directory."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if TELEGRAM_BOT_TOKEN is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN environment variable is not set!"
    echo ""
    echo "To get a bot token:"
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send /newbot command"
    echo "3. Follow the instructions to create your bot"
    echo "4. Copy the token and set it as environment variable:"
    echo ""
    echo "   export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Bot token found!"
echo "🚀 Starting Telegram Domain Checker Bot..."

# Run the bot
python src/main.py

