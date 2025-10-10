"""
discard/categories_part2.py - More API categories
"""

from typing import Dict, Any, Optional
from .client import DiscardClient


# ===== CHATBOTS API =====
class ChatbotsAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def llama_bot(self, text: str) -> Dict[str, Any]:
        """Meta's Llama model providing state-of-the-art language understanding"""
        return self.client._make_request("GET", "/api/bot/llama", {"text": text})

    def qwen_bot(self, text: str) -> Dict[str, Any]:
        """Qwen series model offering efficient language processing"""
        return self.client._make_request("GET", "/api/bot/qwen", {"text": text})

    def baidu_bot(self, text: str) -> Dict[str, Any]:
        """Baidu's ERNIE model providing advanced Chinese language understanding"""
        return self.client._make_request("GET", "/api/bot/baidu", {"text": text})

    def gemma_bot(self, text: str) -> Dict[str, Any]:
        """Google's Gemma model offering high-quality language processing"""
        return self.client._make_request("GET", "/api/bot/gemma", {"text": text})

    def spark_bot(self, text: str) -> Dict[str, Any]:
        """Spark AI offering high-quality language processing"""
        return self.client._make_request("GET", "/api/chat/spark", {"text": text})

    def quark_bot(self, text: str) -> Dict[str, Any]:
        """Quark AI offering high-quality language processing"""
        return self.client._make_request("GET", "/api/chat/quark", {"text": text})

    def glm_bot(self, text: str) -> Dict[str, Any]:
        """Offering high-quality language processing"""
        return self.client._make_request("GET", "/api/chat/glm", {"text": text})


# ===== CANVAS API =====
class CanvasAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def circle(self, avatar: str) -> Dict[str, Any]:
        """Apply circle canvas feature on image"""
        return self.client._make_request(
            "GET", "/api/canvas/circle", {"avatar": avatar}
        )

    def bisexual(self, avatar: str) -> Dict[str, Any]:
        """Apply bisexual canvas feature on image"""
        return self.client._make_request(
            "GET", "/api/canvas/bisexual", {"avatar": avatar}
        )

    def heart(self, avatar: str) -> Dict[str, Any]:
        """Apply heart canvas feature on image"""
        return self.client._make_request("GET", "/api/canvas/heart", {"avatar": avatar})

    def horny(self, avatar: str) -> Dict[str, Any]:
        """Apply horny canvas feature on image"""
        return self.client._make_request("GET", "/api/canvas/horny", {"avatar": avatar})

    def pansexual(self, avatar: str) -> Dict[str, Any]:
        """Apply pansexual canvas feature on image"""
        return self.client._make_request(
            "GET", "/api/canvas/pansexual", {"avatar": avatar}
        )

    def lesbian(self, avatar: str) -> Dict[str, Any]:
        """Apply lesbian canvas feature on image"""
        return self.client._make_request(
            "GET", "/api/canvas/lesbian", {"avatar": avatar}
        )

    def lgbtq(self, avatar: str) -> Dict[str, Any]:
        """Apply LGBT canvas feature on image"""
        return self.client._make_request("GET", "/api/canvas/lgbtq", {"avatar": avatar})

    def nobin(self, avatar: str) -> Dict[str, Any]:
        """Apply no binary canvas feature on image"""
        return self.client._make_request("GET", "/api/canvas/nobin", {"avatar": avatar})

    def transgen(self, avatar: str) -> Dict[str, Any]:
        """Apply transgender canvas feature on image"""
        return self.client._make_request(
            "GET", "/api/canvas/transgen", {"avatar": avatar}
        )

    def tonikawa(self, avatar: str) -> Dict[str, Any]:
        """Apply tonikawa canvas feature on image"""
        return self.client._make_request(
            "GET", "/api/canvas/tonikawa", {"avatar": avatar}
        )

    def simpcard(self, avatar: str) -> Dict[str, Any]:
        """Apply simpcard canvas feature on image"""
        return self.client._make_request(
            "GET", "/api/canvas/simpcard", {"avatar": avatar}
        )


