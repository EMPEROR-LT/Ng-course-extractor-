"""
Inline keyboard layouts for enhanced user interaction
Provides various keyboard configurations for different bot features
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any

class BotKeyboards:
    """Class containing all inline keyboard layouts"""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🔍 Search Courses", callback_data="action_search"),
                InlineKeyboardButton("⭐ Favorites", callback_data="action_favorites")
            ],
            [
                InlineKeyboardButton("📚 History", callback_data="action_history"),
                InlineKeyboardButton("⚙️ Settings", callback_data="action_settings")
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="action_help"),
                InlineKeyboardButton("📊 Stats", callback_data="action_stats")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def search_options() -> InlineKeyboardMarkup:
        """Search options keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🎯 Quick Search", callback_data="search_quick"),
                InlineKeyboardButton("🔧 Advanced", callback_data="search_advanced")
            ],
            [
                InlineKeyboardButton("📁 Google Drive", callback_data="search_drive"),
                InlineKeyboardButton("💾 MediaFire", callback_data="search_mediafire")
            ],
            [
                InlineKeyboardButton("☁️ Mega", callback_data="search_mega"),
                InlineKeyboardButton("📦 All Platforms", callback_data="search_all")
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def search_results(results: List[Dict], page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
        """Search results keyboard with pagination"""
        keyboard = []

        # Add result buttons (with index for identification)
        for i, result in enumerate(results):
            platform = BotKeyboards._get_platform_emoji(result.get('link', ''))
            title = result.get('title', 'Untitled')[:40] + "..." if len(result.get('title', '')) > 40 else result.get('title', 'Untitled')

            keyboard.append([
                InlineKeyboardButton(
                    f"{platform} {title}",
                    callback_data=f"result_{i}"
                ),
                InlineKeyboardButton("⭐", callback_data=f"fav_{i}")
            ])

        # Pagination controls
        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{page-1}"))

            nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="page_info"))

            if page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}"))

            keyboard.append(nav_buttons)

        # Action buttons
        keyboard.extend([
            [
                InlineKeyboardButton("🔍 New Search", callback_data="action_search"),
                InlineKeyboardButton("📋 Export All", callback_data="search_export")
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_main")
            ]
        ])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def result_details(result_index: int) -> InlineKeyboardMarkup:
        """Individual result details keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🔗 Open Link", callback_data=f"open_{result_index}"),
                InlineKeyboardButton("⭐ Add to Favorites", callback_data=f"fav_add_{result_index}")
            ],
            [
                InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{result_index}"),
                InlineKeyboardButton("📤 Share", callback_data=f"share_{result_index}")
            ],
            [
                InlineKeyboardButton("« Back to Results", callback_data="back_results")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def favorites_menu(favorites: List[Dict], page: int = 0) -> InlineKeyboardMarkup:
        """Favorites management keyboard"""
        keyboard = []

        # Show favorites (5 per page)
        start_idx = page * 5
        end_idx = min(start_idx + 5, len(favorites))

        for i in range(start_idx, end_idx):
            fav = favorites[i]
            platform = BotKeyboards._get_platform_emoji(fav.get('url', ''))
            title = fav.get('title', 'Untitled')[:35] + "..." if len(fav.get('title', '')) > 35 else fav.get('title', 'Untitled')

            keyboard.append([
                InlineKeyboardButton(
                    f"{platform} {title}",
                    callback_data=f"fav_open_{i}"
                ),
                InlineKeyboardButton("🗑️", callback_data=f"fav_del_{i}")
            ])

        # Pagination for favorites
        total_pages = (len(favorites) + 4) // 5
        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"fav_page_{page-1}"))

            nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="fav_info"))

            if page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"fav_page_{page+1}"))

            keyboard.append(nav_buttons)

        # Action buttons
        keyboard.extend([
            [
                InlineKeyboardButton("🗑️ Clear All", callback_data="fav_clear"),
                InlineKeyboardButton("📤 Export", callback_data="fav_export")
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_main")
            ]
        ])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def history_menu(history: List[Dict]) -> InlineKeyboardMarkup:
        """Search history keyboard"""
        keyboard = []

        # Show recent searches
        for i, search in enumerate(history[:10]):
            query = search.get('query', '')[:30] + "..." if len(search.get('query', '')) > 30 else search.get('query', '')
            results_count = search.get('results_count', 0)

            keyboard.append([
                InlineKeyboardButton(
                    f"🔍 {query} ({results_count} results)",
                    callback_data=f"history_search_{i}"
                )
            ])

        # Action buttons
        keyboard.extend([
            [
                InlineKeyboardButton("🗑️ Clear History", callback_data="history_clear"),
                InlineKeyboardButton("📊 Export", callback_data="history_export")
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_main")
            ]
        ])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def settings_menu(user_settings: Dict) -> InlineKeyboardMarkup:
        """Settings configuration keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(
                    f"📊 Results per page: {user_settings.get('results_per_page', 5)}",
                    callback_data="setting_results_per_page"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🔍 Default search: {user_settings.get('default_search', 'All platforms')}",
                    callback_data="setting_default_search"
                )
            ],
            [
                InlineKeyboardButton(
                    f"📱 Notifications: {'✅' if user_settings.get('notifications', True) else '❌'}",
                    callback_data="setting_notifications"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🎨 Theme: {user_settings.get('theme', 'Default')}",
                    callback_data="setting_theme"
                )
            ],
            [
                InlineKeyboardButton("💾 Export Data", callback_data="setting_export"),
                InlineKeyboardButton("🗑️ Reset All", callback_data="setting_reset")
            ],
            [
                InlineKeyboardButton("« Back to Menu", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation_dialog(action: str, item_id: str = "") -> InlineKeyboardMarkup:
        """Confirmation dialog keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}_{item_id}"),
                InlineKeyboardButton("❌ No", callback_data=f"cancel_{action}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def progress_indicator() -> InlineKeyboardMarkup:
        """Progress indicator keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("⏹️ Cancel Search", callback_data="cancel_search")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def _get_platform_emoji(url: str) -> str:
        """Get emoji for platform based on URL"""
        url_lower = url.lower()
        if "drive.google.com" in url_lower:
            return "📁"
        elif "mediafire.com" in url_lower:
            return "💾"
        elif "mega.nz" in url_lower:
            return "☁️"
        elif "dropbox.com" in url_lower:
            return "📦"
        elif "onedrive.live.com" in url_lower:
            return "🌐"
        else:
            return "🔗"

    @staticmethod
    def back_button() -> InlineKeyboardMarkup:
        """Simple back button"""
        keyboard = [
            [InlineKeyboardButton("« Back", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
