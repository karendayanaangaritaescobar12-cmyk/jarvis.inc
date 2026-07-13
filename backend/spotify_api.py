import os
import json
import base64
from typing import Optional, Dict
import httpx


class SpotifyAPI:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
        self.token = None
        self.token_url = "https://accounts.spotify.com/api/token"
        self.api_base = "https://api.spotify.com/v1"

    def _get_token(self) -> Optional[str]:
        if self.token:
            return self.token
        if not self.client_id or not self.client_secret:
            return None

        try:
            auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            resp = httpx.post(self.token_url, data={
                "grant_type": "client_credentials"
            }, headers={"Authorization": f"Basic {auth}"}, timeout=10)
            if resp.status_code == 200:
                self.token = resp.json().get("access_token")
                return self.token
        except:
            pass
        return None

    def _headers(self) -> Dict:
        token = self._get_token()
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def is_available(self) -> bool:
        return self._get_token() is not None

    async def search(self, query: str, search_type: str = "track", limit: int = 5) -> str:
        token = self._get_token()
        if not token:
            return "Spotify API no configurado. Necesitas SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET en .env"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.api_base}/search",
                    params={"q": query, "type": search_type, "limit": limit},
                    headers=self._headers(),
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get(f"{search_type}s", {}).get("items", [])
                    if not items:
                        return f"No encontré nada para '{query}'"

                    result = f"🎵 Resultados para '{query}':\n\n"
                    for i, item in enumerate(items[:limit], 1):
                        name = item.get("name", "Unknown")
                        artists = ", ".join([a["name"] for a in item.get("artists", [])])
                        album = item.get("album", {}).get("name", "")
                        url = item.get("external_urls", {}).get("spotify", "")
                        result += f"{i}. {name} - {artists}\n"
                        if album:
                            result += f"   Album: {album}\n"
                        if url:
                            result += f"   🔗 {url}\n"
                        result += "\n"
                    return result
                return f"Error de Spotify API: {resp.status_code}"
        except Exception as e:
            return f"Error: {str(e)[:100]}"

    async def get_track_info(self, track_id: str) -> str:
        token = self._get_token()
        if not token:
            return "Spotify API no configurado."

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.api_base}/tracks/{track_id}",
                    headers=self._headers(),
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    name = data.get("name", "Unknown")
                    artists = ", ".join([a["name"] for a in data.get("artists", [])])
                    album = data.get("album", {}).get("name", "")
                    duration_ms = data.get("duration_ms", 0)
                    duration = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}"
                    popularity = data.get("popularity", 0)
                    return f"🎵 {name}\n🎤 {artists}\n💿 {album}\n⏱ {duration}\n⭐ Popularidad: {popularity}/100"
                return f"Error: {resp.status_code}"
        except Exception as e:
            return f"Error: {str(e)[:100]}"

    async def get_artist_top_tracks(self, artist_name: str) -> str:
        token = self._get_token()
        if not token:
            return "Spotify API no configurado."

        try:
            async with httpx.AsyncClient() as client:
                search_resp = await client.get(
                    f"{self.api_base}/search",
                    params={"q": artist_name, "type": "artist", "limit": 1},
                    headers=self._headers(),
                    timeout=10
                )
                if search_resp.status_code == 200:
                    artists = search_resp.json().get("artists", {}).get("items", [])
                    if artists:
                        artist_id = artists[0]["id"]
                        top_resp = await client.get(
                            f"{self.api_base}/artists/{artist_id}/top-tracks",
                            params={"country": "CO"},
                            headers=self._headers(),
                            timeout=10
                        )
                        if top_resp.status_code == 200:
                            tracks = top_resp.json().get("tracks", [])
                            result = f"🎤 Top tracks de {artist_name}:\n\n"
                            for i, track in enumerate(tracks[:10], 1):
                                result += f"{i}. {track['name']}\n"
                            return result
            return f"No encontré info de {artist_name}"
        except Exception as e:
            return f"Error: {str(e)[:100]}"

    async def get_recommendations(self, seed_artists: str = None, seed_genres: str = None) -> str:
        token = self._get_token()
        if not token:
            return "Spotify API no configurado."

        try:
            params = {"limit": 10, "market": "CO"}
            if seed_artists:
                params["seed_artists"] = seed_artists
            if seed_genres:
                params["seed_genres"] = seed_genres

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.api_base}/recommendations",
                    params=params,
                    headers=self._headers(),
                    timeout=10
                )
                if resp.status_code == 200:
                    tracks = resp.json().get("tracks", [])
                    result = "🎶 Recomendaciones:\n\n"
                    for i, track in enumerate(tracks, 1):
                        artists = ", ".join([a["name"] for a in track.get("artists", [])])
                        result += f"{i}. {track['name']} - {artists}\n"
                    return result
                return "No pude generar recomendaciones"
        except Exception as e:
            return f"Error: {str(e)[:100]}"


spotify_api = SpotifyAPI()
