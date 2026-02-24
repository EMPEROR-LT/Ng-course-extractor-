"""
Utility functions for the Enhanced Course Bot
Contains helper functions for formatting, validation, and common operations
"""

import re
import html
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse
import hashlib

logger = logging.getLogger(__name__)

class MessageFormatter:
    """Class for formatting bot messages with enhanced styling"""

    @staticmethod
    def format_welcome_message(user_name: str) -> str:
        """Format welcome message for new users"""
        from bot.config import Config
        config = Config()
        return f"""
```
🅲🅾🆄🆁🆂🅴 🅵🅸🅽🅳🅴🆁 🅱🅾🆃
✧═══════════════════════════════✧
```

🎓 **𝗪𝗲𝗹𝗰𝗼𝗺𝗲 {user_name}!** [`[ϟ]`]({config.CHANNEL_LINK})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🔥 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:**
```
🔍 𝐒𝐦𝐚𝐫𝐭 𝐒𝐞𝐚𝐫𝐜𝐡    - Multi-platform finder
⭐ 𝐅𝐚𝐯𝐨𝐫𝐢𝐭𝐞𝐬       - Save best courses
📚 𝐇𝐢𝐬𝐭𝐨𝐫𝐲         - Track searches
⚙️ 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬        - Custom experience
📊 𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬        - Real-time updates
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**𝗤𝘂𝗶𝗰𝗸 𝗦𝘁𝗮𝗿𝘁 𝗚𝘂𝗶𝗱𝗲:**
`💡` Type any course name to search
`💡` Use /help for detailed commands
`💡` Try the menu buttons below

**𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿:** [{config.DEVELOPER_TELEGRAM}](https://t.me/{config.DEVELOPER_TELEGRAM[1:]})

```
✧═══════ 𝗟𝗘𝗧'𝗦 𝗙𝗜𝗡𝗗 𝗖𝗢𝗨𝗥𝗦𝗘𝗦! ═══════✧
```
"""

    @staticmethod
    def format_help_message() -> str:
        """Format comprehensive help message"""
        from bot.config import Config
        config = Config()
        return f"""
```
🅷🅴🅻🅿 & 🅶🆄🅸🅳🅴
✧═══════════════════════════════✧
```

📖 **𝗖𝗼𝘂𝗿𝘀𝗲 𝗕𝗼𝘁 𝗛𝗲𝗹𝗽 𝗖𝗲𝗻𝘁𝗲𝗿** [`[ϟ]`]({config.CHANNEL_LINK})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🔍 𝗦𝗲𝗮𝗿𝗰𝗵 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:**
```
• Just type course name to start
• Example: "Python programming course"
```

**⚡ 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:**
```
/start     - Main menu
/help      - This help guide
/settings  - Your preferences
/history   - Search history
/favorites - Saved links
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🎯 𝗦𝗲𝗮𝗿𝗰𝗵 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:**
```
🔥 𝐐𝐮𝐢𝐜𝐤 𝐒𝐞𝐚𝐫𝐜𝐡    - All platforms
🎯 𝐏𝐥𝐚𝐭𝐟𝐨𝐫𝐦 𝐒𝐞𝐚𝐫𝐜𝐡 - Drive, MediaFire, Mega
🔧 𝐀𝐝𝐯𝐚𝐧𝐜𝐞𝐝 𝐒𝐞𝐚𝐫𝐜𝐡 - Filters & quality
📊 𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 𝐓𝐫𝐚𝐜𝐤  - Real-time updates
```

**⭐ 𝗙𝗮𝘃𝗼𝗿𝗶𝘁𝗲𝘀 𝗦𝘆𝘀𝘁𝗲𝗺:**
```
• Add results with ⭐ button
• Quick access from menu
• Export your collection
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💡 𝗣𝗿𝗼 𝗧𝗶𝗽𝘀:**
`🎯` Be specific with course names
`🎯` Use "complete course" in queries
`🎯` Check favorites regularly
`🎯` Use history for repeat searches

**𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿:** [{config.DEVELOPER_TELEGRAM}](https://t.me/{config.DEVELOPER_TELEGRAM[1:]})

```
✧═══════ 𝗛𝗔𝗣𝗣𝗬 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚! ═══════✧
```
"""

    @staticmethod
    def format_search_results(results: List[Dict], query: str,
                            page: int = 0, total_results: int = 0) -> str:
        """Format search results with enhanced display"""
        if not results:
            return f"""
```
✧═══════ SEARCH RESULTS ═══════✧
```

🔍 **Query:** `"{query}"` `[ϟ]`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ **No Results Found**

```
📌 Suggestions:
• Try different keywords
• Check spelling
• Use more general terms
• Try platform-specific search
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
✧═══════ TRY AGAIN! ═══════✧
```
"""

        header = f"""
```
✧═══════ SEARCH RESULTS ═══════✧
```

🔍 **Query:** `"{query}"` `[ϟ]`
📊 **Found:** `{total_results} results` (Page `{page + 1}`)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        results_text = ""
        for i, result in enumerate(results, 1):
            platform_emoji = result.get("platform_emoji", "🔗")
            title = result.get("display_title", result.get("title", "Untitled"))
            snippet = result.get("snippet", "")
            platform = result.get("platform", "Unknown")
            quality_score = result.get("quality_score", 0)

            # Truncate long titles and snippets
            if len(title) > 50:
                title = title[:47] + "..."
            if len(snippet) > 80:
                snippet = snippet[:77] + "..."

            quality_stars = "⭐" * min(quality_score // 2, 5)

            results_text += f"""
