import os
import logging
import json
import time
import telebot
from telebot import types
from threading import Thread
from typing import Dict, Optional

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
    
    def _get_default_links(self) -> Dict[str, str]:
        """Default links configuration."""
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
    
    def _load_links(self) -> Dict[str, str]:
        """Load links from JSON file, create with defaults if not exists."""
        try:
            with open('links.json', 'r', encoding='utf-8') as f:
                links = json.load(f)
                logger.info(f"Loaded {len(links)} links from file")
                return links
        except FileNotFoundError:
            logger.info("links.json not found, creating with default links")
            default_links = self._get_default_links()
            self._save_links(default_links)
            return default_links
        except json.JSONDecodeError:
            logger.error("Error reading links.json, using default links")
            return self._get_default_links()
    
    def _save_links(self, links: Optional[Dict[str, str]] = None):
        """Save links to JSON file."""
        try:
            links_to_save = links if links is not None else self.links
            with open('links.json', 'w', encoding='utf-8') as f:
                json.dump(links_to_save, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(links_to_save)} links to file")
        except Exception as e:
            logger.error(f"Error saving links: {e}")
    
    def _setup_handlers(self):
        """Setup message and callback handlers."""
        self.bot.message_handler(commands=['start'])(self.handle_start)
        self.bot.message_handler(commands=['help'])(self.handle_help)
        self.bot.message_handler(commands=['stats'])(self.handle_stats)
        
        # Admin commands for link management
        self.bot.message_handler(commands=['addlink'])(self.handle_add_link)
        self.bot.message_handler(commands=['updatelink'])(self.handle_update_link)
        self.bot.message_handler(commands=['removelink'])(self.handle_remove_link)
        self.bot.message_handler(commands=['listlinks'])(self.handle_list_links)
        self.bot.message_handler(commands=['reloadlinks'])(self.handle_reload_links)
        
        self.bot.callback_query_handler(func=lambda call: True)(self.handle_callback)
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id == self.admin_id
    
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
        
        # Add admin and help buttons
        admin_btn = types.InlineKeyboardButton("⚙️ Admin", callback_data="admin_menu")
        help_btn = types.InlineKeyboardButton("ℹ️ Help", callback_data="help")
        markup.row(admin_btn, help_btn)
        
        return markup
    
    def create_admin_keyboard(self) -> types.InlineKeyboardMarkup:
        """Create admin management keyboard."""
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        stats_btn = types.InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")
        reload_btn = types.InlineKeyboardButton("🔄 Reload Links", callback_data="admin_reload")
        markup.row(stats_btn, reload_btn)
        
        back_btn = types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")
        markup.row(back_btn)
        
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

<b>User Commands:</b>
• /start - Show main menu with links
• /help - Show this help message

<b>How to use:</b>
1. Click on any link button to receive the invite link
2. Links are automatically deleted after {delay} seconds for privacy
3. Join the community and enjoy!

<b>Admin Commands:</b>
• /stats - Show bot statistics
• /addlink [name] [url] - Add new link
• /updatelink [name] [url] - Update existing link
• /removelink [name] - Remove link
• /listlinks - Show all links
• /reloadlinks - Reload links from file

<b>Examples:</b>
<code>/addlink "New Link" https://t.me/newchannel</code>
<code>/updatelink "Link 1" https://t.me/updated</code>
<code>/removelink "Old Link"</code>

<b>Need support?</b>
Contact the administrator if you encounter any issues.
        """.format(delay=self.auto_delete_delay)
        
        self.bot.send_message(message.chat.id, help_text.strip())
    
    def handle_stats(self, message):
        """Handle /stats command (admin only)."""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Access denied. Admin only.")
            return
        
        stats_text = f"""
📊 <b>Bot Statistics</b>

• Total links: {len(self.links)}
• Auto-delete delay: {self.auto_delete_delay} seconds
• Admin ID: {self.admin_id}
• Bot status: ✅ Running

<b>Available links:</b>
{chr(10).join([f"• {name}" for name in self.links.keys()])}

