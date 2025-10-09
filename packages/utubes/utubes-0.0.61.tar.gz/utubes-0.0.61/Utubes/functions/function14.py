"""
import re
import json
import requests
from ..scripts import Rttps
from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.parse import parse_qs

class Instagrams:

    async def scode(instagram_url, shortcode=None):
        parsed_url = urlparse(instagram_url)
        query_params = parse_qs(parsed_url.query)
        doc_id = query_params.get("doc_id", [None])[0]
        moonas = query_params.get("variables", [None])[0]
        if moonas:
            moones = unquote(moonas)
            moonus = json.loads(moones)
            codeos = moonus.get("shortcode")
        return codeos, doc_id

    async def extract(message):
        moones = re.search(Rttps.DATA05, message)
        return moones.group(0) if moones else None
    
    async def downloadR():
        url = "https://www.instagram.com/graphql/query"
        headers = {"User-Agent": "Mozilla/5.0",}
        params = {"variables": json.dumps({"shortcode": shortcode}), "doc_id": doc_id}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("❌ Failed to fetch:", response.status_code)
            return

        all_urls = []
        data = response.json()
        media = data["data"]["xdt_shortcode_media"]
        if "edge_sidecar_to_children" in media:
            edges = media["edge_sidecar_to_children"]["edges"]
            for i, item in enumerate(edges, start=1):
                node = item["node"]
                if node.get("is_video"):
                    video_url = node.get("video_url")
                    if video_url:
                        all_urls.append(video_url)
                elif node.get("display_url"):
                    all_urls.append(node["display_url"])
                else:
                    pass
            return all_urls
        else:
            if media.get("is_video"):
                video_url = media.get("video_url")
                if video_url:
                    all_urls.append(video_url)
                return all_urls
            elif media.get("display_url"):
                all_urls.append(media["display_url"])
                return all_urls
            else:
                return all_urls
"""
