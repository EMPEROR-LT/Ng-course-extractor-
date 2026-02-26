#!/usr/bin/env python3
"""
Enhanced Telegram Bot for Course Link Finding
Main entry point for the application
"""

import asyncio
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bot.config import Config
from bot.handlers import (
    start_handler, help_handler, search_handler, callback_handler,
    settings_handler, history_handler, favorites_handler
)
from bot.database import Database

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return  # Suppress logs for health checks

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Health check server started on port {port}")
    server.serve_forever()

async def error_handler(update, context):
    """Log errors and send user-friendly messages"""
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Something went wrong. Please try again later.\n"
            "If the problem persists, contact support."
        )

def main():
    """Main function to start the bot"""
    # Start health check server for Render
    if os.environ.get("RENDER"):
        threading.Thread(target=run_health_check_server, daemon=True).start()

    # Initialize configuration
    config = Config()

    # Initialize database
    db = Database()

    # Create application
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("settings", settings_handler))
    application.add_handler(CommandHandler("history", history_handler))
    application.add_handler(CommandHandler("favorites", favorites_handler))

    # Message handlers
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        search_handler
    ))

    # Callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("🚀 Enhanced Course Bot is starting...")
    print("🤖 Bot is running... Press Ctrl+C to stop")

    try:
        application.run_polling(
            poll_interval=1.0,
            timeout=10,
            bootstrap_retries=3,
            read_timeout=30,
            write_timeout=30
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        logger.info("Bot shutdown complete")

if __name__ == '__main__':
    main()