**`{i}.`** {platform_emoji} **{html.escape(title)}** `[ϟ]`
```
Platform: {platform} {quality_stars}
Info: {html.escape(snippet)}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        footer = """
**💡 Pro Tip:** `Click result for details` • `⭐ to save favorites`

```
✧═══════ HAPPY LEARNING! ═══════✧
```
"""

        return header + results_text + footer

    @staticmethod
    def format_result_details(result: Dict, index: int) -> str:
        """Format detailed view of a single result"""
        title = result.get("title", "Untitled")
        link = result.get("link", "")
        snippet = result.get("snippet", "")
        platform = result.get("platform", "Unknown")
        platform_emoji = result.get("platform_emoji", "🔗")
        file_info = result.get("file_info", {})
        quality_score = result.get("quality_score", 0)
        estimated_size = result.get("estimated_size", "Unknown")

        details = f"""
```
✧═══════ COURSE DETAILS ═══════✧
```

{platform_emoji} **{html.escape(title)}** `[ϟ]`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📱 Platform:** `{platform}`
**📊 Quality:** `{quality_score}/10` {"⭐" * min(quality_score // 2, 5)}
**📏 Size:** `{estimated_size}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📝 Description:**
```
{html.escape(snippet)}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🔗 Direct Link:**
```
{link}
```

"""

        # Add file information if available
        if file_info.get("format") or file_info.get("size") or file_info.get("type"):
            details += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n**📋 File Info:**\n```\n"

            if file_info.get("format"):
                details += f"Format: {file_info['format'].upper()}\n"

            if file_info.get("size"):
                details += f"Size: {file_info['size']}\n"

            if file_info.get("type"):
                details += f"Type: {file_info['type'].title()}\n"

            details += "```\n\n"

        details += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💡 Actions:** `Open` • `Save to Favorites` • `Share`

```
✧═══════ ENJOY LEARNING! ═══════✧
```"""

        return details

    @staticmethod
    def format_favorites_list(favorites: List[Dict], page: int = 0) -> str:
        """Format favorites list with pagination"""
        if not favorites:
            return """
```
✧═══════ YOUR FAVORITES ═══════✧
```

⭐ **No Favorites Yet!** `[ϟ]`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
📌 Benefits of Favorites:
• Quick access to saved links
• Organized collection
• Export functionality
• No search needed
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💡 Start searching and click ⭐ to save!**

```
✧═══════ HAPPY COLLECTING! ═══════✧
```
"""

        total_pages = (len(favorites) + 4) // 5
        start_idx = page * 5
        end_idx = min(start_idx + 5, len(favorites))

        header = f"""
```
✧═══════ YOUR FAVORITES ═══════✧
```