# ===== CODEC API =====
class CodecAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def base64(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text with base64"""
        return self.client._make_request(
            "GET", "/api/tools/base64", {"data": data, "mode": mode}
        )

    def base32(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text with base32"""
        return self.client._make_request(
            "GET", "/api/tools/base32", {"data": data, "mode": mode}
        )

    def base16(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text with base16"""
        return self.client._make_request(
            "GET", "/api/tools/base16", {"data": data, "mode": mode}
        )

    def base36(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text with base36"""
        return self.client._make_request(
            "GET", "/api/tools/base36", {"data": data, "mode": mode}
        )

    def base45(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text with base45"""
        return self.client._make_request(
            "GET", "/api/tools/base45", {"data": data, "mode": mode}
        )

    def base58(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text with base58"""
        return self.client._make_request(
            "GET", "/api/tools/base58", {"data": data, "mode": mode}
        )

    def base62(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text with base62"""
        return self.client._make_request(
            "GET", "/api/tools/base62", {"data": data, "mode": mode}
        )

    def base85(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text with base85"""
        return self.client._make_request(
            "GET", "/api/tools/base85", {"data": data, "mode": mode}
        )

    def base91(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text with base91"""
        return self.client._make_request(
            "GET", "/api/tools/base91", {"data": data, "mode": mode}
        )

    def binary(self, data: str, mode: str) -> Dict[str, Any]:
        """Encode or Decode data/text to/from Binary"""
        return self.client._make_request(
            "GET", "/api/tools/binary", {"data": data, "mode": mode}
        )

    def brainfuck(self, text: str) -> Dict[str, Any]:
        """Generate brain fuck code of given text"""
        return self.client._make_request("GET", "/api/tools/brainfuck", {"text": text})

    def interpreter(self, code: str) -> Dict[str, Any]:
        """Implements a Brainfuck language interpreter"""
        return self.client._make_request("GET", "/api/interpreter", {"code": code})


# ===== SHORTENER API =====
class ShortenerAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def isgd(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using is.gd"""
        return self.client._make_request("GET", "/api/short/isgd", {"url": url})

    def l8nu(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using l8.nu"""
        return self.client._make_request("GET", "/api/short/l8nu", {"url": url})

    def reurl(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using reurl"""
        return self.client._make_request("GET", "/api/short/reurl", {"url": url})

    def tinycc(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using tiny.cc"""
        return self.client._make_request("GET", "/api/short/tinycc", {"url": url})

    def clck(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using clck.ru"""
        return self.client._make_request("GET", "/api/short/clck", {"url": url})

    def itsl(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using its.ssl"""
        return self.client._make_request("GET", "/api/short/itsl", {"url": url})

    def cuqin(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using cuq.in"""
        return self.client._make_request("GET", "/api/short/cuqin", {"url": url})

    def surl(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using s-url"""
        return self.client._make_request("GET", "/api/short/surl", {"url": url})

    def vurl(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using v-url"""
        return self.client._make_request("GET", "/api/short/vurl", {"url": url})

    def vgd(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using v.gd"""
        return self.client._make_request("GET", "/api/short/vgd", {"url": url})

    def clean(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using cleanuri"""
        return self.client._make_request("GET", "/api/short/clean", {"url": url})

    def bitly(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using bitly"""
        return self.client._make_request("GET", "/api/short/bitly", {"url": url})

    def tiny(self, url: str) -> Dict[str, Any]:
        """Create short urls from long using tinyurl"""
        return self.client._make_request("GET", "/api/short/tiny", {"url": url})

    def unshort(self, url: str) -> Dict[str, Any]:
        """Get original url from a short url"""
        return self.client._make_request("GET", "/api/short/unshort", {"url": url})


# ===== AUDIODB API =====
class AudioDBAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def search_artist(self, name: str) -> Dict[str, Any]:
        """Search for any Music team by its name"""
        return self.client._make_request("GET", "/api/audiodb/scan", {"name": name})

    def search_track(self, name: str, track: str) -> Dict[str, Any]:
        """Search a track by artist and track title"""
        return self.client._make_request(
            "GET", "/api/audiodb/track", {"name": name, "track": track}
        )

    def discography(self, mbid: str) -> Dict[str, Any]:
        """Search by Music Brainz Artist ID"""
        return self.client._make_request(
            "GET", "/api/audiodb/discography", {"mbid": mbid}
        )

    def search_albums(self, name: str) -> Dict[str, Any]:
        """Get all albums by artist"""
        return self.client._make_request("GET", "/api/audiodb/albums", {"name": name})

    def specific_album(self, name: str, album: str) -> Dict[str, Any]:
        """Get specific album by artist"""
        return self.client._make_request(
            "GET", "/api/audiodb/album", {"name": name, "album": album}
        )

    def artist_by_id(self, id: str) -> Dict[str, Any]:
        """Get Artist by ID"""
        return self.client._make_request("GET", "/api/audiodb/artist", {"id": id})

    def artist_by_mbid(self, mbid: str) -> Dict[str, Any]:
        """Get Artist by Music Brainz Artist ID"""
        return self.client._make_request(
            "GET", "/api/audiodb/artist-mb", {"mbid": mbid}
        )

    def artist_links(self, id: str) -> Dict[str, Any]:
        """Get Artist Links by ID"""
        return self.client._make_request("GET", "/api/audiodb/artist-links", {"id": id})

    def album_by_id(self, id: str) -> Dict[str, Any]:
        """Lookup Album details using its ID"""
        return self.client._make_request("GET", "/api/audiodb/album-id", {"id": id})

    def album_by_mbid(self, mbid: str) -> Dict[str, Any]:
        """Lookup Album details using its MusicBrainz ID"""
        return self.client._make_request("GET", "/api/audiodb/album-mb", {"mbid": mbid})

    def track_by_album(self, id: str) -> Dict[str, Any]:
        """Lookup Track details using its Album ID"""
        return self.client._make_request("GET", "/api/audiodb/track-album", {"id": id})

    def track_by_id(self, id: str) -> Dict[str, Any]:
        """Lookup Track details using its ID"""
        return self.client._make_request("GET", "/api/audiodb/track-id", {"id": id})

    def track_by_mbid(self, mbid: str) -> Dict[str, Any]:
        """Lookup Track details using its MusicBrainz ID"""
        return self.client._make_request("GET", "/api/audiodb/track-mb", {"mbid": mbid})

    def videos_by_id(self, id: str) -> Dict[str, Any]:
        """List all the music videos for an artist ID"""
        return self.client._make_request("GET", "/api/audiodb/mvid", {"id": id})

    def videos_by_mbid(self, mbid: str) -> Dict[str, Any]:
        """List all the music videos for an artist MusicBrainz ID"""
        return self.client._make_request("GET", "/api/audiodb/mvid-mb", {"mbid": mbid})

    def trending_albums(self, country: Optional[str] = None) -> Dict[str, Any]:
        """List trending albums"""
        params = {}
        if country:
            params["country"] = country
        return self.client._make_request("GET", "/api/audiodb/trending-albums", params)

    def trending_singles(self, country: Optional[str] = None) -> Dict[str, Any]:
        """List trending singles"""
        params = {}
        if country:
            params["country"] = country
        return self.client._make_request("GET", "/api/audiodb/trending-singles", params)

    def top_tracks(self, name: str) -> Dict[str, Any]:
        """List the top 10 songs for an artist by artist name"""
        return self.client._make_request(
            "GET", "/api/audiodb/top-tracks", {"name": name}
        )

    def top_tracks_mb(self, mbid: str) -> Dict[str, Any]:
        """List the top 10 songs for an artist by MusicBrainz ID"""
        return self.client._make_request(
            "GET", "/api/audiodb/top-tracks-mb", {"mbid": mbid}
        )


# ===== QUOTES API =====
class QuotesAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def commit_message(self) -> Dict[str, Any]:
        """Get random git commit messages"""
        return self.client._make_request("GET", "/api/commit/message")

    def stranger_things(self) -> Dict[str, Any]:
        """Random stranger things quotes"""
        return self.client._make_request("GET", "/api/quote/stranger")

    def pickup_lines(self) -> Dict[str, Any]:
        """Get random pickup lines"""
        return self.client._make_request("GET", "/api/quote/pickup")

    def why_question(self) -> Dict[str, Any]:
        """Get random why questions"""
        return self.client._make_request("GET", "/api/quote/why")

    def random_quotes(self) -> Dict[str, Any]:
        """Get random quotes from a vast Library of quotes"""
        return self.client._make_request("GET", "/api/quotes/random")

    def tech_tips(self) -> Dict[str, Any]:
        """Get random tech tips"""
        return self.client._make_request("GET", "/api/quote/techtips")

    def coding_tips(self) -> Dict[str, Any]:
        """Get random programming tips"""
        return self.client._make_request("GET", "/api/quote/coding")

    def fun_facts(self) -> Dict[str, Any]:
        """Get random fun facts"""
        return self.client._make_request("GET", "/api/quote/funfacts")

    def wyr_quotes(self) -> Dict[str, Any]:
        """Get random would you rather quotes"""
        return self.client._make_request("GET", "/api/quote/wyr")

    def motive_quotes(self) -> Dict[str, Any]:
        """Get random motivational quotes"""
        return self.client._make_request("GET", "/api/quote/motiv")

    def islamic_quotes(self) -> Dict[str, Any]:
        """Get random Islamic quotes"""
        return self.client._make_request("GET", "/api/quote/islamic")

    def life_hacks(self) -> Dict[str, Any]:
        """Get random life hacks"""
        return self.client._make_request("GET", "/api/quote/lifehacks")

    def breaking_bad(self) -> Dict[str, Any]:
        """Get random quotes of the breaking bad characters"""
        return self.client._make_request("GET", "/api/quote/breakingbad")

    def gautam_buddha(self) -> Dict[str, Any]:
        """Get random quotes of Buddhism"""
        return self.client._make_request("GET", "/api/quote/buddha")

    def quotes_random(self) -> Dict[str, Any]:
        """Get random quotes of famous authors"""
        return self.client._make_request("GET", "/api/quote/random")

    def stoic_quotes(self) -> Dict[str, Any]:
        """Get random stoic quotes"""
        return self.client._make_request("GET", "/api/quote/stoic")

    def lucifer_quotes(self) -> Dict[str, Any]:
        """Get random quotes of Lucifer"""
        return self.client._make_request("GET", "/api/quote/lucifer")


# ===== DOWNLOADS API =====
class DownloadsAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def facebook(self, url: str) -> Dict[str, Any]:
        """Download videos and media from Facebook posts and pages"""
        return self.client._make_request("GET", "/api/dl/facebook", {"url": url})

    def gitclone(self, url: str) -> Dict[str, Any]:
        """Clone GitHub repositories and download as zip files"""
        return self.client._make_request("GET", "/api/dl/gitclone", {"url": url})

    def instagram(self, url: str) -> Dict[str, Any]:
        """Download Instagram posts, reels, stories, and IGTV videos"""
        return self.client._make_request("GET", "/api/dl/instagram", {"url": url})

    def mediafire(self, url: str) -> Dict[str, Any]:
        """Download files directly from Mediafire sharing links"""
        return self.client._make_request("GET", "/api/dl/mediafire", {"url": url})

    def pinterest_search(self, text: str) -> Dict[str, Any]:
        """Search and download high-quality images from Pinterest"""
        return self.client._make_request("GET", "/api/dl/pinterest", {"text": text})

    def pinterest_video(self, url: str) -> Dict[str, Any]:
        """Download Pinterest videos without watermark"""
        return self.client._make_request("GET", "/api/dl/pinterest", {"url": url})

    def tiktok(self, url: str) -> Dict[str, Any]:
        """Download TikTok videos without watermark"""
        return self.client._make_request("GET", "/api/dl/tiktok", {"url": url})

    def twitter(self, url: str) -> Dict[str, Any]:
        """Download Twitter/X videos, images, and GIFs from tweets"""
        return self.client._make_request("GET", "/api/dl/twitter", {"url": url})

    def likee(self, url: str) -> Dict[str, Any]:
        """Download Likee videos without watermark"""
        return self.client._make_request("GET", "/api/dl/likee", {"url": url})

    def threads(self, url: str) -> Dict[str, Any]:
        """Download Threads videos without watermark"""
        return self.client._make_request("GET", "/api/dl/threads", {"url": url})

    def twitch(self, url: str) -> Dict[str, Any]:
        """Download Twitch videos by providing url"""
        return self.client._make_request("GET", "/api/dl/twitch", {"url": url})

    def wallbest(self, text: str, page: Optional[str] = None) -> Dict[str, Any]:
        """Download HD wallpapers with pagination support"""
        params = {"text": text}
        if page:
            params["page"] = page
        return self.client._make_request("GET", "/api/dl/wallbest", params)

    def wallcraft(self, text: str) -> Dict[str, Any]:
        """Alternative wallpaper source for HD images"""
        return self.client._make_request("GET", "/api/dl/wallcraft", {"text": text})

    def wallhaven(
        self,
        q: Optional[str] = None,
        sorting: Optional[str] = None,
        page: Optional[str] = None,
        purity: Optional[str] = None,
        categories: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Alternative wallpaper source for HD images with pagination support"""
        params = {}
        if q:
            params["q"] = q
        if sorting:
            params["sorting"] = sorting
        if page:
            params["page"] = page
        if purity:
            params["purity"] = purity
        if categories:
            params["categories"] = categories
        return self.client._make_request("GET", "/api/dl/wallhaven", params)

    def wikimedia(self, title: str) -> Dict[str, Any]:
        """Download media files from Wikimedia Commons"""
        return self.client._make_request("GET", "/api/dl/wikimedia", {"title": title})

    def youtube_audio(self, url: str, format: str = "mp3") -> Dict[str, Any]:
        """Extract and download audio from YouTube videos"""
        return self.client._make_request(
            "GET", "/api/dl/youtube", {"url": url, "format": format}
        )

    def youtube_video(self, url: str, format: str = "360") -> Dict[str, Any]:
        """Download YouTube videos in various quality options"""
        return self.client._make_request(
            "GET", "/api/dl/youtube", {"url": url, "format": format}
        )

    def bilibili(self, url: str) -> Dict[str, Any]:
        """Download Bilibili videos in Best quality options"""
        return self.client._make_request("GET", "/api/dl/bilibili", {"url": url})

    def linkedin(self, url: str) -> Dict[str, Any]:
        """Download LinkedIn videos without watermark"""
        return self.client._make_request("GET", "/api/dl/linkedin", {"url": url})

    def snapchat(self, url: str) -> Dict[str, Any]:
        """Download Snap Chat videos without watermark"""
        return self.client._make_request("GET", "/api/dl/snapchat", {"url": url})

    def sharechat(self, url: str) -> Dict[str, Any]:
        """Download Share Chat videos without watermark"""
        return self.client._make_request("GET", "/api/dl/sharechat", {"url": url})

    def snack_video(self, url: str) -> Dict[str, Any]:
        """Download Snack videos without watermark"""
        return self.client._make_request("GET", "/api/dl/snack", {"url": url})

    def reddit(self, url: str) -> Dict[str, Any]:
        """Download Reddit videos by providing url"""
        return self.client._make_request("GET", "/api/dl/reddit", {"url": url})

    def videezy(self, url: str) -> Dict[str, Any]:
        """Download stock videos from Videezy"""
        return self.client._make_request("GET", "/api/dl/videezy", {"url": url})

    def vidsplay(self, url: str) -> Dict[str, Any]:
        """Download stock videos from Vidsplay"""
        return self.client._make_request("GET", "/api/dl/vidsplay", {"url": url})

    def imdb(self, url: str) -> Dict[str, Any]:
        """Download IMDb videos by providing url"""
        return self.client._make_request("GET", "/api/dl/imdb", {"url": url})

    def ifunny(self, url: str) -> Dict[str, Any]:
        """Download iFunny videos without watermark"""
        return self.client._make_request("GET", "/api/dl/ifunny", {"url": url})

    def getty(self, url: str) -> Dict[str, Any]:
        """Download stock videos and images by providing url"""
        return self.client._make_request("GET", "/api/dl/getty", {"url": url})

    def pexels_videos(self, query: str) -> Dict[str, Any]:
        """Download free stock pexels videos"""
        return self.client._make_request("GET", "/api/pexels/videos", {"query": query})

    def pexels_images(self, query: str) -> Dict[str, Any]:
        """Download free stock pexels images"""
        return self.client._make_request("GET", "/api/pexels/images", {"query": query})

    def lorem_picsum(
        self,
        id: str,
        height: Optional[str] = None,
        width: Optional[str] = None,
        grayscale: Optional[str] = None,
        blur: Optional[str] = None,
    ) -> Dict[str, Any]:
        """The Lorem Ipsum for photos"""
        params = {"id": id}
        if height:
            params["height"] = height
        if width:
            params["width"] = width
        if grayscale:
            params["grayscale"] = grayscale
        if blur:
            params["blur"] = blur
        return self.client._make_request("GET", "/api/dl/picsum", params)

    def icon_finder(self, query: str) -> Dict[str, Any]:
        """Search and download icons in png, svg and ico format"""
        return self.client._make_request("GET", "/api/icon/finder", {"query": query})

    def pixabay_images(self, query: str, page: Optional[str] = None) -> Dict[str, Any]:
        """Search and download high quality images"""
        params = {"query": query}
        if page:
            params["page"] = page
        return self.client._make_request("GET", "/api/pixabay/images", params)

    def pixabay_videos(
        self, query: str, page: Optional[str] = None, category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search and download high quality videos"""
        params = {"query": query}
        if page:
            params["page"] = page
        if category:
            params["category"] = category
        return self.client._make_request("GET", "/api/pixabay/videos", params)

    def tenor_gifs(self, query: str) -> Dict[str, Any]:
        """Search and download gif and stickers from tenor"""
        return self.client._make_request("GET", "/api/dl/tenor", {"query": query})

    def pastebin(self, id: str, dl: Optional[str] = None) -> Dict[str, Any]:
        """Get pastebin content. If dl=true, return as text file"""
        params = {"id": id}
        if dl:
            params["dl"] = dl
        return self.client._make_request("GET", "/api/dl/pastebin", params)

    def google_image(self, query: str) -> Dict[str, Any]:
        """Search and download images from Google"""
        return self.client._make_request("GET", "/api/dl/gimage", {"query": query})

    def baidu_image(self, query: str, page: Optional[str] = None) -> Dict[str, Any]:
        """Search and download images from Baidu"""
        params = {"query": query}
        if page:
            params["page"] = page
        return self.client._make_request("GET", "/api/img/baidu", params)

    def daily_bing(self) -> Dict[str, Any]:
        """Get daily bing image with details"""
        return self.client._make_request("GET", "/api/img/dailybing")

    def istock(self, url: str) -> Dict[str, Any]:
        """Download stock videos and images from iStock"""
        return self.client._make_request("GET", "/api/dl/istock", {"url": url})

    def odysee(self, url: str) -> Dict[str, Any]:
        """Download Odysee videos without watermark"""
        return self.client._make_request("GET", "/api/dl/odysee", {"url": url})

    def alamy(self, url: str) -> Dict[str, Any]:
        """Download stock videos and images from alamy"""
        return self.client._make_request("GET", "/api/dl/alamy", {"url": url})
