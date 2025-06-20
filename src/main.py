import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from src.models.domain import db
from src.telegram_bot import TelegramDomainBot
from src.config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return """
    <h1>🤖 Telegram Domain Checker Bot</h1>
    <p><strong>Status:</strong> ✅ Bot is running!</p>
    <p><strong>Bot Name:</strong> Naw4la_bot</p>
    <p><strong>Bot Username:</strong> @Nawalas_bot</p>
    <p><strong>Features:</strong></p>
    <ul>
        <li>✅ Real-time domain blocking status check</li>
        <li>📋 Domain monitoring list management</li>
        <li>🔄 Automatic updates every 30 minutes</li>
        <li>🚨 Status change notifications</li>
        <li>🟢 Green status for unblocked domains</li>
        <li>🔴 Red status for blocked domains</li>
    </ul>
    <p><strong>Commands:</strong></p>
    <ul>
        <li>/start - Start using the bot</li>
        <li>/help - Show help</li>
        <li>/add &lt;domain&gt; - Add domain to monitoring</li>
        <li>/list - Show monitored domains</li>
        <li>/remove &lt;domain&gt; - Remove domain from monitoring</li>
        <li>/check &lt;domain&gt; - Check domain status manually</li>
    </ul>
    <p><strong>API Used:</strong> <a href="https://check.skiddle.id/" target="_blank">Skiddle-ID Domain Checker</a></p>
    """

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Bot is running', 'bot': '@Nawalas_bot'}

if __name__ == '__main__':
    try:
        # Validate configuration
        Config.validate()
        
        # Get bot token from config
        bot_token = Config.TELEGRAM_BOT_TOKEN
        
        # Create and start the bot
        bot = TelegramDomainBot(bot_token, app.app_context)
        
        # Start Flask app in a separate thread for health checks
        import threading
        flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False), daemon=True)
        flask_thread.start()
        
        # Start the bot (this will block)
        bot.start_bot()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please set your TELEGRAM_BOT_TOKEN environment variable or create .env file")
        print("Example: export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

