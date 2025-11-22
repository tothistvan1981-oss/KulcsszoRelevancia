import re
import time
import requests
from collections import Counter
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


TI_STOPWORDS = {
    "a", "az", "és", "hogy", "mint", "is", "meg", "vagy", "de", "ha", "mert", "van",
    "volt", "lesz", "lenne", "ilyen", "olyan", "már", "még", "egy", "el", "fel", "le",
    "ki", "be", "nem", "igen", "ő", "én", "te", "mi", "ti", "ők", "ez", "az",
    "arra", "erre", "abból", "ebből", "arról", "erről", "amely", "amelyik", "aki",
    "akik", "nincs", "nagy", "kis", "sok", "kevés", "szerint", "által", "számára",
    "valami", "valaki", "itt", "ott", "tovább", "minden", "sem", "se", "hiszen",
    "tehát", "úgy", "kell", "kellett", "lett", "lehet", "csak", "mindenki", "senki"
}


class TIEredmeny:
    def __init__(self, url, description, keywords, szoveg_kulcs, title, load_time):
        self.url = url
        self.description = description
        self.keywords = keywords
        self.szoveg_kulcs = szoveg_kulcsszavak = szoveg_kulcs


        self.desc_szavak = TIAnalyzer.TI_metatag_szavak(description)
        self.key_szavak = TIAnalyzer.TI_metatag_szavak(keywords)


        self.relev_desc = TIAnalyzer.TI_meta_relevancia(self.desc_szavak, szoveg_kulcsszavak)
        self.relev_keys = TIAnalyzer.TI_meta_relevancia(self.key_szavak, szoveg_kulcsszavak)

        self.title = title
        self.load_time = load_time


class TIAnalyzer:


    @staticmethod
    def TI_letolt_oldal(url):
        try:
            start = time.time()
            r = requests.get(url, timeout=7, headers={'User-Agent': 'Mozilla/5.0'})
            elapsed = time.time() - start

            if r.status_code == 200:
                return r.text, elapsed
            return "", elapsed

        except:
            return "", 0


    @staticmethod
    def TI_kigyujt_meta_es_szoveg(html):
        soup = BeautifulSoup(html, "html.parser")

        description = ""
        keywords = ""
        title = ""

        for tag in soup.find_all("meta"):
            if tag.get("name") == "description":
                description = tag.get("content") or ""
            if tag.get("name") == "keywords":
                keywords = tag.get("content") or ""

        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        text = " ".join(list(soup.stripped_strings))
        return description, keywords, text, title


    @staticmethod
    def TI_belso_linkek(base_url, html):
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        netloc = urlparse(base_url).netloc

        for a in soup.find_all("a", href=True):
            full = urljoin(base_url, a["href"])
            u = urlparse(full)
            if u.netloc == netloc:
                links.add(full)

        return list(links)


    @staticmethod
    def TI_szovegbol_kulcsszavak(szoveg):
        szavak = re.findall(r'\b\w{3,}\b', szoveg.lower())
        szavak = [s for s in szavak if s not in TI_STOPWORDS and not s.isdigit()]
        return Counter(szavak)


    @staticmethod
    def TI_metatag_szavak(meta):
        return set(re.findall(r'\b\w{3,}\b', meta.lower()))


    @staticmethod
    def TI_meta_relevancia(meta_szavak, kulcsszavak):
        if not meta_szavak:
            return 0
        meta = set(meta_szavak)
        kulcs = set(kulcsszavak)
        metszi = meta & kulcs
        return int((len(metszi) / len(meta)) * 100)


    @staticmethod
    def TI_seo_tippek(title, description):
        tips = []

        if not title:
            tips.append("Nincs <title> tag.")
        elif len(title) < 10:
            tips.append("A title túl rövid.")
        elif len(title) > 60:
            tips.append("A title túl hosszú.")

        if not description:
            tips.append("Nincs meta description.")
        elif len(description) < 30:
            tips.append("A meta description túl rövid.")
        elif len(description) > 160:
            tips.append("A meta description túl hosszú.")

        return tips


    def TI_osszes_elemzes(self, base_url, maxoldal=5):
        html, load = self.TI_letolt_oldal(base_url)
        if not html:
            return []

        links = self.TI_belso_linkek(base_url, html)
        urls = [base_url] + links[:maxoldal - 1]

        eredmenyek = []

        for u in urls:
            html, load_time = self.TI_letolt_oldal(u)
            if not html:
                continue

            desc, keys, text, title = self.TI_kigyujt_meta_es_szoveg(html)
            kulcsok = self.TI_szovegbol_kulcsszavak(text)

            eredmenyek.append(
                TIEredmeny(u, desc, keys, kulcsok, title, load_time)
            )

        return eredmenyek


    @staticmethod
    def TI_osszesitett_stat(eredmenyek):
        osszes = Counter()
        meta_rel = []

        for e in eredmenyek:
            osszes += Counter(e.szoveg_kulcs)
            meta_rel.append((e.relev_desc, e.relev_keys))

        return osszes.most_common(20), meta_rel
