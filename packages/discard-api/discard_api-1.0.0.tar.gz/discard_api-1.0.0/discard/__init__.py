"""
discard/__init__.py - Complete Discard API SDK
"""

from .client import DiscardClient
from .categories_part2 import *
from .categories_part3 import *
from .categories_part4 import *

from typing import Dict, Any, Optional


class DiscardAPI:
    """Complete Discard API SDK with all categories"""

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize Discard API SDK

        Args:
            api_key: Your API key
            **kwargs: Additional arguments for DiscardClient
        """
        self.client = DiscardClient(api_key, **kwargs)

        # Initialize all category modules
        self.islam = IslamAPI(self.client)
        self.ai = AIAPI(self.client)
        self.anime = AnimeAPI(self.client)
        self.apps = AppsAPI(self.client)
        self.chatbots = ChatbotsAPI(self.client)
        self.canvas = CanvasAPI(self.client)
        self.codec = CodecAPI(self.client)
        self.shortener = ShortenerAPI(self.client)
        self.audiodb = AudioDBAPI(self.client)
        self.quotes = QuotesAPI(self.client)
        self.downloads = DownloadsAPI(self.client)
        self.imagemakers = ImageMakersAPI(self.client)
        self.music = MusicAPI(self.client)
        self.jokes = JokesAPI(self.client)
        self.images = ImagesAPI(self.client)
        self.facts = FactsAPI(self.client)
        self.faker = FakerAPI(self.client)
        self.fakestore = FakeStoreAPI(self.client)
        self.news = NewsAPI(self.client)
        self.stalker = StalkerAPI(self.client)
        self.search = SearchAPI(self.client)
        self.tools = ToolsAPI(self.client)
        self.memes = MemesAPI(self.client)
        self.time = TimeAPI(self.client)
        self.photooxy = PhotoOxyAPI(self.client)
        self.ephoto360 = Ephoto360API(self.client)
        self.imageprocess = ImageProcessAPI(self.client)
        self.information = InformationAPI(self.client)
        self.tempmail = TempMailAPI(self.client)
        self.uploads = UploadsAPI(self.client)
        self.random = RandomAPI(self.client)


# ===== ISLAMIC API =====
class IslamAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def quran_surah(self, surah: str) -> Dict[str, Any]:
        """Get specific surah by name, pages in images and mp3"""
        return self.client._make_request("GET", "/api/dl/surah", {"surah": surah})

    def sahih_hadith(self, book: str, number: str) -> Dict[str, Any]:
        """Get hadith by book name and hadith number"""
        return self.client._make_request(
            "GET", "/api/get/hadith", {"book": book, "number": number}
        )

    def prayer_timing(self, city: str) -> Dict[str, Any]:
        """Get daily prayer timings for specific city"""
        return self.client._make_request("GET", "/api/prayer/timing", {"city": city})

    def quran(self, surah: str, ayat: str) -> Dict[str, Any]:
        """Get specific surah/ayat in arabic and mp3"""
        return self.client._make_request(
            "GET", "/api/islamic/quran", {"surah": surah, "ayat": ayat}
        )

    def hadit(self, book: str, number: str) -> Dict[str, Any]:
        """Get specific hadith from specific book"""
        return self.client._make_request(
            "GET", "/api/islamic/hadit", {"book": book, "number": number}
        )

    def tahlil(self) -> Dict[str, Any]:
        """Get Tahlil"""
        return self.client._make_request("GET", "/api/islamic/tahlil")

    def wirid(self) -> Dict[str, Any]:
        """Get Wirid"""
        return self.client._make_request("GET", "/api/islamic/wirid")

    def dua_harian(self) -> Dict[str, Any]:
        """Get Dua"""
        return self.client._make_request("GET", "/api/islamic/dua")

    def ayat_kursi(self) -> Dict[str, Any]:
        """Get Ayat-Ul-Kursi"""
        return self.client._make_request("GET", "/api/islamic/ayatkursi")

    def search_books(self) -> Dict[str, Any]:
        """Search Islamic Books"""
        return self.client._make_request("GET", "/api/get/books")

    def get_books(self, category: str) -> Dict[str, Any]:
        """Download Available Islamic Books by providing category"""
        return self.client._make_request(
            "GET", "/api/get/books", {"category": category}
        )


# ===== AI API =====
class AIAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def gemini_pro(self, text: str) -> Dict[str, Any]:
        """Advanced AI model for complex reasoning and problem-solving tasks"""
        return self.client._make_request("GET", "/api/gemini/pro", {"text": text})

    def gemini_flash(self, text: str) -> Dict[str, Any]:
        """Top-tier model with strong reasoning and multimodal capabilities"""
        return self.client._make_request("GET", "/api/gemini/flash", {"text": text})

    def google_gemma(self, text: str) -> Dict[str, Any]:
        """Google's model with strong reasoning and multimodal capabilities"""
        return self.client._make_request("GET", "/api/gemini/gemma", {"text": text})

    def gemini_embed(self, text: str) -> Dict[str, Any]:
        """Embeddings turn text into math you can use to compare, search, and categorize"""
        return self.client._make_request("GET", "/api/gemini/embed", {"text": text})

    def llama_ai(self, text: str) -> Dict[str, Any]:
        """Meta's large language model for conversational AI and text completion"""
        return self.client._make_request("GET", "/api/ai/llama", {"text": text})

    def mythomax(self, text: str) -> Dict[str, Any]:
        """Creative AI model specialized in storytelling and imaginative content"""
        return self.client._make_request("GET", "/api/ai/mythomax", {"text": text})

    def mistral_ai(self, text: str) -> Dict[str, Any]:
        """Mistral AI model for efficient text processing"""
        return self.client._make_request("GET", "/api/ai/mistral", {"text": text})

    def qwen_coder(self, text: str) -> Dict[str, Any]:
        """Optimized for programming tasks, code generation, and developer assistance"""
        return self.client._make_request("GET", "/api/ai/qwen", {"text": text})

    def kimi_ai(self, text: str) -> Dict[str, Any]:
        """Model for general-purpose natural language understanding and generation"""
        return self.client._make_request("GET", "/api/ai/kimi", {"text": text})

    def gemma_ai(self, text: str) -> Dict[str, Any]:
        """Model for general-purpose natural language understanding and generation"""
        return self.client._make_request("GET", "/api/ai/gemma", {"text": text})

    def flux_schnell(self, text: str) -> Dict[str, Any]:
        """High-speed image-generation model for rapid visual outputs"""
        return self.client._make_request("GET", "/api/imagen/schnell", {"text": text})

    def flux_dev(self, text: str) -> Dict[str, Any]:
        """Image-generation model optimized for detailed and creative visuals"""
        return self.client._make_request("GET", "/api/imagen/flux", {"text": text})

    def stable_diffusion(self, text: str) -> Dict[str, Any]:
        """Popular AI model for generating high-quality, realistic images from text prompts"""
        return self.client._make_request("GET", "/api/imagen/diffusion", {"text": text})

    def black_forest(self, text: str) -> Dict[str, Any]:
        """AI image-generation model focused on cinematic aesthetics"""
        return self.client._make_request("GET", "/api/imagen/sdxlb", {"text": text})

    def dalle(self, text: str) -> Dict[str, Any]:
        """Dell-E AI image-generation model"""
        return self.client._make_request("GET", "/api/imagen/dalle", {"text": text})


