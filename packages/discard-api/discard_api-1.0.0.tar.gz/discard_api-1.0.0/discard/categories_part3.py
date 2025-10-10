"""
discard/categories_part3.py - More API categories (ImageMakers to Tools)
"""

from typing import Dict, Any, Optional, BinaryIO
from .client import DiscardClient


# ===== IMAGE MAKERS API =====
class ImageMakersAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def qrcode(self, text: str) -> Dict[str, Any]:
        """Easily generate simple qr code image from your data"""
        return self.client._make_request("GET", "/api/maker/qrcode", {"text": text})

    def qrtag(
        self,
        text: str,
        size: Optional[str] = None,
        color: Optional[str] = None,
        logo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate qr code using more advanced method"""
        params = {"text": text}
        if size:
            params["size"] = size
        if color:
            params["color"] = color
        if logo:
            params["logo"] = logo
        return self.client._make_request("GET", "/api/maker/qrtag", params)

    def text_to_pic(self, text: str) -> Dict[str, Any]:
        """Make beautiful logo images from your text"""
        return self.client._make_request("GET", "/api/maker/ttp", {"text": text})

    def design_font(self, text: str) -> Dict[str, Any]:
        """Make beautiful logo images from your text"""
        return self.client._make_request("GET", "/api/design/font", {"text": text})

    def captcha(self) -> Dict[str, Any]:
        """Generate random Captcha images"""
        return self.client._make_request("GET", "/api/maker/captcha")

    def custom_qr(
        self, text: str, size: Optional[str] = None, color: Optional[str] = None
    ) -> Dict[str, Any]:
        """Yet another alternative for advanced qr code image"""
        params = {"text": text}
        if size:
            params["size"] = size
        if color:
            params["color"] = color
        return self.client._make_request("GET", "/api/maker/customqr", params)

    def text_avatar(self, text: str, shape: Optional[str] = None) -> Dict[str, Any]:
        """Make Avatar from text"""
        params = {"text": text}
        if shape:
            params["shape"] = shape
        return self.client._make_request("GET", "/api/maker/avatar", params)

    def web_logo(self, url: str) -> Dict[str, Any]:
        """Download svg/ico of any website that exists"""
        return self.client._make_request("GET", "/api/maker/weblogo", {"url": url})

    def who_wins(self, url1: str, url2: str) -> Dict[str, Any]:
        """Make a who would win meme"""
        return self.client._make_request(
            "GET", "/api/maker/whowin", {"url1": url1, "url2": url2}
        )

    def quoted_lyo(
        self, text: str, name: str, profile: str, color: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make quoted image using your text, name, image url as profile and color"""
        params = {"text": text, "name": name, "profile": profile}
        if color:
            params["color"] = color
        return self.client._make_request("GET", "/api/maker/quoted", params)

    def qr_pro(
        self,
        text: str,
        size: Optional[str] = None,
        color: Optional[str] = None,
        logo: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Based on your own choice, scale QR code image"""
        params = {"text": text}
        if size:
            params["size"] = size
        if color:
            params["color"] = color
        if logo:
            params["logo"] = logo
        if caption:
            params["caption"] = caption
        return self.client._make_request("GET", "/api/qr/pro", params)

    def img_to_base64(self, file: BinaryIO) -> Dict[str, Any]:
        """Image to base64 converter"""
        return self.client._make_request(
            "POST", "/api/img2base64", files={"file": file}
        )

    def base64_to_img(self, data: str) -> Dict[str, Any]:
        """Base64 to image converter"""
        return self.client._make_request("GET", "/api/img2base64", {"data": data})

    def barcode_128(self, text: str) -> Dict[str, Any]:
        """Easily scale Code128 barcode image"""
        return self.client._make_request("GET", "/api/barcode/code", {"text": text})

    def barcode_ean(self, text: str) -> Dict[str, Any]:
        """EAN-13 requires a 12-digit numeric string"""
        return self.client._make_request("GET", "/api/barcode/ean", {"text": text})

    def barcode_qr(self, text: str) -> Dict[str, Any]:
        """Easily scale Simple QR code image"""
        return self.client._make_request("GET", "/api/barcode/qr", {"text": text})

    def emoji_mosaic(
        self, file: BinaryIO, width: str, palette: str, format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Converts your image into emoji art"""
        data = {"width": width, "palette": palette}
        if format:
            data["format"] = format
        return self.client._make_request(
            "POST", "/api/emoji/mosaic", data=data, files={"file": file}
        )

    def emoji_translate(self, text: str) -> Dict[str, Any]:
        """Translate common words into emojis"""
        return self.client._make_request("GET", "/api/emoji/translate", {"text": text})

    def emoji_replace(self, text: str) -> Dict[str, Any]:
        """Replace vowels (or custom chars) with emojis"""
        return self.client._make_request("GET", "/api/emoji/replace", {"text": text})

    def emoji_mirror(self, text: str) -> Dict[str, Any]:
        """Reverse text or emoji sequences"""
        return self.client._make_request("GET", "/api/emoji/mirror", {"text": text})

    def emoji_rainbow(self, text: str) -> Dict[str, Any]:
        """Insert rainbow emoji between words"""
        return self.client._make_request("GET", "/api/emoji/rainbow", {"text": text})

    def emoji_mix(self, e1: str, e2: str) -> Dict[str, Any]:
        """Mix two emojis into a unique sticker"""
        return self.client._make_request("GET", "/api/emoji/mix", {"e1": e1, "e2": e2})

    def carbon_image(self, code: str, bg: Optional[str] = None) -> Dict[str, Any]:
        """For generating code snippet images"""
        params = {"code": code}
        if bg:
            params["bg"] = bg
        return self.client._make_request("GET", "/api/maker/carbon", params)

    def welcome_image(
        self, background: str, avatar: str, text1: str, text2: str, text3: str
    ) -> Dict[str, Any]:
        """Generate Welcome Cards"""
        return self.client._make_request(
            "GET",
            "/api/maker/welcome",
            {
                "background": background,
                "avatar": avatar,
                "text1": text1,
                "text2": text2,
                "text3": text3,
            },
        )


# ===== MUSIC API =====
class MusicAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def spotify_search(self, query: str) -> Dict[str, Any]:
        """Search for Spotify tracks"""
        return self.client._make_request("GET", "/api/search/spotify", {"query": query})

    def spotify_download(self, url: str) -> Dict[str, Any]:
        """Download tracks from Spotify urls"""
        return self.client._make_request("GET", "/api/dl/spotify", {"url": url})

    def soundcloud_search(self, query: str) -> Dict[str, Any]:
        """Search for sound cloud tracks"""
        return self.client._make_request(
            "GET", "/api/search/soundcloud", {"query": query}
        )

    def soundcloud_download(self, url: str) -> Dict[str, Any]:
        """Download sound cloud tracks by providing url"""
        return self.client._make_request("GET", "/api/dl/soundcloud", {"url": url})

    def lyrics(self, song: str) -> Dict[str, Any]:
        """Get song lyrics"""
        return self.client._make_request("GET", "/api/music/lyrics", {"song": song})

    def ringtones(self, title: str) -> Dict[str, Any]:
        """Search and Download mobile ringtones and notification sounds"""
        return self.client._make_request("GET", "/api/dl/ringtone", {"title": title})

    def search_sound(self, query: str) -> Dict[str, Any]:
        """Search for sounds"""
        return self.client._make_request("GET", "/api/search/sound", {"query": query})

    def preview_sound(self, id: str) -> Dict[str, Any]:
        """Get the high-quality MP3 preview of sounds"""
        return self.client._make_request("GET", "/api/dl/sound", {"id": id})

    def deezer_search(
        self,
        track: Optional[str] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for tracks, albums, artists from deezer"""
        params = {}
        if track:
            params["track"] = track
        if artist:
            params["artist"] = artist
        if album:
            params["album"] = album
        if id:
            params["id"] = id
        return self.client._make_request("GET", "/api/search/deezer", params)

    def musicbrainz_search(
        self, entity: str, query: Optional[str] = None, id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search MusicBrainz database"""
        params = {"entity": entity}
        if query:
            params["query"] = query
        if id:
            params["id"] = id
        return self.client._make_request("GET", "/api/search/musicbrainz", params)

    def openwhyd(self, username: str, limit: Optional[str] = None) -> Dict[str, Any]:
        """Get OpenWhyd user playlists"""
        params = {"username": username}
        if limit:
            params["limit"] = limit
        return self.client._make_request("GET", "/api/search/openwhyd", params)


# ===== JOKES API =====
class JokesAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def dad(self) -> Dict[str, Any]:
        """Classic dad jokes that are so bad they're good"""
        return self.client._make_request("GET", "/api/joke/dad")

    def general(self) -> Dict[str, Any]:
        """Random general jokes for everyday entertainment"""
        return self.client._make_request("GET", "/api/joke/general")

    def knock(self) -> Dict[str, Any]:
        """Interactive knock-knock jokes with classic format"""
        return self.client._make_request("GET", "/api/joke/knock")

    def programming(self) -> Dict[str, Any]:
        """Jokes specifically for programmers"""
        return self.client._make_request("GET", "/api/joke/programming")

    def misc(self) -> Dict[str, Any]:
        """Miscellaneous Jokes"""
        return self.client._make_request("GET", "/api/joke/misc")

    def coding(self) -> Dict[str, Any]:
        """Specifically for Developers"""
        return self.client._make_request("GET", "/api/joke/coding")

    def spooky(self) -> Dict[str, Any]:
        """Halloween related Jokes"""
        return self.client._make_request("GET", "/api/joke/spooky")

    def dark(self) -> Dict[str, Any]:
        """Dark Jokes"""
        return self.client._make_request("GET", "/api/joke/dark")

    def christmas(self) -> Dict[str, Any]:
        """Christmas related Jokes"""
        return self.client._make_request("GET", "/api/joke/Christmas")

    def random(self) -> Dict[str, Any]:
        """Random Jokes"""
        return self.client._make_request("GET", "/api/joke/random")

    def animal(self) -> Dict[str, Any]:
        """Animal related Jokes"""
        return self.client._make_request("GET", "/api/joke/animal")

    def career(self) -> Dict[str, Any]:
        """Career related Jokes"""
        return self.client._make_request("GET", "/api/joke/career")

    def celebrity(self) -> Dict[str, Any]:
        """Celebrity related Jokes"""
        return self.client._make_request("GET", "/api/joke/celebrity")

    def explicit(self) -> Dict[str, Any]:
        """Explicit Jokes"""
        return self.client._make_request("GET", "/api/joke/explicit")

    def fashion(self) -> Dict[str, Any]:
        """Fashion Related Jokes"""
        return self.client._make_request("GET", "/api/joke/fashion")

    def food(self) -> Dict[str, Any]:
        """Food related Jokes"""
        return self.client._make_request("GET", "/api/joke/food")

    def history(self) -> Dict[str, Any]:
        """History related Jokes"""
        return self.client._make_request("GET", "/api/joke/history")

    def money(self) -> Dict[str, Any]:
        """Money related Jokes"""
        return self.client._make_request("GET", "/api/joke/money")

    def movie(self) -> Dict[str, Any]:
        """Movie related Jokes"""
        return self.client._make_request("GET", "/api/joke/movie")

    def music(self) -> Dict[str, Any]:
        """Music related Jokes"""
        return self.client._make_request("GET", "/api/joke/music")

    def science(self) -> Dict[str, Any]:
        """Science related Jokes"""
        return self.client._make_request("GET", "/api/joke/science")

    def sport(self) -> Dict[str, Any]:
        """Sports related Jokes"""
        return self.client._make_request("GET", "/api/joke/sport")

    def travel(self) -> Dict[str, Any]:
        """Travel related Jokes"""
        return self.client._make_request("GET", "/api/joke/travel")


# ===== IMAGES API =====
class ImagesAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def couple(self) -> Dict[str, Any]:
        """Get random couple pp images in high quality"""
        return self.client._make_request("GET", "/api/img/couple")

    def pizza(self) -> Dict[str, Any]:
        """Get random Pizza image in high quality"""
        return self.client._make_request("GET", "/api/images/pizza")

    def burger(self) -> Dict[str, Any]:
        """Get random Burger image in high quality"""
        return self.client._make_request("GET", "/api/images/burger")

    def dosa(self) -> Dict[str, Any]:
        """Get random Dosa image in high quality"""
        return self.client._make_request("GET", "/api/images/dosa")

    def pasta(self) -> Dict[str, Any]:
        """Get random Pasta image in high quality"""
        return self.client._make_request("GET", "/api/images/pasta")

    def biryani(self) -> Dict[str, Any]:
        """Get random Biryani image in high quality"""
        return self.client._make_request("GET", "/api/images/biryani")

    def islamic(self) -> Dict[str, Any]:
        """Get random Islamic image in high quality"""
        return self.client._make_request("GET", "/api/img/islamic")

    def tech(self) -> Dict[str, Any]:
        """Get random Technology image in high quality"""
        return self.client._make_request("GET", "/api/img/tech")

    def game(self) -> Dict[str, Any]:
        """Get random Gaming image in high quality"""
        return self.client._make_request("GET", "/api/img/game")

    def mountain(self) -> Dict[str, Any]:
        """Get random Mountain image in high quality"""
        return self.client._make_request("GET", "/api/img/mountain")

    def programming(self) -> Dict[str, Any]:
        """Get random Programming image in high quality"""
        return self.client._make_request("GET", "/api/img/programming")

    def cyberspace(self) -> Dict[str, Any]:
        """Get random Cyberspace image in high quality"""
        return self.client._make_request("GET", "/api/img/cyberspace")

    def wallpc(self) -> Dict[str, Any]:
        """Get random wallpaper for Pc in high quality"""
        return self.client._make_request("GET", "/api/img/wallpc")

    def messi(self) -> Dict[str, Any]:
        """Get random high quality image of Messi"""
        return self.client._make_request("GET", "/api/img/messi")

    def ronaldo(self) -> Dict[str, Any]:
        """Get random high quality image of Ronaldo"""
        return self.client._make_request("GET", "/api/img/ronaldo")

    def coffee(self) -> Dict[str, Any]:
        """Get random high quality Coffee image"""
        return self.client._make_request("GET", "/api/img/coffee")

    def cat(self) -> Dict[str, Any]:
        """Get random high quality Cat image"""
        return self.client._make_request("GET", "/api/img/cat")

    def dog(self) -> Dict[str, Any]:
        """Get random high quality Dog image"""
        return self.client._make_request("GET", "/api/img/dog")

    def yesno(self) -> Dict[str, Any]:
        """Get random [Yes,No] image"""
        return self.client._make_request("GET", "/api/img/yesno")

    def fox(self) -> Dict[str, Any]:
        """Get random high quality image of Fox"""
        return self.client._make_request("GET", "/api/img/fox")

    def notexist(self) -> Dict[str, Any]:
        """Get random high quality image of persons who don't exist"""
        return self.client._make_request("GET", "/api/img/notexist")


# ===== FACTS API =====
class FactsAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def date_fact(
        self, month: Optional[str] = None, day: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get fact about a specific date or random"""
        params = {}
        if month and day:
            params = {"month": month, "day": day}
            return self.client._make_request("GET", "/api/fact/date", params)
        return self.client._make_request("GET", "/api/date/fact")

    def year_fact(self, year: Optional[str] = None) -> Dict[str, Any]:
        """Get fact about a specific year or random"""
        if year:
            return self.client._make_request("GET", "/api/fact/year", {"year": year})
        return self.client._make_request("GET", "/api/year/fact")

    def math_fact(self, number: Optional[str] = None) -> Dict[str, Any]:
        """Get fact about a specific number or random"""
        if number:
            return self.client._make_request(
                "GET", "/api/fact/math", {"number": number}
            )
        return self.client._make_request("GET", "/api/math/fact")

    def trivia_fact(self, number: Optional[str] = None) -> Dict[str, Any]:
        """Get trivia about a specific number or random"""
        if number:
            return self.client._make_request(
                "GET", "/api/fact/trivia", {"number": number}
            )
        return self.client._make_request("GET", "/api/trivia/fact")

    def useless_facts(self) -> Dict[str, Any]:
        """Get random Useless facts"""
        return self.client._make_request("GET", "/api/fact/useless")

    def today_facts(self) -> Dict[str, Any]:
        """Get useless facts about present day"""
        return self.client._make_request("GET", "/api/fact/today")


# ===== FAKER API =====
class FakerAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def fake_user(self) -> Dict[str, Any]:
        """Generate fake user"""
        return self.client._make_request("GET", "/api/fake/user")

    def fake_users(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        gender: Optional[str] = None,
        seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake users"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if gender:
            params["_gender"] = gender
        if seed:
            params["_seed"] = seed
        return self.client._make_request("GET", "/api/fake/users", params)

    def fake_addresses(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        country_code: Optional[str] = None,
        seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake addresses"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if country_code:
            params["_country_code"] = country_code
        if seed:
            params["_seed"] = seed
        return self.client._make_request("GET", "/api/fake/addresses", params)

    def fake_texts(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        characters: Optional[str] = None,
        seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake texts"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if characters:
            params["_characters"] = characters
        if seed:
            params["_seed"] = seed
        return self.client._make_request("GET", "/api/fake/texts", params)

    def fake_persons(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        gender: Optional[str] = None,
        seed: Optional[str] = None,
        birthday_start: Optional[str] = None,
        birthday_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake persons"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if gender:
            params["_gender"] = gender
        if seed:
            params["_seed"] = seed
        if birthday_start:
            params["_birthday_start"] = birthday_start
        if birthday_end:
            params["_birthday_end"] = birthday_end
        return self.client._make_request("GET", "/api/fake/persons", params)

    def fake_books(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake books"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if seed:
            params["_seed"] = seed
        return self.client._make_request("GET", "/api/fake/books", params)

    def fake_images(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        type: Optional[str] = None,
        seed: Optional[str] = None,
        width: Optional[str] = None,
        height: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake images"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if type:
            params["type"] = type
        if seed:
            params["_seed"] = seed
        if width:
            params["width"] = width
        if height:
            params["height"] = height
        return self.client._make_request("GET", "/api/fake/images", params)

    def fake_credits(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake credit cards"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if seed:
            params["_seed"] = seed
        return self.client._make_request("GET", "/api/fake/credits", params)

    def fake_companies(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake companies"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if seed:
            params["_seed"] = seed
        return self.client._make_request("GET", "/api/fake/companies", params)

    def fake_places(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake places"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if seed:
            params["_seed"] = seed
        return self.client._make_request("GET", "/api/fake/places", params)

    def fake_products(
        self,
        quantity: Optional[str] = None,
        locale: Optional[str] = None,
        seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fake products"""
        params = {}
        if quantity:
            params["_quantity"] = quantity
        if locale:
            params["_locale"] = locale
        if seed:
            params["_seed"] = seed
        return self.client._make_request("GET", "/api/fake/products", params)


# ===== TOOLS API =====
class ToolsAPI:
    def __init__(self, client: DiscardClient):
        self.client = client

    def compress(
        self,
        type: str,
        text: Optional[str] = None,
        url: Optional[str] = None,
        file: Optional[BinaryIO] = None,
    ) -> Dict[str, Any]:
        """Compress text, url or file"""
        if file:
            return self.client._make_request(
                "POST", "/api/compress", data={"type": type}, files={"file": file}
            )
        params = {"type": type}
        if text:
            params["text"] = text
        if url:
            params["url"] = url
        return self.client._make_request("GET", "/api/compress", params)

    def decompress(
        self,
        type: str,
        data: Optional[str] = None,
        url: Optional[str] = None,
        file: Optional[BinaryIO] = None,
    ) -> Dict[str, Any]:
        """Decompress text, url or file"""
        if file:
            return self.client._make_request(
                "POST", "/api/decompress", data={"type": type}, files={"file": file}
            )
        params = {"type": type}
        if data:
            params["data"] = data
        if url:
            params["url"] = url
        return self.client._make_request("GET", "/api/decompress", params)

    def bank_logo(self, domain: str) -> Dict[str, Any]:
        """Get bank logos and branding information by domain"""
        return self.client._make_request(
            "GET", "/api/tools/banklogo", {"domain": domain}
        )

    def detect_lang(self, text: str) -> Dict[str, Any]:
        """Automatically detect the language of input text"""
        return self.client._make_request(
            "GET", "/api/tools/detect-lang", {"text": text}
        )

    def dictionary(self, word: str) -> Dict[str, Any]:
        """Get word definitions, pronunciation, and usage examples"""
        return self.client._make_request("GET", "/api/tools/dictionary", {"word": word})

    def dictionary2(self, word: str) -> Dict[str, Any]:
        """Alternative dictionary lookup"""
        return self.client._make_request("GET", "/api/tools/dict", {"word": word})

    def mathematics(self, expr: str) -> Dict[str, Any]:
        """Solve mathematical expressions and equations"""
        return self.client._make_request("GET", "/api/tools/math", {"expr": expr})

    def math_quiz(
        self,
        difficulty: Optional[str] = None,
        steps: Optional[str] = None,
        allow_negative: Optional[str] = None,
        num_questions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate math quiz"""
        params = {}
        if difficulty:
            params["difficulty"] = difficulty
        if steps:
            params["steps"] = steps
        if allow_negative:
            params["allow_negative"] = allow_negative
        if num_questions:
            params["num_questions"] = num_questions
        return self.client._make_request("GET", "/api/tools/math", params)

    def site_preview(self, url: str) -> Dict[str, Any]:
        """Generate website previews with metadata and screenshots"""
        return self.client._make_request("GET", "/api/tools/preview", {"url": url})

    def screenshot(self, url: str) -> Dict[str, Any]:
        """Capture full-page screenshots of websites"""
        return self.client._make_request("GET", "/api/tools/ssweb", {"url": url})

    def ss_computer(self, url: str) -> Dict[str, Any]:
        """Get screenshot of any web page (computer view)"""
        return self.client._make_request("GET", "/api/tools/sspc", {"url": url})

    def ss_mobile(self, url: str) -> Dict[str, Any]:
        """Get screenshot of any web page (mobile view)"""
        return self.client._make_request("GET", "/api/tools/ssmobile", {"url": url})

    def style_text(self, text: str) -> Dict[str, Any]:
        """Apply various text styling and formatting options"""
        return self.client._make_request("GET", "/api/tools/styletext", {"text": text})

    def morse(self, text: str, mode: str) -> Dict[str, Any]:
        """Morse text styling and decoding option"""
        return self.client._make_request(
            "GET", "/api/tools/morse", {"text": text, "mode": mode}
        )

    def reverse_text(self, text: str) -> Dict[str, Any]:
        """Reverse the text you provided"""
        return self.client._make_request("GET", "/api/tools/reverse", {"text": text})

    def read_qr(self, image: BinaryIO) -> Dict[str, Any]:
        """Get qr code images content"""
        return self.client._make_request(
            "POST", "/api/tools/readqr", files={"image": image}
        )

    def translate(self, text: str, to: str) -> Dict[str, Any]:
        """Translate text between different languages"""
        return self.client._make_request(
            "GET", "/api/tools/translate", {"text": text, "to": to}
        )

    def translate2(self, text: str, lang: Optional[str] = None) -> Dict[str, Any]:
        """Alternative translation method"""
        params = {"text": text}
        if lang:
            params["lang"] = lang
        return self.client._make_request("GET", "/api/go/translate", params)

    def text_to_speech(self, text: str, lang: Optional[str] = None) -> Dict[str, Any]:
        """Generate audio of given text"""
        params = {"text": text}
        if lang:
            params["lang"] = lang
        return self.client._make_request("GET", "/api/tools/tts", params)

    def website_seo(self, url: str, lang: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed information about website SEO status"""
        params = {"url": url}
        if lang:
            params["lang"] = lang
        return self.client._make_request("GET", "/api/tools/seo", params)

    def ping(self, url: str, lang: Optional[str] = None) -> Dict[str, Any]:
        """Ping any url and get detailed information"""
        params = {"url": url}
        if lang:
            params["lang"] = lang
        return self.client._make_request("GET", "/api/tools/ping", params)

    def simple_ping(self, url: str) -> Dict[str, Any]:
        """Simple ping for any url"""
        return self.client._make_request("GET", "/api/simple/ping", {"url": url})

    def simple_counter(self, count: str) -> Dict[str, Any]:
        """Simple counter"""
        return self.client._make_request("GET", "/api/tools/count", {"count": count})

    def whois_lookup(self, domain: str) -> Dict[str, Any]:
        """Fetch WHOIS Lookup"""
        return self.client._make_request("GET", "/api/tools/whois", {"domain": domain})

    def handwriting(self, text: str) -> Dict[str, Any]:
        """Generate hand written text image"""
        return self.client._make_request("GET", "/api/tools/handwrite", {"text": text})

    def to_ascii(self, file: BinaryIO) -> Dict[str, Any]:
        """Convert image to ASCII"""
        return self.client._make_request(
            "POST", "/api/tools/ascii", files={"file": file}
        )

    def random_uuid(self) -> Dict[str, Any]:
        """Random UUID generator"""
        return self.client._make_request("GET", "/api/tools/uuid")

    def generate_hash(self, data: str, algo: str) -> Dict[str, Any]:
        """Generate hash using specific algorithm"""
        return self.client._make_request(
            "GET", "/api/tools/hash", {"data": data, "algo": algo}
        )

    def strong_password(self) -> Dict[str, Any]:
        """Will Suggest strong password"""
        return self.client._make_request("GET", "/api/tools/password")

    def text_stats(self, text: str) -> Dict[str, Any]:
        """String info text stats"""
        return self.client._make_request("GET", "/api/tools/string", {"text": text})

    def word_count(self, text: str) -> Dict[str, Any]:
        """String info words counter"""
        return self.client._make_request("GET", "/api/word/count", {"text": text})

    def port_scanner(self, host: str, subs: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve Open Ports"""
        params = {"host": host}
        if subs:
            params["subs"] = subs
        return self.client._make_request("GET", "/api/tools/port", params)

    def unit_convert(self, from_unit: str, to_unit: str, value: str) -> Dict[str, Any]:
        """Unit converter"""
        return self.client._make_request(
            "GET",
            "/api/convert/unit",
            {"from": from_unit, "to": to_unit, "value": value},
        )

    def markdown_to_html(self, markdown: str) -> Dict[str, Any]:
        """Convert Markdown text into HTML"""
        return self.client._make_request(
            "POST", "/api/tools/markdown", json_data={"markdown": markdown}
        )

    def exif_reader(self, image: BinaryIO) -> Dict[str, Any]:
        """Read EXIF data from image"""
        return self.client._make_request(
            "POST", "/api/tools/exif", files={"image": image}
        )

    def minify_css(self, css: str) -> Dict[str, Any]:
        """Minify CSS input"""
        return self.client._make_request(
            "POST", "/api/tools/minifycss", json_data={"css": css}
        )

    def json_beautify(self, json_str: str) -> Dict[str, Any]:
        """Beautify or minify JSON input"""
        return self.client._make_request(
            "POST", "/api/json/format", json_data={"json": json_str}
        )
