import os
import logging
import requests
import schedule
import time
import threading
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from src.models.domain import Domain, db

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramDomainBot:
    def __init__(self, token, app_context):
        self.token = token
        self.app_context = app_context
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("add", self.add_domain))
        self.application.add_handler(CommandHandler("list", self.list_domains))
        self.application.add_handler(CommandHandler("remove", self.remove_domain))
        self.application.add_handler(CommandHandler("check", self.check_domain))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        welcome_text = """
🤖 *Selamat datang di Bot Checker Domain Nawala!*

Bot ini akan membantu Anda memantau status domain yang mungkin diblokir oleh Nawala atau pemerintah Indonesia.

*Fitur utama:*
• ✅ Cek status domain secara real-time
• 📋 Kelola daftar domain yang dipantau
• 🔄 Update otomatis setiap 30 menit
• 🚨 Notifikasi jika status berubah

*Perintah yang tersedia:*
/help - Tampilkan bantuan
/add <domain> - Tambah domain untuk dipantau
/list - Lihat daftar domain yang dipantau
/remove <domain> - Hapus domain dari pantauan
/check <domain> - Cek status domain secara manual

Mulai dengan menambahkan domain menggunakan /add <nama_domain>
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
📖 *Bantuan Bot Checker Domain Nawala*

*Perintah yang tersedia:*

/start - Mulai menggunakan bot
/help - Tampilkan bantuan ini
/add <domain> - Tambah domain untuk dipantau
   Contoh: /add google.com
/list - Lihat semua domain yang dipantau
/remove <domain> - Hapus domain dari pantauan
   Contoh: /remove google.com
/check <domain> - Cek status domain secara manual
   Contoh: /check reddit.com

*Status Domain:*
🟢 *Hijau* - Domain tidak diblokir
🔴 *Merah* - Domain diblokir oleh Nawala/Pemerintah

*Catatan:*
• Bot akan mengecek semua domain setiap 30 menit
• Anda akan mendapat notifikasi jika status berubah
• Maksimal 10 domain per user
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def add_domain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add domain to monitoring list"""
        if not context.args:
            await update.message.reply_text("❌ Mohon masukkan nama domain.\nContoh: /add google.com")
            return

        domain_name = context.args[0].lower().strip()
        user_id = update.effective_user.id
        
        # Validate domain format
        if not self.is_valid_domain(domain_name):
            await update.message.reply_text("❌ Format domain tidak valid. Contoh: google.com")
            return

        with self.app_context():
            # Check if domain already exists for this user
            existing = Domain.query.filter_by(user_id=user_id, domain=domain_name).first()
            if existing:
                await update.message.reply_text(f"⚠️ Domain {domain_name} sudah ada dalam daftar pantauan.")
                return

            # Check user domain limit
            user_domains = Domain.query.filter_by(user_id=user_id).count()
            if user_domains >= 10:
                await update.message.reply_text("❌ Maksimal 10 domain per user. Hapus domain lain terlebih dahulu.")
                return

            # Check domain status
            status = await self.check_domain_status(domain_name)
            
            # Add domain to database
            new_domain = Domain(
                user_id=user_id,
                domain=domain_name,
                status=status['blocked'],
                last_checked=datetime.now()
            )
            db.session.add(new_domain)
            db.session.commit()

            status_emoji = "🔴" if status['blocked'] else "🟢"
            status_text = "DIBLOKIR" if status['blocked'] else "TIDAK DIBLOKIR"
            
            await update.message.reply_text(
                f"✅ Domain {domain_name} berhasil ditambahkan!\n"
                f"Status saat ini: {status_emoji} {status_text}"
            )

    async def list_domains(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all monitored domains for user"""
        user_id = update.effective_user.id
        
        with self.app_context():
            domains = Domain.query.filter_by(user_id=user_id).all()
            
            if not domains:
                await update.message.reply_text("📋 Belum ada domain yang dipantau.\nGunakan /add <domain> untuk menambah domain.")
                return

            message = "📋 *Daftar Domain yang Dipantau:*\n\n"
            for domain in domains:
                status_emoji = "🔴" if domain.status else "🟢"
                status_text = "DIBLOKIR" if domain.status else "TIDAK DIBLOKIR"
                last_check = domain.last_checked.strftime("%d/%m %H:%M") if domain.last_checked else "Belum dicek"
                
                message += f"{status_emoji} *{domain.domain}*\n"
                message += f"   Status: {status_text}\n"
                message += f"   Terakhir dicek: {last_check}\n\n"

            await update.message.reply_text(message, parse_mode='Markdown')

    async def remove_domain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove domain from monitoring list"""
        if not context.args:
            await update.message.reply_text("❌ Mohon masukkan nama domain.\nContoh: /remove google.com")
            return

        domain_name = context.args[0].lower().strip()
        user_id = update.effective_user.id
        
        with self.app_context():
            domain = Domain.query.filter_by(user_id=user_id, domain=domain_name).first()
            
            if not domain:
                await update.message.reply_text(f"❌ Domain {domain_name} tidak ditemukan dalam daftar pantauan.")
                return

            db.session.delete(domain)
            db.session.commit()
            
            await update.message.reply_text(f"✅ Domain {domain_name} berhasil dihapus dari pantauan.")

    async def check_domain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manually check domain status"""
        if not context.args:
            await update.message.reply_text("❌ Mohon masukkan nama domain.\nContoh: /check google.com")
            return

        domain_name = context.args[0].lower().strip()
        
        if not self.is_valid_domain(domain_name):
            await update.message.reply_text("❌ Format domain tidak valid. Contoh: google.com")
            return

        # Send "checking" message
        checking_msg = await update.message.reply_text(f"🔍 Mengecek status domain {domain_name}...")
        
        try:
            status = await self.check_domain_status(domain_name)
            status_emoji = "🔴" if status['blocked'] else "🟢"
            status_text = "DIBLOKIR" if status['blocked'] else "TIDAK DIBLOKIR"
            
            result_text = f"📊 *Hasil Pengecekan Domain*\n\n"
            result_text += f"🌐 Domain: {domain_name}\n"
            result_text += f"📍 Status: {status_emoji} {status_text}\n"
            result_text += f"🕐 Dicek pada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            
            await checking_msg.edit_text(result_text, parse_mode='Markdown')
            
        except Exception as e:
            await checking_msg.edit_text(f"❌ Gagal mengecek domain {domain_name}. Silakan coba lagi.")
            logger.error(f"Error checking domain {domain_name}: {e}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle non-command messages"""
        text = update.message.text.strip()
        
        # Check if it looks like a domain
        if self.is_valid_domain(text):
            keyboard = [
                [
                    InlineKeyboardButton("✅ Tambah ke Pantauan", callback_data=f"add_{text}"),
                    InlineKeyboardButton("🔍 Cek Status", callback_data=f"check_{text}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🌐 Terdeteksi domain: *{text}*\n\nApa yang ingin Anda lakukan?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❓ Saya tidak mengerti pesan Anda.\n"
                "Gunakan /help untuk melihat perintah yang tersedia."
            )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if data.startswith("add_"):
            domain = data[4:]
            context.args = [domain]
            await self.add_domain(update, context)
        elif data.startswith("check_"):
            domain = data[6:]
            context.args = [domain]
            await self.check_domain(update, context)

    async def check_domain_status(self, domain):
        """Check domain status using Skiddle API"""
        try:
            url = f"https://check.skiddle.id/?domain={domain}&json=true"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get(domain, {'blocked': False})
            
        except Exception as e:
            logger.error(f"Error checking domain {domain}: {e}")
            return {'blocked': False}  # Default to not blocked if error

    def is_valid_domain(self, domain):
        """Validate domain format"""
        import re
        # More strict domain validation
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        return re.match(pattern, domain) is not None and len(domain) <= 253

    async def check_all_domains(self):
        """Check all domains in database and send notifications for status changes"""
        with self.app_context():
            domains = Domain.query.all()
            
            for domain in domains:
                try:
                    new_status = await self.check_domain_status(domain.domain)
                    new_blocked = new_status['blocked']
                    
                    # Check if status changed
                    if domain.status != new_blocked:
                        # Send notification to user
                        status_emoji = "🔴" if new_blocked else "🟢"
                        status_text = "DIBLOKIR" if new_blocked else "TIDAK DIBLOKIR"
                        old_status_text = "DIBLOKIR" if domain.status else "TIDAK DIBLOKIR"
                        
                        notification = f"🚨 *Perubahan Status Domain*\n\n"
                        notification += f"🌐 Domain: {domain.domain}\n"
                        notification += f"📍 Status Lama: {old_status_text}\n"
                        notification += f"📍 Status Baru: {status_emoji} {status_text}\n"
                        notification += f"🕐 Dicek pada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                        
                        try:
                            await self.application.bot.send_message(
                                chat_id=domain.user_id,
                                text=notification,
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"Failed to send notification to user {domain.user_id}: {e}")
                    
                    # Update domain status
                    domain.status = new_blocked
                    domain.last_checked = datetime.now()
                    
                except Exception as e:
                    logger.error(f"Error checking domain {domain.domain}: {e}")
            
            db.session.commit()
            logger.info(f"Checked {len(domains)} domains")

    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        import asyncio
        
        def run_check():
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.check_all_domains())
            finally:
                loop.close()
        
        schedule.every(30).minutes.do(run_check)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def start_bot(self):
        """Start the bot"""
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Start the bot
        logger.info("Starting Telegram bot...")
        self.application.run_polling()