# ===== ANIME API =====
class AnimeAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def anime_nom(self) -> Dict[str, Any]:
        """Get anime nom image"""
        return self.client._make_request("GET", "/api/anime/nom")

    def anime_poke(self) -> Dict[str, Any]:
        """Get anime poke image"""
        return self.client._make_request("GET", "/api/anime/poke")

    def anime_cry(self) -> Dict[str, Any]:
        """Get anime cry image"""
        return self.client._make_request("GET", "/api/anime/cry")

    def anime_kiss(self) -> Dict[str, Any]:
        """Get anime kiss image"""
        return self.client._make_request("GET", "/api/anime/nom")

    def anime_pat(self) -> Dict[str, Any]:
        """Get anime pat image"""
        return self.client._make_request("GET", "/api/anime/pat")

    def anime_hug(self) -> Dict[str, Any]:
        """Get anime hug image"""
        return self.client._make_request("GET", "/api/anime/hug")

    def anime_wink(self) -> Dict[str, Any]:
        """Get anime wink image"""
        return self.client._make_request("GET", "/api/anime/nom")

    def anime_face(self) -> Dict[str, Any]:
        """Get anime face image"""
        return self.client._make_request("GET", "/api/anime/nom")


# ===== APPS API =====
class AppsAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def android_one_search(self, query: str) -> Dict[str, Any]:
        """Search mod apk from Android 1"""
        return self.client._make_request(
            "GET", "/api/apk/search/android1", {"query": query}
        )

    def android_one_download(self, url: str) -> Dict[str, Any]:
        """Download mod apks from Android 1"""
        return self.client._make_request("GET", "/api/apk/dl/android1", {"url": url})

    def app_store(self, id: str) -> Dict[str, Any]:
        """Get detailed information about appstore app"""
        return self.client._make_request("GET", "/api/apk/search/appstore", {"id": id})

    def apk_mirror_search(self, query: str) -> Dict[str, Any]:
        """Search mod apk from ApkMirror"""
        return self.client._make_request(
            "GET", "/api/apk/search/apkmirror", {"query": query}
        )

    def apk_mirror_download(self, url: str) -> Dict[str, Any]:
        """Download mod apk from ApkMirror"""
        return self.client._make_request("GET", "/api/apk/dl/apkmirror", {"url": url})

    def apk_pure_search(self, query: str) -> Dict[str, Any]:
        """Search for mod app from apk pure"""
        return self.client._make_request(
            "GET", "/api/apk/search/apkpure", {"query": query}
        )

    def apk_pure_download(self, url: str) -> Dict[str, Any]:
        """Download mod app from apk pure"""
        return self.client._make_request("GET", "/api/apk/dl/apkpure", {"url": url})

    def mod_combo_search(self, query: str) -> Dict[str, Any]:
        """Search mod details from mod combo"""
        return self.client._make_request(
            "GET", "/api/apk/search/modcombo", {"query": query}
        )

    def play_store_search(self, query: str) -> Dict[str, Any]:
        """Search for apps on playstore"""
        return self.client._make_request(
            "GET", "/api/apk/search/playstore", {"query": query}
        )

    def play_store_download(self, url: str) -> Dict[str, Any]:
        """Download apps from playstore"""
        return self.client._make_request("GET", "/api/apk/dl/playstore", {"url": url})

    def rexdl_search(self, query: str) -> Dict[str, Any]:
        """Search for apps from Rexdl"""
        return self.client._make_request(
            "GET", "/api/apk/search/rexdl", {"query": query}
        )

    def rexdl_download(self, url: str) -> Dict[str, Any]:
        """Download app from Rexdl"""
        return self.client._make_request("GET", "/api/apk/dl/rexdl", {"url": url})

    def steam_app(self, query: str) -> Dict[str, Any]:
        """Get details of Steam game/app"""
        return self.client._make_request(
            "GET", "/api/apk/search/steam", {"query": query}
        )

    def happy_mod(self, query: str) -> Dict[str, Any]:
        """Search mod apks from happy mod"""
        return self.client._make_request(
            "GET", "/api/apk/search/happymod", {"query": query}
        )

    def sfile_mobi(self, query: str) -> Dict[str, Any]:
        """Search apks from SFile Mobi"""
        return self.client._make_request(
            "GET", "/api/apk/search/sfile", {"query": query}
        )
