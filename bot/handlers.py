"""
Enhanced handler functions for the Telegram bot
Contains all command and callback handlers with improved functionality
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest, NetworkError

from bot.config import Config
from bot.database import Database
from bot.search import SearchEngine, SearchProgress
from bot.keyboards import BotKeyboards
from bot.utils import MessageFormatter, Validator, RateLimiter

logger = logging.getLogger(__name__)

# Global instances
config = Config()
db = Database()
search_engine = SearchEngine()
keyboards = BotKeyboards()
formatter = MessageFormatter()
validator = Validator()
rate_limiter = RateLimiter()

# Store current search results in memory (in production, use Redis)
user_search_results = {}
user_search_states = {}

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced start command handler"""
    try:
        user = update.effective_user

        # Add/update user in database
        db.add_or_update_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

        # Send welcome message with main menu
        welcome_text = formatter.format_welcome_message(user.first_name or user.username or "there")

        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboards.main_menu(),
            parse_mode='Markdown'
        )

        logger.info(f"User {user.id} started the bot")

    except Exception as e:
        logger.error(f"Start handler error: {e}")
        await update.message.reply_text(
            "Welcome! I'm your enhanced course finder bot. Use /help for assistance.",
            reply_markup=keyboards.main_menu()
        )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced help command handler"""
    try:
        help_text = formatter.format_help_message()

        await update.message.reply_text(
            help_text,
            reply_markup=keyboards.back_button(),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Help handler error: {e}")
        await update.message.reply_text(
            "Help information is temporarily unavailable. Please try again later."
        )

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced search message handler with progress tracking"""
    try:
        user_id = update.effective_user.id
        query = update.message.text.strip()

        # Validate query
        if not validator.is_valid_search_query(query):
            await update.message.reply_text(
                formatter.format_error_message("invalid_query"),
                parse_mode='Markdown'
            )
            return

        # Check rate limiting
        if not rate_limiter.is_allowed(user_id, config.RATE_LIMIT_SEARCHES, config.RATE_LIMIT_WINDOW):
            await update.message.reply_text(
                formatter.format_error_message("rate_limit"),
                parse_mode='Markdown'
            )
            return

        # Also check database rate limiting
        if not db.check_rate_limit(user_id):
            await update.message.reply_text(
                formatter.format_error_message("rate_limit"),
                parse_mode='Markdown'
            )
            return

        # Send initial progress message
        progress_msg = await update.message.reply_text(
            "🔍 Starting search...",
            reply_markup=keyboards.progress_indicator()
        )

        # Create progress tracker
        progress = SearchProgress(progress_msg, config)

        # Get user settings
        user_settings = db.get_user_settings(user_id)
        max_results = user_settings.get('results_per_page', config.MAX_RESULTS_PER_PAGE)

        # Perform search
        try:
            results, total_found = await search_engine.search_courses(
                query=query,
                max_results=max_results,
                progress_callback=progress.update
            )

            progress.stop()

            # Store results for pagination and callbacks
            user_search_results[user_id] = {
                'query': query,
                'results': results,
                'total_found': total_found,
                'current_page': 0
            }

            # Add to search history
            db.add_search_history(user_id, query, len(results))

            # Format and send results
            if results:
                results_text = formatter.format_search_results(
                    results, query, 0, total_found
                )

                await progress_msg.edit_text(
                    results_text,
                    reply_markup=keyboards.search_results(results, 0, 1),
                    parse_mode='Markdown'
                )
            else:
                await progress_msg.edit_text(
                    formatter.format_error_message("no_results"),
                    reply_markup=keyboards.search_options(),
                    parse_mode='Markdown'
                )

        except Exception as search_error:
            progress.stop()
            logger.error(f"Search error for user {user_id}: {search_error}")

            await progress_msg.edit_text(
                formatter.format_error_message("search_failed", str(search_error)),
                reply_markup=keyboards.search_options(),
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Search handler error: {e}")
        await update.message.reply_text(
            formatter.format_error_message("api_error"),
            parse_mode='Markdown'
        )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced callback query handler for inline keyboards"""
    try:
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        data = query.data

        # Route to appropriate handler based on callback data
        if data.startswith("action_"):
            await handle_action_callbacks(query, user_id, data)
        elif data.startswith("search_"):
            await handle_search_callbacks(query, user_id, data)
        elif data.startswith("result_"):
            await handle_result_callbacks(query, user_id, data)
        elif data.startswith("fav_"):
            await handle_favorite_callbacks(query, user_id, data)
        elif data.startswith("history_"):
            await handle_history_callbacks(query, user_id, data)
        elif data.startswith("setting_"):
            await handle_setting_callbacks(query, user_id, data)
        elif data.startswith("back_"):
            await handle_back_callbacks(query, user_id, data)
        elif data.startswith("page_"):
            await handle_pagination_callbacks(query, user_id, data)
        elif data.startswith("cancel_"):
            await query.edit_message_text(
                "Operation cancelled. Use the menu to continue.",
                reply_markup=keyboards.main_menu()
            )
        elif data.startswith("confirm_"):
            # Handle confirmations
            await query.edit_message_text(
                "Action confirmed. Processing...",
                reply_markup=keyboards.main_menu()
            )
        else:
            await query.edit_message_text(
                "Please use the menu buttons to navigate.",
                reply_markup=keyboards.main_menu()
            )

    except BadRequest as e:
        logger.warning(f"Bad request in callback handler: {e}")
    except Exception as e:
        logger.error(f"Callback handler error: {e}")
        try:
            await query.edit_message_text(
                "⚠️ An error occurred. Please try again.",
                reply_markup=keyboards.main_menu()
            )
        except:
            pass

async def handle_action_callbacks(query, user_id: int, data: str):
    """Handle main action callbacks"""
    action = data.replace("action_", "")

    if action == "search":
        await query.edit_message_text(
            "🔍 **Search Options**\n\nChoose your preferred search method:",
            reply_markup=keyboards.search_options(),
            parse_mode='Markdown'
        )

    elif action == "favorites":
        favorites = db.get_favorites(user_id)
        favorites_text = formatter.format_favorites_list(favorites)

        await query.edit_message_text(
            favorites_text,
            reply_markup=keyboards.favorites_menu(favorites),
            parse_mode='Markdown'
        )

    elif action == "history":
        history = db.get_search_history(user_id)
        history_text = formatter.format_search_history(history)

        await query.edit_message_text(
            history_text,
            reply_markup=keyboards.history_menu(history),
            parse_mode='Markdown'
        )

    elif action == "settings":
        settings = db.get_user_settings(user_id)
        settings_text = formatter.format_settings_display(settings)

        await query.edit_message_text(
            settings_text,
            reply_markup=keyboards.settings_menu(settings),
            parse_mode='Markdown'
        )

    elif action == "help":
        help_text = formatter.format_help_message()

        await query.edit_message_text(
            help_text,
            reply_markup=keyboards.back_button(),
            parse_mode='Markdown'
        )

    elif action == "stats":
        await show_user_stats(query, user_id)

async def handle_search_callbacks(query, user_id: int, data: str):
    """Handle search-related callbacks"""
    search_type = data.replace("search_", "")

    instructions = {
        "quick": "Type any course name to start a quick search across all platforms.",
        "advanced": "Type your course name. I'll search with advanced filters for better results.",
        "drive": "Type your course name to search specifically on Google Drive.",
        "mediafire": "Type your course name to search specifically on MediaFire.",
        "mega": "Type your course name to search specifically on Mega.",
        "all": "Type your course name to search across all supported platforms."
    }

    instruction = instructions.get(search_type, "Type your course name to search.")

    # Store search preference
    user_search_states[user_id] = {
        'type': search_type,
        'waiting_for_query': True
    }

    await query.edit_message_text(
        f"🔍 **{search_type.title()} Search**\n\n{instruction}",
        reply_markup=keyboards.back_button(),
        parse_mode='Markdown'
    )

async def handle_result_callbacks(query, user_id: int, data: str):
    """Handle result-related callbacks"""
    if user_id not in user_search_results:
        await query.edit_message_text(
            "No search results available. Please perform a new search.",
            reply_markup=keyboards.main_menu()
        )
        return

    action_parts = data.split("_")
    if len(action_parts) < 2:
        return

    action = action_parts[1]

    if action.isdigit():
        # Show result details
        result_index = int(action)
        results = user_search_results[user_id]['results']

        if 0 <= result_index < len(results):
            result = results[result_index]
            details_text = formatter.format_result_details(result, result_index)

            await query.edit_message_text(
                details_text,
                reply_markup=keyboards.result_details(result_index),
                parse_mode='Markdown'
            )

async def handle_favorite_callbacks(query, user_id: int, data: str):
    """Handle favorite-related callbacks"""
    action_parts = data.split("_", 2)
    if len(action_parts) < 2:
        return

    action = action_parts[1]

    if action.isdigit() and user_id in user_search_results:
        # Add to favorites from search results
        result_index = int(action)
        results = user_search_results[user_id]['results']

        if 0 <= result_index < len(results):
            result = results[result_index]

            success = db.add_favorite(
                user_id=user_id,
                title=result.get('title', 'Untitled'),
                url=result.get('link', ''),
                platform=result.get('platform', 'Unknown')
            )

            if success:
                await query.answer("⭐ Added to favorites!")
            else:
                await query.answer("Already in favorites!")

    elif action == "add" and len(action_parts) > 2:
        # Add specific result to favorites
        result_index = int(action_parts[2])
        # Implementation similar to above
        pass

    elif action == "clear":
        # Show confirmation dialog
        await query.edit_message_text(
            "🗑️ **Clear All Favorites**\n\nAre you sure you want to remove all saved favorites? This action cannot be undone.",
            reply_markup=keyboards.confirmation_dialog("clear_favorites"),
            parse_mode='Markdown'
        )

    elif action == "export":
        favorites = db.get_favorites(user_id)
        export_text = formatter.export_favorites_text(favorites)

        await query.edit_message_text(
            f"📤 **Favorites Export**\n\n```\n{export_text}\n```",
            reply_markup=keyboards.back_button(),
            parse_mode='Markdown'
        )

async def handle_history_callbacks(query, user_id: int, data: str):
    """Handle history-related callbacks"""
    action_parts = data.split("_", 2)
    if len(action_parts) < 2:
        return

    action = action_parts[1]

    if action == "search" and len(action_parts) > 2:
        # Re-run search from history
        search_index = int(action_parts[2])
        history = db.get_search_history(user_id)

        if 0 <= search_index < len(history):
            search_query = history[search_index]['query']

            # Simulate a new search message
            await query.edit_message_text(
                f"🔍 Re-running search: \"{search_query}\"",
                reply_markup=keyboards.progress_indicator()
            )

            # Perform the search (similar to search_handler)
            try:
                results, total_found = await search_engine.search_courses(
                    query=search_query,
                    max_results=config.MAX_RESULTS_PER_PAGE
                )

                user_search_results[user_id] = {
                    'query': search_query,
                    'results': results,
                    'total_found': total_found,
                    'current_page': 0
                }

                db.add_search_history(user_id, search_query, len(results))

                if results:
                    results_text = formatter.format_search_results(
                        results, search_query, 0, total_found
                    )

                    await query.edit_message_text(
                        results_text,
                        reply_markup=keyboards.search_results(results, 0, 1),
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text(
                        formatter.format_error_message("no_results"),
                        reply_markup=keyboards.search_options(),
                        parse_mode='Markdown'
                    )

            except Exception as e:
                await query.edit_message_text(
                    formatter.format_error_message("search_failed"),
                    reply_markup=keyboards.main_menu(),
                    parse_mode='Markdown'
                )

    elif action == "clear":
        await query.edit_message_text(
            "🗑️ **Clear Search History**\n\nAre you sure you want to clear your search history? This action cannot be undone.",
            reply_markup=keyboards.confirmation_dialog("clear_history"),
            parse_mode='Markdown'
        )

async def handle_setting_callbacks(query, user_id: int, data: str):
    """Handle settings callbacks"""
    setting = data.replace("setting_", "")
    current_settings = db.get_user_settings(user_id)

    if setting == "results_per_page":
        current_value = current_settings.get('results_per_page', 5)
        new_value = (current_value % 10) + 3  # Cycle between 3-10

        current_settings['results_per_page'] = new_value
        db.update_user_settings(user_id, current_settings)

        await query.answer(f"Results per page set to {new_value}")

        # Refresh settings display
        settings_text = formatter.format_settings_display(current_settings)
        await query.edit_message_text(
            settings_text,
            reply_markup=keyboards.settings_menu(current_settings),
            parse_mode='Markdown'
        )

    elif setting == "notifications":
        current_value = current_settings.get('notifications', True)
        current_settings['notifications'] = not current_value
        db.update_user_settings(user_id, current_settings)

        status = "enabled" if not current_value else "disabled"
        await query.answer(f"Notifications {status}")

        # Refresh settings display
        settings_text = formatter.format_settings_display(current_settings)
        await query.edit_message_text(
            settings_text,
            reply_markup=keyboards.settings_menu(current_settings),
            parse_mode='Markdown'
        )

async def handle_back_callbacks(query, user_id: int, data: str):
    """Handle back navigation callbacks"""
    destination = data.replace("back_", "")

    if destination == "main":
        welcome_text = formatter.format_welcome_message(
            update.effective_user.first_name or "there"
        )

        await query.edit_message_text(
            welcome_text,
            reply_markup=keyboards.main_menu(),
            parse_mode='Markdown'
        )

    elif destination == "results" and user_id in user_search_results:
        search_data = user_search_results[user_id]
        results_text = formatter.format_search_results(
            search_data['results'],
            search_data['query'],
            search_data['current_page'],
            search_data['total_found']
        )

        await query.edit_message_text(
            results_text,
            reply_markup=keyboards.search_results(
                search_data['results'],
                search_data['current_page'],
                1
            ),
            parse_mode='Markdown'
        )

async def handle_pagination_callbacks(query, user_id: int, data: str):
    """Handle pagination callbacks"""
    if user_id not in user_search_results:
        await query.answer("No search results available")
        return

    page_str = data.replace("page_", "")
    if not page_str.isdigit():
        return

    new_page = int(page_str)
    search_data = user_search_results[user_id]
    search_data['current_page'] = new_page

    # Update display
    results_text = formatter.format_search_results(
        search_data['results'],
        search_data['query'],
        new_page,
        search_data['total_found']
    )

    await query.edit_message_text(
        results_text,
        reply_markup=keyboards.search_results(
            search_data['results'],
            new_page,
            1
        ),
        parse_mode='Markdown'
    )

async def show_user_stats(query, user_id: int):
    """Show user statistics"""
    try:
        history = db.get_search_history(user_id)
        favorites = db.get_favorites(user_id)

        total_searches = len(history)
        total_favorites = len(favorites)

        # Calculate some basic stats
        total_results_found = sum(h.get('results_count', 0) for h in history)
        avg_results = total_results_found / max(total_searches, 1)

        stats_text = f"""
📊 **Your Bot Statistics**

**🔍 Search Activity:**
• Total searches: **{total_searches}**
• Results found: **{total_results_found}**
• Average per search: **{avg_results:.1f}**

**⭐ Collection:**
• Saved favorites: **{total_favorites}**

**📅 Activity:**
• Member since: **Registration date**
• Last search: **Recent activity**

**🏆 Achievement:**
{'🥇 Power User!' if total_searches > 50 else '🚀 Getting Started!' if total_searches > 10 else '👋 New User!'}

Keep exploring and finding great courses! 🎓
"""

        await query.edit_message_text(
            stats_text,
            reply_markup=keyboards.back_button(),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Stats display error: {e}")
        await query.edit_message_text(
            "📊 Statistics temporarily unavailable.",
            reply_markup=keyboards.back_button()
        )

# Additional handler functions for specific commands
async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Settings command handler"""
    user_id = update.effective_user.id
    settings = db.get_user_settings(user_id)
    settings_text = formatter.format_settings_display(settings)

    await update.message.reply_text(
        settings_text,
        reply_markup=keyboards.settings_menu(settings),
        parse_mode='Markdown'
    )

async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """History command handler"""
    user_id = update.effective_user.id
    history = db.get_search_history(user_id)
    history_text = formatter.format_search_history(history)

    await update.message.reply_text(
        history_text,
        reply_markup=keyboards.history_menu(history),
        parse_mode='Markdown'
    )

async def favorites_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Favorites command handler"""
    user_id = update.effective_user.id
    favorites = db.get_favorites(user_id)
    favorites_text = formatter.format_favorites_list(favorites)

    await update.message.reply_text(
        favorites_text,
        reply_markup=keyboards.favorites_menu(favorites),
        parse_mode='Markdown'
    )