⭐ **Saved Collection** `[ϟ]`
📊 **Total:** `{len(favorites)} links` • **Page:** `{page + 1}/{total_pages}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        favorites_text = ""
        for i, fav in enumerate(favorites[start_idx:end_idx], start_idx + 1):
            platform_emoji = MessageFormatter._get_platform_emoji(fav.get('url', ''))
            title = fav.get('title', 'Untitled')
            platform = fav.get('platform', 'Unknown')
            added_date = fav.get('added_at', '')

            # Format date
            try:
                if added_date:
                    date_obj = datetime.fromisoformat(added_date.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%b %d')
                else:
                    formatted_date = "Unknown"
            except:
                formatted_date = "Unknown"

            if len(title) > 45:
                title = title[:42] + "..."

            favorites_text += f"""
**`{i}.`** {platform_emoji} **{html.escape(title)}** `[ϟ]`
```
Platform: {platform} • Added: {formatted_date}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        footer = """
**💡 Actions:** `Open Link` • `Remove from Favorites` • `Export All`

```
✧═══════ ENJOY YOUR COURSES! ═══════✧
```
"""

        return header + favorites_text + footer

    @staticmethod
    def format_search_history(history: List[Dict]) -> str:
        """Format search history display"""
        if not history:
            return """
```
✧═══════ SEARCH HISTORY ═══════✧
```

📚 **No History Yet!** `[ϟ]`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
📌 History Features:
• Quick re-search from history
• Result count tracking
• Date stamps
• Easy access to past queries
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💡 Start searching to build your history!**

```
✧═══════ SEARCH & DISCOVER! ═══════✧
```
"""

        header = f"""
```
✧═══════ SEARCH HISTORY ═══════✧
```

📚 **Your Search History** `[ϟ]`
📊 **Total Searches:** `{len(history)}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        history_text = ""
        for i, search in enumerate(history, 1):
            query = search.get('query', 'Unknown')
            results_count = search.get('results_count', 0)
            timestamp = search.get('timestamp', '')

            # Format timestamp
            try:
                if timestamp:
                    date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    if date_obj.date() == datetime.now().date():
                        formatted_time = date_obj.strftime('%H:%M')
                    else:
                        formatted_time = date_obj.strftime('%b %d')
                else:
                    formatted_time = "Unknown"
            except:
                formatted_time = "Unknown"

            if len(query) > 35:
                query = query[:32] + "..."

            results_emoji = "✅" if results_count > 0 else "❌"

            history_text += f"""
**`{i}.`** 🔍 **{html.escape(query)}** `[ϟ]`
```
Results: {results_count} • Time: {formatted_time} {results_emoji}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        footer = """
**💡 Actions:** `Click any search to run again` • `Export History`

```
✧═══════ SEARCH AGAIN! ═══════✧
```
"""

        return header + history_text + footer

    @staticmethod
    def export_favorites_text(favorites: List[Dict]) -> str:
        """Export favorites as formatted text"""
        if not favorites:
            return "No favorites to export."

        from datetime import datetime
        export_text = f"""
𝗖𝗼𝘂𝗿𝘀𝗲 𝗙𝗮𝘃𝗼𝗿𝗶𝘁𝗲𝘀 𝗘𝘅𝗽𝗼𝗿𝘁
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total items: {len(favorites)}

{'='*50}

"""

        for i, fav in enumerate(favorites, 1):
            export_text += f"""
{i}. {fav.get('title', 'Untitled')}
   Platform: {fav.get('platform', 'Unknown')}
   URL: {fav.get('url', '')}
   Added: {fav.get('added_at', 'Unknown')}

"""

        return export_text

    @staticmethod
    def format_settings_display(settings: Dict) -> str:
        """Format current settings display"""
        return f"""
```
✧═══════ YOUR SETTINGS ═══════✧
```

⚙️ **Bot Configuration** `[ϟ]`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📊 Search Preferences:**
```
Results per page: {settings.get('results_per_page', 5)}
Default search: {settings.get('default_search', 'All platforms')}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🎨 Interface:**
```
Theme: {settings.get('theme', 'Default')}
Notifications: {'Enabled' if settings.get('notifications', True) else 'Disabled'}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📱 Advanced:**
```
Auto-save searches: {'Yes' if settings.get('auto_save', True) else 'No'}
Show quality scores: {'Yes' if settings.get('show_scores', True) else 'No'}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💡 Tip:** `Click any setting to modify it!`

