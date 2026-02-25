"""
Configuration module for the Enhanced Course Bot
Handles environment variables and bot settings
"""

import os
from typing import List

class Config:
    """Configuration class for bot settings"""

    def __init__(self):
        # Bot credentials
        self.BOT_TOKEN = os.getenv(
            "BOT_TOKEN",
            "YOUR_BOT_TOKEN_HERE"
        )

        # Search API credentials
        self.SERPAPI_KEY = os.getenv(
            "SERPAPI_KEY",
            "YOUR_SERPAPI_KEY_HERE"
        )

        # Developer info (encoded)
        import base64
        self.DEVELOPER_TELEGRAM = base64.b64decode("QE5HWVQ3NzdHRw==").decode('utf-8')
        self.CHANNEL_LINK = base64.b64decode("aHR0cHM6Ly90Lm1lLytGTnN0Tllfb29WMWxZemRs").decode('utf-8')

        # Search settings
        self.MAX_RESULTS_PER_PAGE = 5
        self.MAX_SEARCH_HISTORY = 20
        self.MAX_FAVORITES = 50

        # Supported platforms
        self.SUPPORTED_PLATFORMS = [
            "drive.google.com",
            "mediafire.com",
            "mega.nz",
            "dropbox.com",
            "onedrive.live.com"
        ]

        # Search engines
        self.SEARCH_ENGINES = ["google", "bing", "duckduckgo"]

        # Rate limiting
        self.RATE_LIMIT_SEARCHES = 10  # per minute
        self.RATE_LIMIT_WINDOW = 60    # seconds

        # Database settings
        self.DATABASE_FILE = "course_bot.db"

        # Progress animation settings
        self.PROGRESS_FRAMES = ["⏳", "⌛", "🔍", "📚", "🎯"]
        self.PROGRESS_DELAY = 0.5  # seconds

    def get_search_query_template(self, platform: str = None) -> str:
        """Get search query template for specific platform"""
        if platform:
            return f"{{query}} site:{platform}"
        else:
            platforms = " OR ".join([f"site:{p}" for p in self.SUPPORTED_PLATFORMS])
            return f"{{query}} ({platforms})"

    def is_valid_platform(self, url: str) -> bool:
        """Check if URL belongs to supported platform"""
        return any(platform in url.lower() for platform in self.SUPPORTED_PLATFORMS)
