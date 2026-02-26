"""
Enhanced search module with multiple sources and improved result processing
Handles course link searching with progress tracking and error handling
"""

import asyncio
import httpx
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import re
from datetime import datetime

from bot.config import Config

logger = logging.getLogger(__name__)

class SearchEngine:
    """Enhanced search engine with multiple sources and better filtering"""

    def __init__(self):
        self.config = Config()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def search_courses(self, query: str, platform: str = None,
                           max_results: int = None, progress_callback=None) -> Tuple[List[Dict], int]:
        """
        Search for course links with progress tracking

        Args:
            query: Search query
            platform: Specific platform to search (optional)
            max_results: Maximum number of results
            progress_callback: Callback for progress updates

        Returns:
            Tuple of (results_list, total_found)
        """
        if max_results is None:
            max_results = self.config.MAX_RESULTS_PER_PAGE

        try:
            # Update progress
            if progress_callback:
                await progress_callback("🔍 Preparing search...")

            # Build search query
            search_query = self._build_search_query(query, platform)

            if progress_callback:
                await progress_callback("📡 Searching platforms...")

            # Perform search
            results = await self._perform_search(search_query, max_results, progress_callback)

            if progress_callback:
                await progress_callback("🔄 Processing results...")

            # Filter and enhance results
            filtered_results = self._filter_and_enhance_results(results)

            if progress_callback:
                await progress_callback("✅ Search completed!")

            return filtered_results[:max_results], len(filtered_results)

        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            if progress_callback:
                await progress_callback("❌ Search failed")
            return [], 0

    def _build_search_query(self, query: str, platform: str = None) -> str:
        """Build optimized search query"""
        # Clean and enhance query
        clean_query = re.sub(r'[^\w\s]', ' ', query.strip())
        clean_query = ' '.join(clean_query.split())  # Remove extra spaces

        # Add common course-related terms
        course_terms = ["course", "tutorial", "lessons", "training", "class"]
        if not any(term in clean_query.lower() for term in course_terms):
            clean_query += " course"

        # Add file type indicators
        file_indicators = ["download", "files", "resources", "materials"]
        if not any(indicator in clean_query.lower() for indicator in file_indicators):
            clean_query += " download"

        # Platform-specific query building
        if platform:
            if platform in self.config.SUPPORTED_PLATFORMS:
                return f'{clean_query} site:{platform}'

        # Multi-platform search
        platform_queries = []
        for p in self.config.SUPPORTED_PLATFORMS:
            platform_queries.append(f"site:{p}")

        platform_string = " OR ".join(platform_queries)
        return f'{clean_query} ({platform_string})'

    async def _perform_search(self, query: str, max_results: int,
                            progress_callback=None) -> List[Dict]:
        """Perform the actual search using SERPAPI"""
        all_results = []

        try:
            # Search parameters
            params = {
                "q": query,
                "engine": "google",
                "api_key": self.config.SERPAPI_KEY,
                "num": min(max_results * 2, 20),  # Get more results for filtering
                "safe": "off",
                "gl": "us",
                "hl": "en"
            }

            if progress_callback:
                await progress_callback("🌐 Querying search engine...")

            # Make search request using httpx
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                response = await client.get(
                    "https://serpapi.com/search",
                    params=params
                )
                response.raise_for_status()
                data = response.json()

            if progress_callback:
                await progress_callback("📋 Parsing results...")

            # Process organic results
            for result in data.get("organic_results", []):
                processed_result = self._process_search_result(result)
                if processed_result:
                    all_results.append(processed_result)

            # Also check related searches and people also ask
            await self._process_additional_results(data, all_results, progress_callback)

        except httpx.HTTPError as e:
            logger.error(f"Search API request failed: {e}")
            raise Exception(f"Search service unavailable: {e}")
        except Exception as e:
            logger.error(f"Search processing failed: {e}")
            raise Exception(f"Search failed: {e}")

        return all_results

    def _process_search_result(self, result: Dict) -> Optional[Dict]:
        """Process individual search result"""
        try:
            link = result.get("link", "")
            title = result.get("title", "")
            snippet = result.get("snippet", "")

            # Validate link
            if not link or not self.config.is_valid_platform(link):
                return None

            # Extract additional metadata
            platform = self._identify_platform(link)
            file_info = self._extract_file_info(link, title, snippet)

            return {
                "title": title.strip(),
                "link": link,
                "snippet": snippet.strip(),
                "platform": platform,
                "file_info": file_info,
                "quality_score": self._calculate_quality_score(title, snippet, link),
                "found_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to process result: {e}")
            return None

    async def _process_additional_results(self, data: Dict, all_results: List[Dict],
                                        progress_callback=None):
        """Process additional result sections"""
        try:
            # Process "People also ask" section
            paa_results = data.get("people_also_ask", [])
            for paa in paa_results[:3]:  # Limit to avoid spam
                if "link" in paa and self.config.is_valid_platform(paa["link"]):
                    processed = self._process_search_result(paa)
                    if processed:
                        all_results.append(processed)

            # Process related searches that might have direct links
            related_searches = data.get("related_searches", [])
            for related in related_searches[:2]:
                # This would require additional API calls, so we skip for now
                pass

        except Exception as e:
            logger.error(f"Failed to process additional results: {e}")

    def _filter_and_enhance_results(self, results: List[Dict]) -> List[Dict]:
        """Filter and enhance search results"""
        filtered_results = []
        seen_links = set()

        for result in results:
            link = result.get("link", "")

            # Skip duplicates
            if link in seen_links:
                continue
            seen_links.add(link)

            # Quality filtering
            if result.get("quality_score", 0) < 3:
                continue

            # Enhanced metadata
            result["display_title"] = self._create_display_title(result)
            result["platform_emoji"] = self._get_platform_emoji(result["platform"])
            result["estimated_size"] = self._estimate_content_size(result)

            filtered_results.append(result)

        # Sort by quality score
        filtered_results.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

        return filtered_results

    def _identify_platform(self, url: str) -> str:
        """Identify platform from URL"""
        url_lower = url.lower()

        if "drive.google.com" in url_lower:
            return "Google Drive"
        elif "mediafire.com" in url_lower:
            return "MediaFire"
        elif "mega.nz" in url_lower:
            return "Mega"
        elif "dropbox.com" in url_lower:
            return "Dropbox"
        elif "onedrive.live.com" in url_lower:
            return "OneDrive"
        else:
            return "Unknown"

    def _extract_file_info(self, link: str, title: str, snippet: str) -> Dict:
        """Extract file information from link and metadata"""
        info = {
            "type": "unknown",
            "size": None,
            "format": None
        }

        # Extract file type from URL or title
        file_extensions = re.findall(r'\.(zip|rar|7z|tar|gz|mp4|mkv|avi|pdf|epub|mobi)(?:\s|$|[?&#])',
                                   f"{link} {title} {snippet}", re.IGNORECASE)
        if file_extensions:
            info["format"] = file_extensions[0].lower()
            info["type"] = self._categorize_file_type(info["format"])

        # Extract size information
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(MB|GB|TB)', snippet, re.IGNORECASE)
        if size_match:
            info["size"] = f"{size_match.group(1)} {size_match.group(2).upper()}"

        return info

    def _categorize_file_type(self, extension: str) -> str:
        """Categorize file type based on extension"""
        video_formats = ["mp4", "mkv", "avi", "mov", "wmv", "flv"]
        archive_formats = ["zip", "rar", "7z", "tar", "gz"]
        document_formats = ["pdf", "epub", "mobi", "doc", "docx"]

        if extension in video_formats:
            return "video"
        elif extension in archive_formats:
            return "archive"
        elif extension in document_formats:
            return "document"
        else:
            return "unknown"

    def _calculate_quality_score(self, title: str, snippet: str, link: str) -> int:
        """Calculate quality score for result ranking"""
        score = 5  # Base score

        # Title quality indicators
        positive_title_terms = ["course", "tutorial", "complete", "full", "master", "class", "training"]
        negative_title_terms = ["preview", "sample", "demo", "trailer"]

        title_lower = title.lower()
        for term in positive_title_terms:
            if term in title_lower:
                score += 2

        for term in negative_title_terms:
            if term in title_lower:
                score -= 3

        # Snippet quality indicators
        snippet_lower = snippet.lower()
        if "download" in snippet_lower:
            score += 1
        if "free" in snippet_lower:
            score += 1
        if any(size in snippet_lower for size in ["gb", "mb"]):
            score += 2

        # Link quality (shorter, cleaner links often better)
        if len(link) < 100:
            score += 1

        # Platform preferences
        if "drive.google.com" in link:
            score += 2
        elif "mega.nz" in link:
            score += 1

        return max(0, min(10, score))  # Clamp between 0-10

    def _create_display_title(self, result: Dict) -> str:
        """Create enhanced display title"""
        title = result.get("title", "Untitled")
        platform = result.get("platform", "Unknown")
        file_info = result.get("file_info", {})

        # Add file size if available
        if file_info.get("size"):
            title += f" ({file_info['size']})"

        # Add file type indicator
        if file_info.get("format"):
            title += f" [{file_info['format'].upper()}]"

        return title

    def _get_platform_emoji(self, platform: str) -> str:
        """Get emoji for platform"""
        emoji_map = {
            "Google Drive": "📁",
            "MediaFire": "💾",
            "Mega": "☁️",
            "Dropbox": "📦",
            "OneDrive": "🌐"
        }
        return emoji_map.get(platform, "🔗")

    def _estimate_content_size(self, result: Dict) -> str:
        """Estimate content size category"""
        snippet = result.get("snippet", "").lower()

        if "gb" in snippet:
            return "Large (1GB+)"
        elif "mb" in snippet:
            return "Medium (1-999MB)"
        else:
            return "Unknown size"

class SearchProgress:
    """Helper class for managing search progress"""

    def __init__(self, message, config: Config):
        self.message = message
        self.config = config
        self.current_frame = 0
        self.is_active = True

    async def update(self, text: str):
        """Update progress message"""
        if not self.is_active:
            return

        try:
            emoji = self.config.PROGRESS_FRAMES[self.current_frame % len(self.config.PROGRESS_FRAMES)]
            await self.message.edit_text(f"{emoji} {text}")
            self.current_frame += 1

            # Small delay for visual effect
            await asyncio.sleep(0.3)

        except Exception as e:
            logger.error(f"Progress update failed: {e}")

    def stop(self):
        """Stop progress updates"""
        self.is_active = False