```
✧═══════ CUSTOMIZE & ENJOY! ═══════✧
```
"""

    @staticmethod
    def format_error_message(error_type: str, details: str = "") -> str:
        """Format error messages with helpful information"""
        error_messages = {
            "search_failed": "🔍 **Search Failed**\n\nThe search service is temporarily unavailable. Please try again in a few moments.",
            "rate_limit": "⏰ **Rate Limit Exceeded**\n\nYou've made too many searches recently. Please wait a moment before searching again.",
            "invalid_query": "❓ **Invalid Query**\n\nPlease enter a valid course name to search for.",
            "no_results": "📭 **No Results Found**\n\nTry using different keywords or check your spelling.",
            "api_error": "🔧 **Service Error**\n\nOur search service is experiencing issues. Please try again later.",
            "network_error": "🌐 **Network Error**\n\nPlease check your connection and try again."
        }

        base_message = error_messages.get(error_type, "❌ **An error occurred**\n\nPlease try again.")

        if details:
            base_message += f"\n\n**Details:** {details}"

        base_message += "\n\n💡 **Tip:** If the problem persists, try using the /help command for guidance."

        return base_message

    @staticmethod
    def format_success_message(action: str, details: str = "") -> str:
        """Format success messages"""
        success_messages = {
            "added_favorite": "⭐ **Added to Favorites!**\n\nThe link has been saved to your favorites collection.",
            "removed_favorite": "🗑️ **Removed from Favorites**\n\nThe link has been removed from your collection.",
            "settings_updated": "⚙️ **Settings Updated**\n\nYour preferences have been saved successfully.",
            "history_cleared": "🗑️ **History Cleared**\n\nYour search history has been cleared.",
            "data_exported": "📤 **Data Exported**\n\nYour data has been prepared for export."
        }

        base_message = success_messages.get(action, "✅ **Success!**\n\nThe action was completed successfully.")

        if details:
            base_message += f"\n\n{details}"

        return base_message

    @staticmethod
    def _get_platform_emoji(url: str) -> str:
        """Get platform emoji from URL"""
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

class Validator:
    """Input validation utilities"""

    @staticmethod
    def is_valid_search_query(query: str) -> bool:
        """Validate search query"""
        if not query or not query.strip():
            return False

        # Check minimum length
        if len(query.strip()) < 2:
            return False

        # Check for valid characters (allow unicode for international course names)
        if not re.match(r'^[\w\s\-\.\(\)\[\]]+$', query, re.UNICODE):
            return False

        return True

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        if not text:
            return ""

        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', text)

        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200]

        return sanitized.strip()

class RateLimiter:
    """Simple rate limiting utility"""

    def __init__(self):
        self.requests = {}

    def is_allowed(self, user_id: int, limit: int = 10, window: int = 60) -> bool:
        """Check if user is within rate limits"""
        now = datetime.now()

        if user_id not in self.requests:
            self.requests[user_id] = []

        # Clean old requests
        cutoff = now - timedelta(seconds=window)
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[user_id]) >= limit:
            return False

        # Add current request
        self.requests[user_id].append(now)
        return True

class TextUtils:
    """Text processing utilities"""

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text with suffix"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extract keywords from text"""
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}

        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter out stop words and short words
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        return list(set(keywords))  # Remove duplicates

    @staticmethod
    def create_fingerprint(text: str) -> str:
        """Create a fingerprint for text deduplication"""
        normalized = re.sub(r'\W+', '', text.lower())
        return hashlib.md5(normalized.encode()).hexdigest()

class ExportUtils:
    """Data export utilities"""

    @staticmethod
    def export_favorites_text(favorites: List[Dict]) -> str:
        """Export favorites as formatted text"""
        if not favorites:
            return "No favorites to export."

        export_text = f"""
📚 Course Favorites Export
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total items: {len(favorites)}

{"="*50}

"""

        for i, fav in enumerate(favorites, 1):
            export_text += f"""
{i}. {fav.get('title', 'Untitled')}
   Platform: {fav.get('platform', 'Unknown')}
   URL: {fav.get('url', 'No URL')}
   Added: {fav.get('added_at', 'Unknown date')}

"""

        return export_text

    @staticmethod
    def export_history_text(history: List[Dict]) -> str:
        """Export search history as formatted text"""
        if not history:
            return "No search history to export."

        export_text = f"""
🔍 Search History Export
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total searches: {len(history)}

{"="*50}

"""

        for i, search in enumerate(history, 1):
            export_text += f"""
{i}. Query: "{search.get('query', 'Unknown')}"
   Results found: {search.get('results_count', 0)}
   Date: {search.get('timestamp', 'Unknown')}

"""

        return export_text
