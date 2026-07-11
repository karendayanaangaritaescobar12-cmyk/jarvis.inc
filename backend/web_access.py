import httpx
import re
import json
import urllib.parse
from bs4 import BeautifulSoup
from typing import Optional, List, Dict


class WebAccess:
    def __init__(self):
        self.client = httpx.Client(
            timeout=15,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

    def search_google(self, query: str, num_results: int = 5) -> str:
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=es&gl=es"
            r = self.client.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            results = []
            for g in soup.select("div.g"):
                title_el = g.select_one("h3")
                link_el = g.select_one("a")
                snippet_el = g.select_one("div.VwiC3b, div[data-sncf], span.aCOpRe")
                if title_el and link_el:
                    title = title_el.get_text(strip=True)
                    link = link_el.get("href", "")
                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                    if link.startswith("/url?"):
                        link = urllib.parse.parse_qs(urllib.parse.urlparse(link).query).get("q", [""])[0]
                    if link.startswith("http"):
                        results.append(f"**{title}**\n{link}\n{snippet}")
                if len(results) >= num_results:
                    break
            if not results:
                return self.search_duckduckgo(query, num_results)
            return f"Resultados para '{query}':\n\n" + "\n\n".join(results)
        except Exception as e:
            return self.search_duckduckgo(query, num_results)

    def search_duckduckgo(self, query: str, num_results: int = 5) -> str:
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            r = self.client.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            results = []
            for result in soup.select(".result"):
                title_el = result.select_one(".result__title a, .result__a")
                snippet_el = result.select_one(".result__snippet")
                if title_el:
                    title = title_el.get_text(strip=True)
                    link = title_el.get("href", "")
                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                    results.append(f"**{title}**\n{link}\n{snippet}")
                if len(results) >= num_results:
                    break
            if not results:
                return f"No encontré resultados para '{query}'."
            return f"Resultados para '{query}':\n\n" + "\n\n".join(results)
        except Exception as e:
            return f"Error buscando: {str(e)}"

    def fetch_page(self, url: str, max_chars: int = 3000) -> str:
        try:
            if not url.startswith("http"):
                url = "https://" + url
            r = self.client.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
                tag.decompose()
            title = soup.title.get_text(strip=True) if soup.title else url
            text = soup.get_text(separator="\n", strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' {2,}', ' ', text)
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n[... contenido truncado ...]"
            return f"**{title}**\nFuente: {url}\n\n{text}"
        except Exception as e:
            return f"Error accediendo a {url}: {str(e)}"

    def get_news(self, query: str = "noticias", num_results: int = 5) -> str:
        try:
            url = f"https://news.google.com/search?q={urllib.parse.quote(query)}&hl=es-419&gl=ES&ceid=ES:es-419"
            r = self.client.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            results = []
            for article in soup.select("article"):
                title_el = article.select_one("a[href]")
                if title_el:
                    title = title_el.get_text(strip=True)
                    link = title_el.get("href", "")
                    if link.startswith("./"):
                        link = "https://news.google.com" + link[1:]
                    results.append(f"- {title}\n  {link}")
                if len(results) >= num_results:
                    break
            if not results:
                return self.search_duckduckgo(f"noticias {query}", num_results)
            return f"Últimas noticias sobre '{query}':\n\n" + "\n\n".join(results)
        except Exception as e:
            return self.search_duckduckgo(f"noticias {query}", num_results)

    def get_weather(self, city: str) -> str:
        try:
            url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1&lang=es"
            r = self.client.get(url)
            data = r.json()
            current = data.get("current_condition", [{}])[0]
            temp = current.get("temp_C", "?")
            feels = current.get("FeelsLikeC", "?")
            desc = current.get("lang_es", [{}])[0].get("value", current.get("weatherDesc", [{}])[0].get("value", "?"))
            humidity = current.get("humidity", "?")
            wind = current.get("windspeedKmph", "?")
            tomorrow = data.get("weather", [{}])[0]
            max_temp = tomorrow.get("maxtempC", "?")
            min_temp = tomorrow.get("mintempC", "?")
            return (
                f"Clima en {city}:\n"
                f"Temperatura: {temp}°C (sensación: {feels}°C)\n"
                f"Condición: {desc}\n"
                f"Humedad: {humidity}%\n"
                f"Viento: {wind} km/h\n"
                f"Máx: {max_temp}°C / Mín: {min_temp}°C"
            )
        except Exception as e:
            return f"Error obteniendo clima: {str(e)}"

    def get_definition(self, word: str) -> str:
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
            r = self.client.get(url)
            if r.status_code == 200:
                data = r.json()
                if data:
                    entry = data[0]
                    meanings = entry.get("meanings", [])
                    result = f"**{entry.get('word', word)}**"
                    for m in meanings[:3]:
                        pos = m.get("partOfSpeech", "")
                        defs = m.get("definitions", [])
                        if defs:
                            result += f"\n\n*{pos}*: {defs[0].get('definition', '')}"
                            if defs[0].get("example"):
                                result += f"\n  Ejemplo: \"{defs[0]['example']}\""
                    return result
            return f"No encontré definición para '{word}'."
        except Exception as e:
            return f"Error: {str(e)}"

    def get_wikipedia(self, query: str) -> str:
        try:
            url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
            r = self.client.get(url)
            if r.status_code == 200:
                data = r.json()
                title = data.get("title", query)
                extract = data.get("extract", "No hay información disponible.")
                page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                return f"**{title}**\n{page_url}\n\n{extract}"
            search_url = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit=3"
            r2 = self.client.get(search_url)
            data2 = r2.json()
            results = data2.get("query", {}).get("search", [])
            if results:
                res = f"Resultados en Wikipedia para '{query}':\n"
                for item in results:
                    res += f"\n- **{item['title']}**: {item.get('snippet', '')[:100]}"
                return res
            return f"No encontré nada en Wikipedia para '{query}'."
        except Exception as e:
            return f"Error de Wikipedia: {str(e)}"

    def translate(self, text: str, target: str = "en") -> str:
        try:
            url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=es|{target}"
            r = self.client.get(url)
            data = r.json()
            translated = data.get("responseData", {}).get("translatedText", "")
            if translated:
                return f"Traducción ({target}): {translated}"
            return "No pude traducir eso."
        except Exception as e:
            return f"Error de traducción: {str(e)}"

    def check_url(self, url: str) -> str:
        try:
            if not url.startswith("http"):
                url = "https://" + url
            r = self.client.head(url, timeout=10)
            return f"URL: {url}\nEstado: {r.status_code}\nTipo: {r.headers.get('content-type', '?')}\nTamaño: {r.headers.get('content-length', '?')} bytes"
        except Exception as e:
            return f"Error verificando {url}: {str(e)}"

    def download_file(self, url: str, filename: str = None) -> str:
        try:
            if not url.startswith("http"):
                url = "https://" + url
            if not filename:
                filename = urllib.parse.urlparse(url).path.split("/")[-1] or "download"
            import os
            save_dir = os.path.join(os.path.dirname(__file__), "..", "workspace", "downloads")
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)
            with self.client.stream("GET", url) as r:
                r.raise_for_status()
                with open(save_path, "wb") as f:
                    for chunk in r.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            size = os.path.getsize(save_path)
            return f"Descargado: {filename} ({size / 1024:.1f} KB)\nUbicación: {save_path}"
        except Exception as e:
            return f"Error descargando: {str(e)}"

    def close(self):
        self.client.close()


web = WebAccess()
