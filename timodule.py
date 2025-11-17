import re
from collections import Counter
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup

TI_STOPWORDS = {
    "a", "az", "és", "hogy", "mint", "is", "meg", "vagy", "de", "ha", "mert", "van",
    "volt", "lesz", "lenne", "ilyen", "olyan", "már", "még", "egy", "el", "fel", "le",
    "ki", "be", "nem", "igen", "nem", "ő", "én", "te", "mi", "ti", "ők", "ez", "az",
    "arra", "erre", "abból", "ebből", "arról", "erről", "amely", "amelyik", "aki", "akik",
    "nincs", "nagy", "kis", "sok", "kevés", "szerint", "által", "számára", "valami",
    "valaki", "itt", "ott", "tovább", "minden", "sem", "se", "hiszen", "tehát", "úgy",
    "kell", "kellett", "lesz", "lett", "lehet", "lehetett", "csak", "mindenki", "senki"
}
def TI_kigyujt_meta_es_szoveg(html):
    soup = BeautifulSoup(html, "html.parser")
    description = ""
    keywords = ""
    for tag in soup.find_all("meta"):
        if tag.get("name") == "description":
            description = tag.get("content") or ""
        if tag.get("name") == "keywords":
            keywords = tag.get("content") or ""
    texts = [t for t in soup.stripped_strings]
    szoveg = " ".join(texts)
    return description, keywords, szoveg


def TI_belso_linkek(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    netloc = urlparse(base_url).netloc
    for a in soup.find_all("a", href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        p = urlparse(full_url)
        if p.netloc == netloc and full_url.startswith('http'):
            links.add(full_url)
    return list(links)

def TI_szovegbol_kulcsszavak(szoveg):
    szavak = re.findall(r'\b\w{3,}\b', szoveg.lower())
    szavak = [s for s in szavak if s not in TI_STOPWORDS and not s.isdigit()]
    return Counter(szavak)

def TI_metatag_szavak(meta):
    return set(re.findall(r'\b\w{3,}\b', meta.lower()))

def TI_meta_relevancia(meta_szavak, kulcsszavak):
    if not meta_szavak:
        return 0
    meta_set = set(meta_szavak)
    kulcs_set = set(kulcsszavak)
    metakulcsok = meta_set & kulcs_set
    return int(len(metakulcsok) / len(meta_set) * 100) if meta_set else 0

def TI_osszesitett_stat(eredmenyek):
    osszes_kulcs = Counter()
    meta_relev = []
    for e in eredmenyek:
        osszes_kulcs += Counter(e.szoveg_kulcs)
        meta_relev.append((e.relev_desc, e.relev_keys))
    return osszes_kulcs.most_common(20), meta_relev

class TIEredmeny:
    def __init__(self, url, description, keywords, szoveg_kulcs):
        self.url = url
        self.description = description
        self.keywords = keywords
        self.szoveg_kulcs = szoveg_kulcs
        self.desc_szavak = TI_metatag_szavak(description)
        self.key_szavak = TI_metatag_szavak(keywords)
        self.relev_desc = TI_meta_relevancia(self.desc_szavak, szoveg_kulcs)
        self.relev_keys = TI_meta_relevancia(self.key_szavak, szoveg_kulcs)