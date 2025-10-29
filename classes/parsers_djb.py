# classes/djb_unified.py
import os, time, re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("BASE_URL")
ROOT = os.getenv("ROOT_URL")
HEADERS = {"User-Agent": "SusanaNewsBot/1.0 (nachrichten.pena-abogados.com)"}

class DJBUnified:
    def __init__(self, base_url=BASE, max_items=30, follow_detail=True, delay=0.8):
        self.base_url = base_url
        self.max_items = max_items     # cuántos ítems del listado procesar
        self.follow_detail = follow_detail  # entrar al detalle para fecha/resumen
        self.delay = delay             # espera entre requests
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _get(self, url, timeout=20):
        r = self.session.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text

    def _normalize_space(self, s):
        return re.sub(r"\s+", " ", s or "").strip()

    def _absolute(self, href):
        if not href:
            return None
        return href if href.startswith("http") else urljoin(ROOT, href)

    # 1) LIST PAGE: títulos + links + resume
    def _parse_list_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        items = []

        cards = soup.select("div.article[itemtype='http://schema.org/Article'], div.article")
        for card in cards:
        # Título + URL dentro de .news-header (o h3 como fallback)
            a = card.select_one(".news-header a")
            if not a:
                continue
            title = self._normalize_space(a.get_text())
            href = self._absolute(a.get("href"))
            if not title or not href or href == "#":
                continue

            prev_el = card.select_one(".news-content-preview")
            resume = self._normalize_space(prev_el.get_text()) if prev_el else None

            date_txt = None
            time_el = card.find('time', itemprop="datePublished")
            if time_el:
                date_txt = time_el.get("datetime") or time_el.get_text(" ", strip=True)

            else:
                span_el = card.select_one(".news-content-date, .article-date, .date")
                if span_el:
                    raw = span_el.get_text(" ", strip=True)
                    date_txt = raw.split(" - ", 1)[0].strip()

            date_txt = self._normalize_space(date_txt)


            items.append({
                "title": title,
                "url": href,
                "date": date_txt,
                "resume": resume,
                "source": "djb.de/familienrecht",
                "quelle": BASE
            })
            if len(items) >= self.max_items:
                break

        return items

    # 2) DETAIL PAGE: fecha + resumen (+ imagen si aparece)
    def _enrich_from_detail(self, url):
        try:
            html = self._get(url)
        except Exception:
            return {}

        soup = BeautifulSoup(html, "html.parser")
        result = {}

        # Fecha: <time>, .news-content-date, meta
        t = soup.find('time', itemprop="datePublished")
        if t and t.get_text(strip=True):
            result["date"] = self._normalize_space(t.get_text(strip=True))
        else:
            el = soup.select_one("time", itemprop="datePublished")
            if el:
                result["date"] = self._normalize_space(el.get_text())

        # Resumen: primer párrafo “largo” del contenido principal
        for p in soup.select(".news-content"):
            txt = self._normalize_space(p.get_text())
            if len(txt) >= 10:
                result["resume"] = txt
                break
        return result

    def fetch_items(self):
        # Soporta /familienrecht y paginaciones como /familienrecht/seite-2
        list_urls = [self.base_url]

        all_items = []
        for list_url in list_urls:
            try:
                list_html = self._get(list_url)
            except Exception as e:
                print(f"[WARN] list fetch failed: {e}")
                continue

            items = self._parse_list_page(list_html)
            if not self.follow_detail:
                all_items.extend(items)
                continue

            # Enriquecer desde el detalle (con delay educado)
            for item in items:
                time.sleep(self.delay)
                info = self._enrich_from_detail(item["url"])
                item.update(info)
                all_items.append(item)

        # Deduplicar por URL
        seen, uniq = set(), []
        for item in all_items:
            if item["url"] in seen:
                continue
            seen.add(item["url"])
            uniq.append(item)

        return uniq
    
if __name__ == "__main__":
    parser = DJBUnified()
    items = parser.fetch_items()
    for item in items:
        print(item)
