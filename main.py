import os
import logging
import asyncio
import telebot
from telebot import types
from threading import Thread
from typing import Dict, Optional
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramLinkBot:
    def __init__(self):
        """Initialize the bot with configuration from environment variables."""
        self.api_token = os.getenv('BOT_TOKEN')
        self.admin_id = int(os.getenv('ADMIN_ID', '0'))
        self.auto_delete_delay = int(os.getenv('AUTO_DELETE_DELAY', '15'))
        
        if not self.api_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        self.bot = telebot.TeleBot(self.api_token, parse_mode="HTML")
        self.links = self._load_links()
        self._setup_handlers()
        
        logger.info("Bot initialized successfully")
    
    def _load_links(self) -> Dict[str, str]:
        """Load links configuration. In production, consider loading from a database."""
        return {
            "Link 1": "https://t.me/addlist/k_I9pFnlDkEyYjVl",
            "Link 2": "https://t.me/pinaywalkgirls",
            "Link 3": "https://t.me/+9XenMPwkQAQ2Nzll",
            "Link 4": "https://t.me/+LA6xn67ruvViN2Y1",
            "Link 5": "https://t.me/+c08qfoR41GY0YTU9",
            "Link 6": "https://t.me/downpinay",
            "Link 7": "https://t.me/+CrP4i74WskwxMjdl",
            "Link 8": "https://t.me/+na36O3XeatpmZDc1",
            "Link 9": "https://t.me/+I691GXtd7U44MTdl",
            "Link 10": "https://t.me/+J55Fxj2Ew6xkMWY1",
            "Link 11": "https://t.me/+ziG83SRhsp9iNjM1",
            "Link 12": "http://t.me/katorsxbot/atabs",
            "Link 13": "https://t.me/+MTyth4gVAXxmNDJl",
            "Link 14": "http://t.me/pinayatabs18bot/librenood",
            "Link 15": "https://t.me/batangmalandibot?startapp=WatchNow",
            "Link 16": "https://t.me/pnytbsvideosbot?startapp=watchnow",
            "Link 17": "https://t.me/+qzH8LRQwLYhjYjA1"
        }
    
    def _setup_handlers(self):
        """Setup message and callback handlers."""
        self.bot.message_handler(commands=['start'])(self.handle_start)
        self.bot.message_handler(commands=['help'])(self.handle_help)
        self.bot.message_handler(commands=['stats'])(self.handle_stats)
        self.bot.callback_query_handler(func=lambda call: True)(self.handle_callback)
    
    def send_and_auto_delete(self, chat_id: int, text: str, delay: Optional[int] = None) -> None:
        """Send a message and automatically delete it after specified delay."""
        if delay is None:
            delay = self.auto_delete_delay
            
        try:
            msg = self.bot.send_message(chat_id, text)
            
            def delete_later():
                time.sleep(delay)
                try:
                    self.bot.delete_message(chat_id, msg.message_id)
                    logger.debug(f"Auto-deleted message {msg.message_id} from chat {chat_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete message {msg.message_id}: {e}")
            
            Thread(target=delete_later, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Failed to send message to chat {chat_id}: {e}")
    
    def create_links_keyboard(self) -> types.InlineKeyboardMarkup:
        """Create inline keyboard with all available links."""
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        buttons = []
        for name in self.links.keys():
            btn = types.InlineKeyboardButton(name, callback_data=f"link_{name}")
            buttons.append(btn)
        
        # Add buttons in rows of 2
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                markup.row(buttons[i], buttons[i + 1])
            else:
                markup.row(buttons[i])
        
        # Add help button
        help_btn = types.InlineKeyboardButton("ℹ️ Help", callback_data="help")
        markup.row(help_btn)
        
        return markup
    
    def handle_start(self, message):
        """Handle /start command."""
        try:
            user = message.from_user
            welcome_text = f"👋 Welcome <b>{user.first_name}</b>!\n\n"
            welcome_text += "Choose a link below to join the community:"
            
            markup = self.create_links_keyboard()
            self.bot.send_message(
                message.chat.id, 
                welcome_text, 
                reply_markup=markup
            )
            
            logger.info(f"User {user.id} ({user.username}) started the bot")
            
        except Exception as e:
            logger.error(f"Error in start handler: {e}")
            self.bot.send_message(
                message.chat.id, 
                "❌ An error occurred. Please try again later."
            )
    
    def handle_help(self, message):
        """Handle /help command."""
        help_text = """
🤖 <b>Bot Help</b>

<b>Commands:</b>
• /start - Show main menu
• /help - Show this help message
• /stats - Show bot statistics (admin only)

<b>How to use:</b>
1. Click on any link button to receive the invite link
2. Links are automatically deleted after 15 seconds for privacy
3. Join the community and enjoy!

<b>Need support?</b>
Contact the administrator if you encounter any issues.
        """
        
        self.bot.send_message(message.chat.id, help_text.strip())
    
    def handle_stats(self, message):
        """Handle /stats command (admin only)."""
        if message.from_user.id != self.admin_id:
            self.bot.send_message(message.chat.id, "❌ Access denied. Admin only.")
            return
        
        stats_text = f"""
📊 <b>Bot Statistics</b>

• Total links: {len(self.links)}
• Bot uptime: Running
• Auto-delete delay: {self.auto_delete_delay} seconds

<b>Available links:</b>
{chr(10).join([f"• {name}" for name in self.links.keys()])}
        """
        
        self.bot.send_message(message.chat.id, stats_text.strip())
    
    def handle_callback(self, call):
        """Handle callback queries from inline keyboards."""
        try:
            if call.data == "help":
                self.handle_help(call.message)
                self.bot.answer_callback_query(call.id, "Help information sent!")
                return
            
            if call.data.startswith("link_"):
                link_name = call.data[5:]  # Remove "link_" prefix
                
                if link_name in self.links:
                    link_url = self.links[link_name]
                    response_text = f"🔗 <b>{link_name}</b>\n\n👉 {link_url}\n\n⏰ This message will be deleted in {self.auto_delete_delay} seconds"
                    
                    self.send_and_auto_delete(
                        call.message.chat.id, 
                        response_text, 
                        self.auto_delete_delay
                    )
                    
                    self.bot.answer_callback_query(
                        call.id, 
                        f"✅ {link_name} sent! Check your chat."
                    )
                    
                    logger.info(f"User {call.from_user.id} requested {link_name}")
                else:
                    self.bot.answer_callback_query(call.id, "❌ Link not found!")
            else:
                self.bot.answer_callback_query(call.id, "❌ Unknown command!")
                
        except Exception as e:
            logger.error(f"Error in callback handler: {e}")
            self.bot.answer_callback_query(call.id, "❌ An error occurred!")
    
    def run(self):
        """Start the bot with error handling and restart capability."""
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            try:
                logger.info("Starting bot...")
                self.bot.infinity_polling(
                    timeout=10, 
                    long_polling_timeout=5,
                    none_stop=True,
                    interval=1
                )
            except Exception as e:
                retry_count += 1
                logger.error(f"Bot crashed (attempt {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    sleep_time = min(60 * retry_count, 300)  # Exponential backoff, max 5 minutes
                    logger.info(f"Restarting bot in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.critical("Max retries reached. Bot shutting down.")
                    break

def main():
    """Main function to run the bot."""
    try:
        bot = TelegramLinkBot()
        bot.run()
    except Exception as e:
        logger.critical(f"Failed to initialize bot: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
