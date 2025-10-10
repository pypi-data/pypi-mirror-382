"""
discard/categories_part4.py - Final API categories
"""

from typing import Dict, Any, Optional, BinaryIO, List
from .client import DiscardClient


# ===== FAKESTORE API =====
class FakeStoreAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def add_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new product"""
        return self.client._make_request(
            "POST", "/api/store/add/products", json_data=product_data
        )

    def delete_product(self, id: str) -> Dict[str, Any]:
        """Delete a product by ID"""
        return self.client._make_request(
            "DELETE", "/api/store/products", json_data={"id": id}
        )

    def update_product(self, id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product"""
        product_data["id"] = id
        return self.client._make_request(
            "PUT", "/api/store/products", json_data=product_data
        )

    def all_products(self) -> Dict[str, Any]:
        """Get all products"""
        return self.client._make_request("GET", "/api/store/products")

    def get_product(self, id: str) -> Dict[str, Any]:
        """Get product by ID"""
        return self.client._make_request("GET", "/api/store/product", {"id": id})

    def all_carts(self) -> Dict[str, Any]:
        """Get all carts"""
        return self.client._make_request("GET", "/api/store/carts")

    def add_cart(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new cart"""
        return self.client._make_request(
            "POST", "/api/store/carts", json_data=cart_data
        )

    def get_cart(self, id: str) -> Dict[str, Any]:
        """Get cart by ID"""
        return self.client._make_request("GET", "/api/store/cart", {"id": id})

    def update_cart(self, id: str, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a cart"""
        cart_data["id"] = id
        return self.client._make_request("PUT", "/api/store/carts", json_data=cart_data)

    def delete_cart(self, id: str) -> Dict[str, Any]:
        """Delete a cart"""
        return self.client._make_request(
            "DELETE", "/api/store/carts", json_data={"id": id}
        )

    def all_users(self) -> Dict[str, Any]:
        """Get all users"""
        return self.client._make_request("GET", "/api/store/users")

    def add_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new user"""
        return self.client._make_request(
            "POST", "/api/store/users", json_data=user_data
        )

    def get_user(self, id: str) -> Dict[str, Any]:
        """Get user by ID"""
        return self.client._make_request("GET", "/api/store/user", {"id": id})

    def update_user(self, id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user"""
        user_data["id"] = id
        return self.client._make_request(
            "PUT", "/api/store/products", json_data=user_data
        )

    def delete_user(self, id: str) -> Dict[str, Any]:
        """Delete a user"""
        return self.client._make_request(
            "DELETE", "/api/store/users", json_data={"id": id}
        )

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user"""
        return self.client._make_request(
            "POST",
            "/api/store/login",
            json_data={"username": username, "password": password},
        )


# ===== NEWS API =====
class NewsAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def aljazeera_english(self) -> Dict[str, Any]:
        """Fetch latest headlines from Aljazeera English News"""
        return self.client._make_request("GET", "/api/news/aljazeera")

    def aljazeera_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Aljazeera English News"""
        return self.client._make_request("GET", "/api/aljazeera/article", {"url": url})

    def aljazeera_arabic(self) -> Dict[str, Any]:
        """Fetch latest headlines from Aljazeera Arabic News"""
        return self.client._make_request("GET", "/api/news/aljazeera/ar")

    def aljazeera_arabic_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Aljazeera Arabic News"""
        return self.client._make_request(
            "GET", "/api/aljazeera/article/ar", {"url": url}
        )

    def trt_world(self) -> Dict[str, Any]:
        """Fetch latest headlines from TRT World News"""
        return self.client._make_request("GET", "/api/news/trt")

    def trt_article(self, url: str) -> Dict[str, Any]:
        """Get full article from TRT World"""
        return self.client._make_request("GET", "/api/trt/article", {"url": url})

    def trt_afrika(self) -> Dict[str, Any]:
        """Fetch latest headlines from TRT Afrika News"""
        return self.client._make_request("GET", "/api/news/trt/af")

    def trt_afrika_article(self, url: str) -> Dict[str, Any]:
        """Get full article from TRT Afrika"""
        return self.client._make_request("GET", "/api/trt/article/af", {"url": url})

    def sky_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from Sky News"""
        return self.client._make_request("GET", "/api/news/sky")

    def sky_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Sky News"""
        return self.client._make_request("GET", "/api/sky/article", {"url": url})

    def sky_sports(self, sport: str) -> Dict[str, Any]:
        """Fetch latest headlines from Sky Sports"""
        return self.client._make_request("GET", "/api/news/skysports", {"sport": sport})

    def sky_sports_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Sky Sports"""
        return self.client._make_request("GET", "/api/skysports/article", {"url": url})

    def fox_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from Fox News"""
        return self.client._make_request("GET", "/api/news/fox")

    def fox_media(self, url: str) -> Dict[str, Any]:
        """Get media url from Fox News article"""
        return self.client._make_request("GET", "/api/fox/media", {"url": url})

    def cgtn_world(self) -> Dict[str, Any]:
        """Fetch latest headlines from CGTN News"""
        return self.client._make_request("GET", "/api/news/cgtn")

    def cgtn_article(self, url: str) -> Dict[str, Any]:
        """Get full article from CGTN News"""
        return self.client._make_request("GET", "/api/cgtn/article", {"url": url})

    def cgtn_tech(self) -> Dict[str, Any]:
        """Fetch latest headlines from CGTN Tech News"""
        return self.client._make_request("GET", "/api/news/cgtn/tech")

    def cgtn_tech_article(self, url: str) -> Dict[str, Any]:
        """Get full article from CGTN Tech News"""
        return self.client._make_request("GET", "/api/cgtn/tech/article", {"url": url})

    def dawn_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from Dawn News English"""
        return self.client._make_request("GET", "/api/news/dawn")

    def dawn_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Dawn News"""
        return self.client._make_request("GET", "/api/dawn/article", {"url": url})

    def cnn_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from CNN World News"""
        return self.client._make_request("GET", "/api/news/cnn")

    def cnn_article(self, url: str) -> Dict[str, Any]:
        """Get full article from CNN News"""
        return self.client._make_request("GET", "/api/cnn/article", {"url": url})

    def guardian_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from The Guardian"""
        return self.client._make_request("GET", "/api/news/guardian")

    def guardian_article(self, url: str) -> Dict[str, Any]:
        """Get full article from The Guardian"""
        return self.client._make_request("GET", "/api/guardian/article", {"url": url})

    def tribune_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from Express Tribune"""
        return self.client._make_request("GET", "/api/news/tribune")

    def tribune_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Express Tribune"""
        return self.client._make_request("GET", "/api/tribune/article", {"url": url})

    def geo_urdu(self) -> Dict[str, Any]:
        """Fetch latest headlines from Geo News Urdu"""
        return self.client._make_request("GET", "/api/news/geo")

    def geo_urdu_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Geo News Urdu"""
        return self.client._make_request("GET", "/api/geo/article", {"url": url})

    def geo_english(self) -> Dict[str, Any]:
        """Fetch latest headlines from Geo News English"""
        return self.client._make_request("GET", "/api/news/geo/en")

    def geo_english_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Geo News English"""
        return self.client._make_request("GET", "/api/geo/en/article", {"url": url})

    def geo_super(self) -> Dict[str, Any]:
        """Fetch latest Sports headlines from Geo Super"""
        return self.client._make_request("GET", "/api/news/geosuper")

    def geo_super_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Geo Super"""
        return self.client._make_request("GET", "/api/geosuper/article", {"url": url})

    def gnn_english(self) -> Dict[str, Any]:
        """Fetch latest headlines from GNN News English"""
        return self.client._make_request("GET", "/api/news/gnn/en")

    def gnn_urdu(self) -> Dict[str, Any]:
        """Fetch latest headlines from GNN Urdu News"""
        return self.client._make_request("GET", "/api/news/gnn")

    def express_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from Express News Urdu"""
        return self.client._make_request("GET", "/api/news/express")

    def express_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Express News"""
        return self.client._make_request("GET", "/api/express/article", {"url": url})

    def neo_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from Neo News Urdu"""
        return self.client._make_request("GET", "/api/news/neo")

    def neo_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Neo News"""
        return self.client._make_request("GET", "/api/neo/article", {"url": url})

    def antara_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from Antara News Indonesia"""
        return self.client._make_request("GET", "/api/news/antara")

    def antara_article(self, url: str) -> Dict[str, Any]:
        """Get full article from Antara News"""
        return self.client._make_request("GET", "/api/antara/article", {"url": url})

    def detik_news(self) -> Dict[str, Any]:
        """Fetch latest headlines from Detik News Indonesia"""
        return self.client._make_request("GET", "/api/news/detik")

    def spaceflight_news(self, type: str) -> Dict[str, Any]:
        """Get articles from Spaceflight News"""
        return self.client._make_request("GET", "/api/news/spaceflight", {"type": type})

    def daily_news_china(self) -> Dict[str, Any]:
        """Get top headlines from Daily News China"""
        return self.client._make_request("GET", "/api/news/daily/cn")


# ===== STALKER API =====
class StalkerAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def genshin_stalk(self, id: str) -> Dict[str, Any]:
        """Get Genshin Impact player statistics"""
        return self.client._make_request("GET", "/api/stalk/genshin", {"id": id})

    def github_stalk(self, username: str) -> Dict[str, Any]:
        """Fetch GitHub user profile information"""
        return self.client._make_request(
            "GET", "/api/stalk/github", {"username": username}
        )

    def instagram_stalk(self, username: str) -> Dict[str, Any]:
        """Get Instagram user profile information"""
        return self.client._make_request(
            "GET", "/api/stalk/instagram", {"username": username}
        )

    def pinterest_stalk(self, username: str) -> Dict[str, Any]:
        """Get Pinterest user profile information"""
        return self.client._make_request(
            "GET", "/api/stalk/pinterest", {"username": username}
        )

    def threads_stalk(self, username: str) -> Dict[str, Any]:
        """Get Threads user profile information"""
        return self.client._make_request(
            "GET", "/api/stalk/threads", {"username": username}
        )

    def twitter_stalk(self, username: str) -> Dict[str, Any]:
        """Get Twitter user profile information"""
        return self.client._make_request(
            "GET", "/api/stalk/twitter", {"username": username}
        )

    def npm_stalk(self, pkg: str) -> Dict[str, Any]:
        """Get detailed information about NPM packages"""
        return self.client._make_request("GET", "/api/stalk/npm", {"pkg": pkg})

    def telegram_stalk(self, username: str) -> Dict[str, Any]:
        """Fetch Telegram channel/user information"""
        return self.client._make_request(
            "GET", "/api/stalk/telegram", {"username": username}
        )

    def tiktok_stalk(self, username: str) -> Dict[str, Any]:
        """Get TikTok user profile and video statistics"""
        return self.client._make_request(
            "GET", "/api/stalk/tiktok", {"username": username}
        )


# ===== SEARCH API =====
class SearchAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def google_search(self, query: str) -> Dict[str, Any]:
        """Get results from Google"""
        return self.client._make_request("GET", "/api/search/google", {"query": query})

    def bing_search(self, query: str) -> Dict[str, Any]:
        """Get results from Bing"""
        return self.client._make_request("GET", "/api/search/bing", {"query": query})

    def baidu_search(self) -> Dict[str, Any]:
        """Get hot topics from Baidu"""
        return self.client._make_request("GET", "/api/search/baidu")

    def weibo_search(self) -> Dict[str, Any]:
        """Get hot topics from Weibo"""
        return self.client._make_request("GET", "/api/search/weibo")

    def imgur_search(self, query: str) -> Dict[str, Any]:
        """Get gallery results from Imgur"""
        return self.client._make_request("GET", "/api/search/imgur", {"query": query})

    def search_360(self, query: str) -> Dict[str, Any]:
        """Get image result from 360"""
        return self.client._make_request("GET", "/api/search/360", {"query": query})

    def time_search(self, place: str) -> Dict[str, Any]:
        """Get detailed time info of any country or city"""
        return self.client._make_request("GET", "/api/search/time", {"place": place})

    def movies_search(self, query: str) -> Dict[str, Any]:
        """Search for movies"""
        return self.client._make_request("GET", "/api/search/tmdb", {"query": query})

    def flicker_search(self, query: str) -> Dict[str, Any]:
        """Search Flickr images"""
        return self.client._make_request("GET", "/api/search/flicker", {"query": query})

    def itunes_search(self, query: str) -> Dict[str, Any]:
        """Search iTunes"""
        return self.client._make_request("GET", "/api/search/itunes", {"query": query})

    def wattpad_search(self, query: str) -> Dict[str, Any]:
        """Search Wattpad"""
        return self.client._make_request("GET", "/api/search/wattpad", {"query": query})

    def sticker_search(self, query: str) -> Dict[str, Any]:
        """Find and download sticker packs"""
        return self.client._make_request(
            "GET", "/api/search/stickers", {"query": query}
        )

    def youtube_search(self, query: str) -> Dict[str, Any]:
        """Search YouTube videos"""
        return self.client._make_request(
            "GET", "/api/search/youtube2", {"query": query}
        )

    def bilibili_search(self, query: str) -> Dict[str, Any]:
        """Search Bilibili videos"""
        return self.client._make_request(
            "GET", "/api/search/bilibili", {"query": query}
        )

    def klipy_sticker(self, query: str) -> Dict[str, Any]:
        """Search and Download Stickers from Klipy"""
        return self.client._make_request("GET", "/api/klipy/sticker", {"query": query})

    def klipy_gif(self, query: str) -> Dict[str, Any]:
        """Search and Download Gifs from Klipy"""
        return self.client._make_request("GET", "/api/klipy/gif", {"query": query})

    def klipy_meme(self, query: str) -> Dict[str, Any]:
        """Search and Download Memes from Klipy"""
        return self.client._make_request("GET", "/api/klipy/meme", {"query": query})

    def manga_toon(self, query: str) -> Dict[str, Any]:
        """Search Mangatoon comics"""
        return self.client._make_request("GET", "/api/search/manga", {"query": query})


# ===== MEMES API =====
class MemesAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def custom_meme(
        self,
        template_id: str,
        text1: str,
        text2: Optional[str] = None,
        text3: Optional[str] = None,
        text4: Optional[str] = None,
        text5: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Use template and text of your own choice"""
        params = {"template_id": template_id, "text1": text1}
        if text2:
            params["text2"] = text2
        if text3:
            params["text3"] = text3
        if text4:
            params["text4"] = text4
        if text5:
            params["text5"] = text5
        return self.client._make_request("GET", "/api/meme/custom", params)

    def two_buttons(self, text1: str, text2: Optional[str] = None) -> Dict[str, Any]:
        """Two Red Buttons Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/buttons", params)

    def yelling_woman(self, text1: str, text2: Optional[str] = None) -> Dict[str, Any]:
        """Woman Yelling At Cat Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/yelling", params)

    def success_kid(self, text1: str, text2: Optional[str] = None) -> Dict[str, Any]:
        """Success Kid Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/success", params)

    def puppet_monkey(self, text1: str, text2: Optional[str] = None) -> Dict[str, Any]:
        """Monkey Puppet Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/puppet", params)

    def thinking_couple(
        self, text1: str, text2: Optional[str] = None
    ) -> Dict[str, Any]:
        """He is thinking about other woman Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/couple", params)

    def winnie_pooh(self, text1: str, text2: Optional[str] = None) -> Dict[str, Any]:
        """Tuxedo Winnie The Pooh Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/pooh", params)

    def squid_game(self, text1: str, text2: Optional[str] = None) -> Dict[str, Any]:
        """Squid Game Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/squid", params)

    def rock_driving(self, text1: str, text2: Optional[str] = None) -> Dict[str, Any]:
        """The Rock Driving Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/rock", params)

    def disappointed_guy(
        self, text1: str, text2: Optional[str] = None
    ) -> Dict[str, Any]:
        """Disappointed Black Guy Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/disappointed", params)

    def disaster_girl(self, text1: str, text2: Optional[str] = None) -> Dict[str, Any]:
        """Disaster Girl Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/disaster", params)

    def drake_hotline(self, text1: str, text2: Optional[str] = None) -> Dict[str, Any]:
        """Drake hotline bling Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        return self.client._make_request("GET", "/api/meme/drake", params)

    def argument_meme(
        self,
        text1: str,
        text2: Optional[str] = None,
        text3: Optional[str] = None,
        text4: Optional[str] = None,
        text5: Optional[str] = None,
    ) -> Dict[str, Any]:
        """American Chopper Argument Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        if text3:
            params["text3"] = text3
        if text4:
            params["text4"] = text4
        if text5:
            params["text5"] = text5
        return self.client._make_request("GET", "/api/meme/argument", params)

    def mask_reveal(
        self,
        text1: str,
        text2: Optional[str] = None,
        text3: Optional[str] = None,
        text4: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Scooby doo mask reveal Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        if text3:
            params["text3"] = text3
        if text4:
            params["text4"] = text4
        return self.client._make_request("GET", "/api/meme/mask", params)

    def expanding_brain(
        self,
        text1: str,
        text2: Optional[str] = None,
        text3: Optional[str] = None,
        text4: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Expanding Brain Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        if text3:
            params["text3"] = text3
        if text4:
            params["text4"] = text4
        return self.client._make_request("GET", "/api/meme/brain", params)

    def drowning_kid(
        self,
        text1: str,
        text2: Optional[str] = None,
        text3: Optional[str] = None,
        text4: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mother ignoring drowning kid Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        if text3:
            params["text3"] = text3
        if text4:
            params["text4"] = text4
        return self.client._make_request("GET", "/api/meme/drowning", params)

    def distracted_boyfriend(
        self, text1: str, text2: Optional[str] = None, text3: Optional[str] = None
    ) -> Dict[str, Any]:
        """Distracted boyfriend Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        if text3:
            params["text3"] = text3
        return self.client._make_request("GET", "/api/meme/boyfriend", params)

    def left_exit(
        self, text1: str, text2: Optional[str] = None, text3: Optional[str] = None
    ) -> Dict[str, Any]:
        """Left exit off ramp Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        if text3:
            params["text3"] = text3
        return self.client._make_request("GET", "/api/meme/exit", params)

    def anakin_padme(
        self, text1: str, text2: Optional[str] = None, text3: Optional[str] = None
    ) -> Dict[str, Any]:
        """Anakin padme 4 panel Meme"""
        params = {"text1": text1}
        if text2:
            params["text2"] = text2
        if text3:
            params["text3"] = text3
        return self.client._make_request("GET", "/api/meme/padme", params)

    def trending_memes(self) -> Dict[str, Any]:
        """Get trending memes"""
        return self.client._make_request("GET", "/api/meme/memes")


# ===== TIME API =====
class TimeAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def time_by_zone(self, zone: str) -> Dict[str, Any]:
        """Get current time for specific timezone"""
        return self.client._make_request("GET", "/api/time/zone", {"zone": zone})

    def time_by_ip(self, ip: str) -> Dict[str, Any]:
        """Get time based on IP address location"""
        return self.client._make_request("GET", "/api/time/ip", {"ip": ip})

    def time_coordinate(self, lat: str, lon: str) -> Dict[str, Any]:
        """Get time for specific latitude and longitude coordinates"""
        return self.client._make_request(
            "GET", "/api/time/coordinate", {"lat": lat, "lon": lon}
        )

    def time_zones(self) -> Dict[str, Any]:
        """List all available timezones"""
        return self.client._make_request("GET", "/api/time/zones")

    def time_convert(
        self, from_zone: str, to_zone: str, dateTime: str
    ) -> Dict[str, Any]:
        """Convert time between timezones"""
        return self.client._make_request(
            "GET",
            "/api/time/convert",
            {"from": from_zone, "to": to_zone, "dateTime": dateTime},
        )

    def time_translate(self, dateTime: str, lang: str) -> Dict[str, Any]:
        """Translate datetime into a language translated friendly string"""
        return self.client._make_request(
            "GET", "/api/time/translate", {"dateTime": dateTime, "lang": lang}
        )

    def day_of_week(self, date: str) -> Dict[str, Any]:
        """Convert a date to the day of the week"""
        return self.client._make_request("GET", "/api/time/dayofweek", {"date": date})

    def day_of_year(self, date: str) -> Dict[str, Any]:
        """Convert a date to the day of the year"""
        return self.client._make_request("GET", "/api/time/dayofyear", {"date": date})


# ===== PHOTOOXY API =====
class PhotoOxyAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def custom_effect(self, url: str, text: str) -> Dict[str, Any]:
        """Use effect page url of your own choice (single text)"""
        return self.client._make_request(
            "GET", "/api/photo/custom", {"url": url, "text": text}
        )

    def custom_effect2(self, url: str, text1: str, text2: str) -> Dict[str, Any]:
        """Use effect page url of your own choice (two texts)"""
        return self.client._make_request(
            "GET", "/api/photo/custom2", {"url": url, "text1": text1, "text2": text2}
        )

    def pubg_banner(self, text1: str, text2: str) -> Dict[str, Any]:
        """Make wallpaper battlegrounds logo text, banner PUBG game"""
        return self.client._make_request(
            "GET", "/api/photo/pug", {"text1": text1, "text2": text2}
        )

    def battlefield(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create Battlefield 4 Rising Effect"""
        return self.client._make_request(
            "GET", "/api/photo/battle4", {"text1": text1, "text2": text2}
        )

    def tiktok_effect(self, text1: str, text2: str) -> Dict[str, Any]:
        """Make tik tok text effect"""
        return self.client._make_request(
            "GET", "/api/photo/tiktok", {"text1": text1, "text2": text2}
        )

    def neon_effect(self, text: str) -> Dict[str, Any]:
        """Create glowing neon text effect"""
        return self.client._make_request("GET", "/api/photo/neon", {"text": text})

    def warface(self, text: str) -> Dict[str, Any]:
        """Free Warface facebook cover with name"""
        return self.client._make_request("GET", "/api/photo/warface", {"text": text})

    def warface2(self, text: str) -> Dict[str, Any]:
        """Make avatar Challenges Warface"""
        return self.client._make_request("GET", "/api/photo/warface2", {"text": text})

    def league_legends(self, text: str) -> Dict[str, Any]:
        """Create your own avatar League of Legends game avatar"""
        return self.client._make_request("GET", "/api/photo/league", {"text": text})

    def league_cover(self, text: str) -> Dict[str, Any]:
        """Make great League of Legends cover photo"""
        return self.client._make_request("GET", "/api/photo/lolcover", {"text": text})

    def league_shine(self, text: str) -> Dict[str, Any]:
        """Create Shine banner skins of league of legends"""
        return self.client._make_request("GET", "/api/photo/lolshine", {"text": text})

    def overwatch(self, text: str) -> Dict[str, Any]:
        """Make Cover Facebook for Overwatch Game"""
        return self.client._make_request("GET", "/api/photo/lolshine", {"text": text})

    def dark_metal(self, text: str) -> Dict[str, Any]:
        """Create dark metal text with special logo"""
        return self.client._make_request("GET", "/api/photo/darkmetal", {"text": text})

    def csgo_cover(self, text: str) -> Dict[str, Any]:
        """Personalize CS GO facebook cover photo with your name"""
        return self.client._make_request("GET", "/api/photo/csgo", {"text": text})


# ===== EPHOTO360 API =====
class Ephoto360API:
    def __init__(self, client: DiscardClient):
        self.client = client

    def custom_effect(self, url: str, text1: str) -> Dict[str, Any]:
        """Use effect url of your own choice (single text)"""
        return self.client._make_request(
            "GET", "/api/ephoto/custom", {"url": url, "text1": text1}
        )

    def custom_effect2(self, url: str, text1: str, text2: str) -> Dict[str, Any]:
        """Use effect url of your own choice (two texts)"""
        return self.client._make_request(
            "GET", "/api/ephoto/custom", {"url": url, "text1": text1, "text2": text2}
        )

    def deadpool(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create text effects in the style of the Deadpool logo"""
        return self.client._make_request(
            "GET", "/api/ephoto/deadpool", {"text1": text1, "text2": text2}
        )

    def wolf_logo(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create logo, avatar Wolf Galaxy"""
        return self.client._make_request(
            "GET", "/api/ephoto/wolf", {"text1": text1, "text2": text2}
        )

    def football_shirt(self, text1: str, text2: str) -> Dict[str, Any]:
        """Paul Scholes shirt foot ball print"""
        return self.client._make_request(
            "GET", "/api/ephoto/shirt", {"text1": text1, "text2": text2}
        )

    def pencil_sketch(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create text effects in the style of the Pencil Sketch logo"""
        return self.client._make_request(
            "GET", "/api/ephoto/sketch", {"text1": text1, "text2": text2}
        )

    def thor_logo(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create Thor logo style text effects"""
        return self.client._make_request(
            "GET", "/api/ephoto/thor", {"text1": text1, "text2": text2}
        )

    def captain_america(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create a cinematic Captain America text effect"""
        return self.client._make_request(
            "GET", "/api/ephoto/captain", {"text1": text1, "text2": text2}
        )

    def letter_logos(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create letter logos, colorful eye-catching abstract logo"""
        return self.client._make_request(
            "GET", "/api/ephoto/logo", {"text1": text1, "text2": text2}
        )

    def avengers_3d(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create text effects in the style of the Avengers 3D logo"""
        return self.client._make_request(
            "GET", "/api/ephoto/avengers", {"text1": text1, "text2": text2}
        )

    def mascot_logo(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create text effects in the style of the Mascot avatar logo"""
        return self.client._make_request(
            "GET", "/api/ephoto/mascot", {"text1": text1, "text2": text2}
        )

    def wood_3d(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create text effects in the style of 3D Wood"""
        return self.client._make_request(
            "GET", "/api/ephoto/wooden", {"text1": text1, "text2": text2}
        )

    def football_logo(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create text effects in the style of the Circle Football logo"""
        return self.client._make_request(
            "GET", "/api/ephoto/football", {"text1": text1, "text2": text2}
        )

    def steel_text(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create text effects in the style of steel text"""
        return self.client._make_request(
            "GET", "/api/ephoto/steel", {"text1": text1, "text2": text2}
        )

    def royal_text(self, text: str) -> Dict[str, Any]:
        """Create text effects in the style of Royal black and gold text"""
        return self.client._make_request("GET", "/api/ephoto/royal", {"text": text})

    def comic_3d(self, text: str) -> Dict[str, Any]:
        """Create 3D comic style text effect"""
        return self.client._make_request("GET", "/api/ephoto/comic", {"text": text})

    def angel_wing(self, text: str) -> Dict[str, Any]:
        """Create colorful angel wing avatars"""
        return self.client._make_request("GET", "/api/ephoto/angel", {"text": text})

    def glossy_silver(self, text: str) -> Dict[str, Any]:
        """Create glossy silver 3D text effects"""
        return self.client._make_request("GET", "/api/ephoto/glossy", {"text": text})

    def fps_game(self, text: str) -> Dict[str, Any]:
        """Gaming logo maker for FPS game team"""
        return self.client._make_request("GET", "/api/ephoto/game", {"text": text})

    def sand_text(self, text: str) -> Dict[str, Any]:
        """Write names and messages on the sand"""
        return self.client._make_request("GET", "/api/ephoto/sand", {"text": text})

    def colorful_text(self, text: str) -> Dict[str, Any]:
        """Create colorful text effects"""
        return self.client._make_request("GET", "/api/ephoto/colorful", {"text": text})

    def graffiti_color(self, text: str) -> Dict[str, Any]:
        """Create text effects in graffiti font color"""
        return self.client._make_request("GET", "/api/ephoto/graffiti", {"text": text})

    def jewel_effect(self, text: str) -> Dict[str, Any]:
        """Create gemstone effect, luxury and sophisticated"""
        return self.client._make_request("GET", "/api/ephoto/jewel", {"text": text})

    def glitch_text(self, text: str) -> Dict[str, Any]:
        """Create digital glitch effect"""
        return self.client._make_request("GET", "/api/ephoto/glitch", {"text": text})

    def gold_purple(self, text: str) -> Dict[str, Any]:
        """Metallic purple letters art"""
        return self.client._make_request("GET", "/api/ephoto/gpurple", {"text": text})

    def pubg_logo(self, text: str) -> Dict[str, Any]:
        """Create Colorful PUBG Logo"""
        return self.client._make_request("GET", "/api/ephoto/pubg", {"text": text})

    def arena_valor(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create Youtube banner for the AOV, ROV game"""
        return self.client._make_request(
            "GET", "/api/ephoto/valor", {"text1": text1, "text2": text2}
        )

    def war_zone(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create Youtube banner for the Call Of Duty War Zone game"""
        return self.client._make_request(
            "GET", "/api/ephoto/duty", {"text1": text1, "text2": text2}
        )

    def free_fire(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create Youtube banner for the Free Fire game"""
        return self.client._make_request(
            "GET", "/api/ephoto/ffire", {"text1": text1, "text2": text2}
        )

    def apex_legends(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create Youtube banner for the Apex Legends game"""
        return self.client._make_request(
            "GET", "/api/ephoto/apex", {"text1": text1, "text2": text2}
        )

    def overwatch1(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create Youtube banner for the Overwatch 1 game"""
        return self.client._make_request(
            "GET", "/api/ephoto/watch1", {"text1": text1, "text2": text2}
        )

    def overwatch2(self, text1: str, text2: str) -> Dict[str, Any]:
        """Create Youtube banner for the Overwatch 2 game"""
        return self.client._make_request(
            "GET", "/api/ephoto/watch2", {"text1": text1, "text2": text2}
        )

    def league_king(self, text: str) -> Dict[str, Any]:
        """Create profile cover for the League of King game"""
        return self.client._make_request("GET", "/api/ephoto/king", {"text": text})

    def league_king_aov(self, text: str) -> Dict[str, Any]:
        """Create profile cover for the League of King AOV game"""
        return self.client._make_request("GET", "/api/ephoto/kingaov", {"text": text})

    def league_legends_cover(self, text: str) -> Dict[str, Any]:
        """Create profile cover for the League of Legends game"""
        return self.client._make_request("GET", "/api/ephoto/legends", {"text": text})

    def black_board(self, text: str) -> Dict[str, Any]:
        """Writing chalk on the blackboard"""
        return self.client._make_request("GET", "/api/ephoto/board", {"text": text})

    def metal_avatar(self, text: str) -> Dict[str, Any]:
        """Create a Metal Avatar by your name"""
        return self.client._make_request("GET", "/api/ephoto/mavatar", {"text": text})

    def music_equalizer(self, text: str) -> Dict[str, Any]:
        """Create Music equalizer text effect"""
        return self.client._make_request("GET", "/api/ephoto/music", {"text": text})

    def fame_star(self, text: str) -> Dict[str, Any]:
        """Print Name On Hollywood Walk of Fame Star"""
        return self.client._make_request("GET", "/api/ephoto/fstar", {"text": text})

    def pavement_typo(self, text: str) -> Dict[str, Any]:
        """Create Typography text effect on pavement"""
        return self.client._make_request("GET", "/api/ephoto/pavement", {"text": text})


# ===== IMAGE PROCESS API =====
class ImageProcessAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def pixelate(
        self, file: BinaryIO, pixel_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a pixelated, retro 8-bit style effect"""
        data = {}
        if pixel_size:
            data["pixel_size"] = pixel_size
        return self.client._make_request(
            "POST", "/api/image/pixelate", data=data, files={"file": file}
        )

    def sketch(
        self, file: BinaryIO, style: str, effect_intensity: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert your images into pencil sketch style"""
        data = {"style": style}
        if effect_intensity:
            data["effect_intensity"] = effect_intensity
        return self.client._make_request(
            "POST", "/api/image/sketch", data=data, files={"file": file}
        )

    def halftone(
        self, file: BinaryIO, dot_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a dotted halftone pattern effect"""
        data = {}
        if dot_size:
            data["dot_size"] = dot_size
        return self.client._make_request(
            "POST", "/api/image/halftone", data=data, files={"file": file}
        )

    def denoise(self, file: BinaryIO, strength: Optional[str] = None) -> Dict[str, Any]:
        """Remove noise while preserving image details"""
        data = {}
        if strength:
            data["strength"] = strength
        return self.client._make_request(
            "POST", "/api/image/denoise", data=data, files={"file": file}
        )

    def remove_bg(self, file: BinaryIO) -> Dict[str, Any]:
        """Automatically remove image background with AI"""
        return self.client._make_request(
            "POST", "/api/image/rmbg", files={"file": file}
        )

    def draw_rectangle(
        self,
        file: BinaryIO,
        x1: str,
        x2: str,
        y1: str,
        y2: str,
        color: str,
        thickness: str,
    ) -> Dict[str, Any]:
        """Draw rectangles on your images for annotations"""
        data = {
            "x1": x1,
            "x2": x2,
            "y1": y1,
            "y2": y2,
            "color": color,
            "thickness": thickness,
        }
        return self.client._make_request(
            "POST", "/api/image/rectangle", data=data, files={"file": file}
        )

    def contrast(self, file: BinaryIO, factor: Optional[str] = None) -> Dict[str, Any]:
        """Enhance the contrast between light and dark areas"""
        data = {}
        if factor:
            data["factor"] = factor
        return self.client._make_request(
            "POST", "/api/image/contrast", data=data, files={"file": file}
        )

    def sepia(self, file: BinaryIO) -> Dict[str, Any]:
        """Add a warm, vintage sepia tone to your images"""
        return self.client._make_request(
            "POST", "/api/image/sepia", files={"file": file}
        )

    def brightness(
        self, file: BinaryIO, factor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Adjust the brightness of your images"""
        data = {}
        if factor:
            data["factor"] = factor
        return self.client._make_request(
            "POST", "/api/image/brightness", data=data, files={"file": file}
        )

    def threshold(
        self, file: BinaryIO, threshold_value: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply binary threshold to create high contrast images"""
        data = {}
        if threshold_value:
            data["threshold_value"] = threshold_value
        return self.client._make_request(
            "POST", "/api/image/threshold", data=data, files={"file": file}
        )

    def isolate(self, file: BinaryIO, channel: str) -> Dict[str, Any]:
        """Isolate red, green or blue color channels"""
        return self.client._make_request(
            "POST",
            "/api/image/isolate",
            data={"channel": channel},
            files={"file": file},
        )

    def invert(self, file: BinaryIO) -> Dict[str, Any]:
        """Invert the colors of your images for negative effect"""
        return self.client._make_request(
            "POST", "/api/image/invert", files={"file": file}
        )

    def blur(self, file: BinaryIO, intensity: Optional[str] = None) -> Dict[str, Any]:
        """Apply gaussian blur for a soft focus effect"""
        data = {}
        if intensity:
            data["intensity"] = intensity
        return self.client._make_request(
            "POST", "/api/image/blur", data=data, files={"file": file}
        )

    def sharpen(self, file: BinaryIO) -> Dict[str, Any]:
        """Enhance details and edges in your images"""
        return self.client._make_request(
            "POST", "/api/image/sharpen", files={"file": file}
        )

    def edges(self, file: BinaryIO, method: Optional[str] = None) -> Dict[str, Any]:
        """Detect and highlight edges in your images"""
        data = {}
        if method:
            data["method"] = method
        return self.client._make_request(
            "POST", "/api/image/edges", data=data, files={"file": file}
        )

    def cartoon(
        self,
        file: BinaryIO,
        edge_size: Optional[str] = None,
        num_colors: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transform photos into cartoon style illustration"""
        data = {}
        if edge_size:
            data["edge_size"] = edge_size
        if num_colors:
            data["num_colors"] = num_colors
        return self.client._make_request(
            "POST", "/api/image/cartoon", data=data, files={"file": file}
        )

    def emboss(
        self,
        file: BinaryIO,
        direction: Optional[str] = None,
        strength: Optional[str] = None,
        grayscale: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a 3D embossed effect on your images"""
        data = {}
        if direction:
            data["direction"] = direction
        if strength:
            data["strength"] = strength
        if grayscale:
            data["grayscale"] = grayscale
        return self.client._make_request(
            "POST", "/api/image/emboss", data=data, files={"file": file}
        )

    def vignette(
        self, file: BinaryIO, intensity: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a soft vignette effect around the edges"""
        data = {}
        if intensity:
            data["intensity"] = intensity
        return self.client._make_request(
            "POST", "/api/image/vignette", data=data, files={"file": file}
        )

    def tint(
        self, file: BinaryIO, color: str, intensity: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply a color tint to your images"""
        data = {"color": color}
        if intensity:
            data["intensity"] = intensity
        return self.client._make_request(
            "POST", "/api/image/tint", data=data, files={"file": file}
        )

    def gamma_correction(
        self, file: BinaryIO, gamma: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply gamma correction to adjust image luminance"""
        data = {}
        if gamma:
            data["gamma"] = gamma
        return self.client._make_request(
            "POST", "/api/image/correction", data=data, files={"file": file}
        )

    def adaptive(
        self,
        file: BinaryIO,
        clip_limit: Optional[str] = None,
        tile_grid_size: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Apply adaptive histogram equalization"""
        data = {}
        if clip_limit:
            data["clip_limit"] = clip_limit
        if tile_grid_size:
            data["tile_grid_size"] = tile_grid_size
        return self.client._make_request(
            "POST", "/api/image/adaptive", data=data, files={"file": file}
        )

    def posterize(self, file: BinaryIO, levels: Optional[str] = None) -> Dict[str, Any]:
        """Reduce the number of colors for a poster-like effect"""
        data = {}
        if levels:
            data["levels"] = levels
        return self.client._make_request(
            "POST", "/api/image/posterize", data=data, files={"file": file}
        )

    def histogram(self, file: BinaryIO) -> Dict[str, Any]:
        """Generate a histogram to analyze color distribution"""
        return self.client._make_request(
            "POST", "/api/image/histogram", files={"file": file}
        )

    def resize(
        self,
        file: BinaryIO,
        width: str,
        height: str,
        keep_aspect_ratio: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resize your images to specific dimensions"""
        data = {"width": width, "height": height}
        if keep_aspect_ratio:
            data["keep_aspect_ratio"] = keep_aspect_ratio
        return self.client._make_request(
            "POST", "/api/image/resize", data=data, files={"file": file}
        )

    def crop(
        self,
        file: BinaryIO,
        x: str,
        y: str,
        width: str,
        height: str,
        quality: Optional[str] = None,
        smart_crop: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Crop your images to focus on important parts"""
        data = {"x": x, "y": y, "width": width, "height": height}
        if quality:
            data["quality"] = quality
        if smart_crop:
            data["smart_crop"] = smart_crop
        return self.client._make_request(
            "POST", "/api/image/crop", data=data, files={"file": file}
        )

    def rotate(
        self,
        file: BinaryIO,
        angle: str,
        quality: Optional[str] = None,
        centerX: Optional[str] = None,
        centerY: Optional[str] = None,
        expand: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Rotate your image to any angle with precision"""
        data = {"angle": angle}
        if quality:
            data["quality"] = quality
        if centerX:
            data["centerX"] = centerX
        if centerY:
            data["centerY"] = centerY
        if expand:
            data["expand"] = expand
        return self.client._make_request(
            "POST", "/api/image/rotate", data=data, files={"file": file}
        )

    def flip(
        self, file: BinaryIO, mode: str, quality: Optional[str] = None
    ) -> Dict[str, Any]:
        """Flip your image vertically or horizontally"""
        data = {"mode": mode}
        if quality:
            data["quality"] = quality
        return self.client._make_request(
            "POST", "/api/image/flip", data=data, files={"file": file}
        )

    def convert(self, file: BinaryIO, target_format: str, **kwargs) -> Dict[str, Any]:
        """Convert between image formats like jpg, png, webp"""
        data = {"target_format": target_format}
        data.update(kwargs)
        return self.client._make_request(
            "POST", "/api/image/convert", data=data, files={"file": file}
        )

    def padding(
        self,
        file: BinaryIO,
        target_width: Optional[str] = None,
        target_height: Optional[str] = None,
        background_color: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resize image and add padding to maintain aspect ratio"""
        data = {}
        if target_width:
            data["target_width"] = target_width
        if target_height:
            data["target_height"] = target_height
        if background_color:
            data["background_color"] = background_color
        return self.client._make_request(
            "POST", "/api/image/padding", data=data, files={"file": file}
        )

    def compress(self, file: BinaryIO, **kwargs) -> Dict[str, Any]:
        """Reduce file size while maintaining visual quality"""
        return self.client._make_request(
            "POST", "/api/image/compress", data=kwargs, files={"file": file}
        )

    def thumbnail(
        self, file: BinaryIO, width: str, height: str, crop: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate optimized thumbnails"""
        data = {"width": width, "height": height}
        if crop:
            data["crop"] = crop
        return self.client._make_request(
            "POST", "/api/image/thumbnail", data=data, files={"file": file}
        )

    def grayscale(self, file: BinaryIO) -> Dict[str, Any]:
        """Convert your images to black and white"""
        return self.client._make_request(
            "POST", "/api/image/grayscale", files={"file": file}
        )


# ===== INFORMATION API =====
class InformationAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def github_user(self, username: str) -> Dict[str, Any]:
        """Get detailed information of a Github user"""
        return self.client._make_request(
            "GET", "/api/github/user", {"username": username}
        )

    def github_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get detailed information of specific public repository"""
        return self.client._make_request(
            "GET", "/api/github/repo", {"owner": owner, "repo": repo}
        )

    def github_readme(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch Readme of specific public repository"""
        return self.client._make_request(
            "GET", "/api/github/readme", {"owner": owner, "repo": repo}
        )

    def imdb_info(self, query: str) -> Dict[str, Any]:
        """Get detailed movie and TV show information from IMDb"""
        return self.client._make_request("GET", "/api/info/imdb", {"query": query})

    def tmdb_info(self, query: str) -> Dict[str, Any]:
        """Get detailed movie and TV show information from TMDb"""
        return self.client._make_request("GET", "/api/info/tmdb", {"query": query})

    def movie_info(self, title: str) -> Dict[str, Any]:
        """Get detailed movie information"""
        return self.client._make_request("GET", "/api/info/movie", {"title": title})

    def university(self, country: str) -> Dict[str, Any]:
        """Get detailed list of universities in any country"""
        return self.client._make_request(
            "GET", "/api/info/university", {"country": country}
        )

    def ip_info(self, ip: str) -> Dict[str, Any]:
        """Get detailed information about IP addresses including location"""
        return self.client._make_request("GET", "/api/info/ip", {"ip": ip})

    def x_trends(self, country: str) -> Dict[str, Any]:
        """Get trending topics and hashtags from Twitter/X by country"""
        return self.client._make_request(
            "GET", "/api/info/trends", {"country": country}
        )

    def open_weather(self, place: str) -> Dict[str, Any]:
        """Get current weather information from open weather"""
        return self.client._make_request("GET", "/api/weather/open", {"place": place})

    def weather(self, lat: str, lon: str) -> Dict[str, Any]:
        """Get current weather information based on latitude and longitude"""
        return self.client._make_request(
            "GET", "/api/info/weather", {"lat": lat, "lon": lon}
        )

    def weather_city(self, city: str) -> Dict[str, Any]:
        """Get current weather information for any city worldwide"""
        return self.client._make_request("GET", "/api/weather/info", {"city": city})

    def go_weather(self, place: str) -> Dict[str, Any]:
        """Get current weather information for any city worldwide"""
        return self.client._make_request("GET", "/api/info/goweather", {"place": place})

    def air_quality(self, lat: str, lon: str) -> Dict[str, Any]:
        """Get air quality information based on latitude and longitude"""
        return self.client._make_request(
            "GET", "/api/info/air", {"lat": lat, "lon": lon}
        )

    def flood_info(self, lat: str, lon: str) -> Dict[str, Any]:
        """Get river information based on latitude and longitude"""
        return self.client._make_request(
            "GET", "/api/info/river", {"lat": lat, "lon": lon}
        )

    def geo_coding(self, name: str) -> Dict[str, Any]:
        """Get complete geo details of any city/place"""
        return self.client._make_request("GET", "/api/info/geo", {"name": name})

    def crypto_info(self, id: str) -> Dict[str, Any]:
        """Get information about crypto coins"""
        return self.client._make_request("GET", "/api/info/crypto", {"id": id})

    def crypto_tags(self) -> Dict[str, Any]:
        """Get crypto info by coin tags"""
        return self.client._make_request("GET", "/api/crypto/tags")

    def rgb_info(self, rgb: str) -> Dict[str, Any]:
        """Get detailed Color Info via RGB"""
        return self.client._make_request("GET", "/api/info/rgb", {"rgb": rgb})

    def hex_info(self, hex: str) -> Dict[str, Any]:
        """Get detailed Color Info via HEX"""
        return self.client._make_request("GET", "/api/info/hex", {"hex": hex})

    def scheme_rgb(self, rgb: str) -> Dict[str, Any]:
        """Get detailed Color Scheme via RGB"""
        return self.client._make_request("GET", "/api/scheme/rgb", {"rgb": rgb})

    def scheme_hex(
        self, hex: str, mode: Optional[str] = None, count: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed Color Scheme via HEX"""
        params = {"hex": hex}
        if mode:
            params["mode"] = mode
        if count:
            params["count"] = count
        return self.client._make_request("GET", "/api/scheme/hex", params)

    def country_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about any country"""
        return self.client._make_request("GET", "/api/info/country", {"name": name})

    def wikipedia(self, query: str) -> Dict[str, Any]:
        """Search and get Wikipedia article summaries"""
        return self.client._make_request("GET", "/api/info/wiki", {"query": query})

    def top_websites(self, country: str) -> Dict[str, Any]:
        """Get top rated websites by visitors in a specific country"""
        return self.client._make_request(
            "GET", "/api/top/websites", {"country": country}
        )

    def top_servers(self) -> Dict[str, Any]:
        """Get a list of top rated web servers"""
        return self.client._make_request("GET", "/api/top/servers")

    def top_tech(self) -> Dict[str, Any]:
        """Get a list of top rated technologies"""
        return self.client._make_request("GET", "/api/top/tech")

    def top_frameworks(self) -> Dict[str, Any]:
        """Get a list of top rated web frameworks"""
        return self.client._make_request("GET", "/api/top/frameworks")

    def top_apps(self, country: str) -> Dict[str, Any]:
        """Get top rated android apps by usage in specific country"""
        return self.client._make_request("GET", "/api/top/apps", {"country": country})

    def top_movies(self) -> Dict[str, Any]:
        """Get top rated movies on IMDb"""
        return self.client._make_request("GET", "/api/top/movies")

    def top_series(self) -> Dict[str, Any]:
        """Get top rated TV series on IMDb"""
        return self.client._make_request("GET", "/api/top/series")

    def country_indicators(self, country: str) -> Dict[str, Any]:
        """Get country indicators, Economy and other info"""
        return self.client._make_request(
            "GET", "/api/info/country", {"country": country}
        )

    def mobile_prices(self, brand: str, page: Optional[str] = None) -> Dict[str, Any]:
        """Get latest mobile phone prices in PKR, models and more info"""
        params = {"brand": brand}
        if page:
            params["page"] = page
        return self.client._make_request("GET", "/api/prices/mobile", params)


# ===== TEMPMAIL API =====
class TempMailAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def mail_domains(self) -> Dict[str, Any]:
        """Get working domains for temp mail account"""
        return self.client._make_request("GET", "/api/mailtm/domains")

    def create_mail(self, password: str) -> Dict[str, Any]:
        """Create temporary email account"""
        return self.client._make_request(
            "GET", "/api/mailtm/create", {"password": password}
        )

    def mail_inbox(self, token: str, page: Optional[str] = None) -> Dict[str, Any]:
        """Gets all the Message resources from inbox"""
        params = {"token": token}
        if page:
            params["page"] = page
        return self.client._make_request("GET", "/api/mailtm/inbox", params)

    def account_id(self, token: str, id: str) -> Dict[str, Any]:
        """Get resources by account id using account token"""
        return self.client._make_request(
            "GET", "/api/mailtm/account", {"token": token, "id": id}
        )

    def message_id(self, token: str, id: str) -> Dict[str, Any]:
        """Get Message by message id using account token from inbox"""
        return self.client._make_request(
            "GET", "/api/mailtm/message", {"token": token, "id": id}
        )

    def delete_account(self, token: str, id: str) -> Dict[str, Any]:
        """Delete your temp mail account"""
        return self.client._make_request(
            "GET", "/api/mailtm/del/acc", {"token": token, "id": id}
        )

    def delete_message(self, token: str, id: str) -> Dict[str, Any]:
        """Delete a specific message from inbox"""
        return self.client._make_request(
            "GET", "/api/mailtm/del/msg", {"token": token, "id": id}
        )

    def create_mailgw(self, password: str) -> Dict[str, Any]:
        """10 Minute Mail, create temporary email account"""
        return self.client._make_request(
            "GET", "/api/mailgw/create", {"password": password}
        )

    def mailgw_inbox(self, token: str) -> Dict[str, Any]:
        """Gets all messages from MailGW inbox"""
        return self.client._make_request("GET", "/api/mailgw/inbox", {"token": token})


# ===== UPLOADS API =====
class UploadsAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def catbox(self, file: BinaryIO) -> Dict[str, Any]:
        """Upload files to catbox, valid forever, all types supported"""
        return self.client._make_request("POST", "/api/catbox", files={"file": file})

    def gofile(self, file: BinaryIO) -> Dict[str, Any]:
        """Upload images or files to gofile, valid forever"""
        return self.client._make_request("POST", "/api/gofile", files={"file": file})

    def gyazo(self, file: BinaryIO) -> Dict[str, Any]:
        """Upload images and videos to gyazo, validity forever"""
        return self.client._make_request("POST", "/api/gyazo", files={"file": file})

    def hastebin(self, file: BinaryIO) -> Dict[str, Any]:
        """Upload text or files to hastebin, valid forever"""
        return self.client._make_request("POST", "/api/hastebin", files={"file": file})

    def pastebin(self, file: BinaryIO) -> Dict[str, Any]:
        """Upload text or files to pastebin, valid forever"""
        return self.client._make_request("POST", "/api/pastebin", files={"file": file})

    def imgbb(self, file: BinaryIO) -> Dict[str, Any]:
        """Upload images and gifs to Imgbb, validity 7 days"""
        return self.client._make_request("POST", "/api/imgbb", files={"file": file})

    def pixeldrain(self, file: BinaryIO) -> Dict[str, Any]:
        """Upload images to PixelDrain"""
        return self.client._make_request(
            "POST", "/api/pixeldrain", files={"file": file}
        )

    def uguuse(self, file: BinaryIO) -> Dict[str, Any]:
        """Upload image, gif and files to uguuse, validity 24 hours"""
        return self.client._make_request("POST", "/api/uguuse", files={"file": file})

    def map_360(self, url: str) -> Dict[str, Any]:
        """Upload Image from url to Map 360"""
        return self.client._make_request("GET", "/api/upload/360", {"url": url})

    def xian_image(self, url: str) -> Dict[str, Any]:
        """Upload Image from url to Xian"""
        return self.client._make_request("GET", "/api/upload/xian", {"url": url})


# ===== RANDOM API =====
class RandomAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def sudoku_generate(self, difficulty: str) -> Dict[str, Any]:
        """Generate Sudoku Game"""
        return self.client._make_request(
            "GET", "/api/sudoku/generate", {"difficulty": difficulty}
        )

    def sudoku_solve(self, puzzle: List[List[int]]) -> Dict[str, Any]:
        """Solve Sudoku Game"""
        return self.client._make_request(
            "POST", "/api/sudoku/solve", json_data={"puzzle": puzzle}
        )

    def archive_metadata(self, id: str) -> Dict[str, Any]:
        """Get Internet Archive Metadata of a specific ID"""
        return self.client._make_request("GET", "/api/archive/metadata", {"id": id})

    def wayback_snapshot(self, url: str) -> Dict[str, Any]:
        """Check if a given url is archived in the Wayback Machine"""
        return self.client._make_request("GET", "/api/archive/wayback", {"url": url})

    def create_snapshot(self, url: str) -> Dict[str, Any]:
        """Create Wayback Snapshots"""
        return self.client._make_request(
            "POST", "/api/archive/wayback", json_data={"url": url}
        )

    def book_cover(self, itemid: str) -> Dict[str, Any]:
        """Get book cover by specific ID"""
        return self.client._make_request(
            "GET", "/api/archive/bookcover", {"itemid": itemid}
        )

    def world_wonders(self) -> Dict[str, Any]:
        """Get detailed information of a World Wonders"""
        return self.client._make_request("GET", "/api/wonders/info")

    def random_trivia(self) -> Dict[str, Any]:
        """Get Random Trivia"""
        return self.client._make_request("GET", "/api/random/trivia")

    def age_guess(self, name: str) -> Dict[str, Any]:
        """Guess age by name"""
        return self.client._make_request("GET", "/api/age/info", {"name": name})

    def gender_guess(self, name: str) -> Dict[str, Any]:
        """Gender guess by name"""
        return self.client._make_request("GET", "/api/gender/info", {"name": name})

    def name_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a name"""
        return self.client._make_request("GET", "/api/name/info", {"name": name})

    def random_advice(self) -> Dict[str, Any]:
        """Get random advice"""
        return self.client._make_request("GET", "/api/random/advice")

    def random_fact(self) -> Dict[str, Any]:
        """Get random fact"""
        return self.client._make_request("GET", "/api/random/fact")

    def random_uuid(self) -> Dict[str, Any]:
        """Random uuid generator"""
        return self.client._make_request("GET", "/api/random/uuid")