<b>Recent activity:</b>
• Links file: ✅ Available
• Log file: ✅ Active
        """
        
        self.bot.send_message(message.chat.id, stats_text.strip())
    
    def handle_add_link(self, message):
        """Handle /addlink command (admin only)."""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Access denied. Admin only.")
            return
        
        try:
            # Parse command: /addlink "Link Name" https://url
            text = message.text[9:].strip()  # Remove '/addlink '
            
            # Handle quoted link names
            if text.startswith('"'):
                end_quote = text.find('"', 1)
                if end_quote == -1:
                    raise ValueError("Missing closing quote")
                link_name = text[1:end_quote]
                link_url = text[end_quote+1:].strip()
            else:
                parts = text.split(' ', 1)
                if len(parts) != 2:
                    raise ValueError("Invalid format")
                link_name, link_url = parts
            
            if not link_url.startswith(('http://', 'https://', 't.me/')):
                raise ValueError("Invalid URL format")
            
            self.links[link_name] = link_url
            self._save_links()
            
            self.bot.send_message(
                message.chat.id, 
                f"✅ <b>Link Added!</b>\n\n📝 Name: {link_name}\n🔗 URL: {link_url}"
            )
            
            logger.info(f"Admin {message.from_user.id} added link: {link_name}")
            
        except Exception as e:
            self.bot.send_message(
                message.chat.id, 
                f"❌ <b>Error adding link!</b>\n\n"
                f"Format: <code>/addlink \"Link Name\" https://url</code>\n"
                f"Example: <code>/addlink \"New Channel\" https://t.me/channel</code>\n\n"
                f"Error: {str(e)}"
            )
    
    def handle_update_link(self, message):
        """Handle /updatelink command (admin only)."""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Access denied. Admin only.")
            return
        
        try:
            text = message.text[12:].strip()  # Remove '/updatelink '
            
            # Handle quoted link names
            if text.startswith('"'):
                end_quote = text.find('"', 1)
                if end_quote == -1:
                    raise ValueError("Missing closing quote")
                link_name = text[1:end_quote]
                link_url = text[end_quote+1:].strip()
            else:
                parts = text.split(' ', 1)
                if len(parts) != 2:
                    raise ValueError("Invalid format")
                link_name, link_url = parts
            
            if link_name not in self.links:
                self.bot.send_message(message.chat.id, f"❌ Link '{link_name}' not found!")
                return
            
            if not link_url.startswith(('http://', 'https://', 't.me/')):
                raise ValueError("Invalid URL format")
            
            old_url = self.links[link_name]
            self.links[link_name] = link_url
            self._save_links()
            
            self.bot.send_message(
                message.chat.id, 
                f"✅ <b>Link Updated!</b>\n\n"
                f"📝 Name: {link_name}\n"
                f"🔗 Old URL: {old_url}\n"
                f"🔗 New URL: {link_url}"
            )
            
            logger.info(f"Admin {message.from_user.id} updated link: {link_name}")
            
        except Exception as e:
            self.bot.send_message(
                message.chat.id, 
                f"❌ <b>Error updating link!</b>\n\n"
                f"Format: <code>/updatelink \"Link Name\" https://newurl</code>\n\n"
                f"Error: {str(e)}"
            )
    
    def handle_remove_link(self, message):
        """Handle /removelink command (admin only)."""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Access denied. Admin only.")
            return
        
        try:
            link_name = message.text[12:].strip()  # Remove '/removelink '
            
            # Handle quoted names
            if link_name.startswith('"') and link_name.endswith('"'):
                link_name = link_name[1:-1]
            
            if not link_name:
                raise ValueError("Link name is required")
            
            if link_name not in self.links:
                self.bot.send_message(message.chat.id, f"❌ Link '{link_name}' not found!")
                return
            
            removed_url = self.links[link_name]
            del self.links[link_name]
            self._save_links()
            
            self.bot.send_message(
                message.chat.id, 
                f"✅ <b>Link Removed!</b>\n\n"
                f"📝 Name: {link_name}\n"
                f"🔗 URL: {removed_url}"
            )
            
            logger.info(f"Admin {message.from_user.id} removed link: {link_name}")
            
        except Exception as e:
            self.bot.send_message(
                message.chat.id, 
                f"❌ <b>Error removing link!</b>\n\n"
                f"Format: <code>/removelink \"Link Name\"</code>\n\n"
                f"Error: {str(e)}"
            )
    
    def handle_list_links(self, message):
        """Handle /listlinks command (admin only)."""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Access denied. Admin only.")
            return
        
        if not self.links:
            self.bot.send_message(message.chat.id, "📝 No links available.")
            return
        
        links_text = "📝 <b>Current Links:</b>\n\n"
        for i, (name, url) in enumerate(self.links.items(), 1):
            links_text += f"{i}. <b>{name}</b>\n   🔗 {url}\n\n"
        
        # Split message if too long
        if len(links_text) > 4000:
            chunks = [links_text[i:i+4000] for i in range(0, len(links_text), 4000)]
            for chunk in chunks:
                self.bot.send_message(message.chat.id, chunk)
        else:
            self.bot.send_message(message.chat.id, links_text)
    
    def handle_reload_links(self, message):
        """Handle /reloadlinks command (admin only)."""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Access denied. Admin only.")
            return
        
        try:
            old_count = len(self.links)
            self.links = self._load_links()
            new_count = len(self.links)
            
            self.bot.send_message(
                message.chat.id, 
                f"✅ <b>Links Reloaded!</b>\n\n"
                f"📝 Previous count: {old_count}\n"
                f"📝 Current count: {new_count}"
            )
            
            logger.info(f"Admin {message.from_user.id} reloaded links")
            
        except Exception as e:
            self.bot.send_message(
                message.chat.id, 
                f"❌ Error reloading links: {str(e)}"
            )
    
    def handle_callback(self, call):
        """Handle callback queries from inline keyboards."""
        try:
            if call.data == "help":
                self.handle_help(call.message)
                self.bot.answer_callback_query(call.id, "Help information sent!")
                return
            
            if call.data == "admin_menu":
                if not self._is_admin(call.from_user.id):
                    self.bot.answer_callback_query(call.id, "❌ Access denied!")
                    return
                
                admin_text = "⚙️ <b>Admin Panel</b>\n\nChoose an action:"
                markup = self.create_admin_keyboard()
                
                self.bot.edit_message_text(
                    admin_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )
                self.bot.answer_callback_query(call.id, "Admin panel opened!")
                return
            
            if call.data == "admin_stats":
                if not self._is_admin(call.from_user.id):
                    self.bot.answer_callback_query(call.id, "❌ Access denied!")
                    return
                
                self.handle_stats(call.message)
                self.bot.answer_callback_query(call.id, "Statistics sent!")
                return
            
            if call.data == "admin_reload":
                if not self._is_admin(call.from_user.id):
                    self.bot.answer_callback_query(call.id, "❌ Access denied!")
                    return
                
                self.handle_reload_links(call.message)
                self.bot.answer_callback_query(call.id, "Links reloaded!")
                return
            
            if call.data == "back_to_menu":
                user = call.from_user
                welcome_text = f"👋 Welcome <b>{user.first_name}</b>!\n\n"
                welcome_text += "Choose a link below to join the community:"
                
                markup = self.create_links_keyboard()
                self.bot.edit_message_text(
                    welcome_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )
                self.bot.answer_callback_query(call.id, "Back to main menu!")
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
