import json
import os
import re
import time
import random
import requests
from pathlib import Path
from duckduckgo_search import DDGS

RECIPES_PATH = "backend/data/recipes.json"
OUTPUT_DIR = Path("public/images/recipies")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def clean_title(title: str) -> str:
    """Parantez içi diyet etiketlerini kaldırır: 'Vegan Sütlaç (Vegan)' → 'Vegan Sütlaç'"""
    return re.sub(r"\s*\(.*?\)", "", title).strip()


def fetch_image_url(query: str) -> str | None:
    """DuckDuckGo ile görsel URL'si arar, bulamazsa None döner."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(
                keywords=f"{query} yemeği tarifi",
                region="tr-tr",
                safesearch="moderate",
                max_results=5,
            ))
        for r in results:
            url = r.get("image", "")
            if url and url.startswith("http"):
                return url
    except Exception as e:
        print(f"    [DDG hata] {e}")
    return None


def download_image(url: str, dest: Path) -> bool:
    """Görseli indirir, başarı durumunda True döner."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if "image" not in content_type:
            return False
        dest.write_bytes(resp.content)
        return True
    except requests.HTTPError as e:
        print(f"    [HTTP hata] {e}")
    except requests.RequestException as e:
        print(f"    [İndirme hata] {e}")
    return False


def main():
    with open(RECIPES_PATH, encoding="utf-8") as f:
        recipes = json.load(f)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = len(recipes)
    skipped = 0
    success = 0
    failed = 0

    for i, recipe in enumerate(recipes, start=1):
        title = recipe["Title"]
        image_name = recipe["Image_Name"]
        dest = OUTPUT_DIR / f"{image_name}.jpg"

        prefix = f"{i}/{total}"

        if dest.exists():
            print(f"  ⏭  {prefix} atlandı (mevcut): {title}")
            skipped += 1
            continue

        clean = clean_title(title)
        print(f"  ⬇  {prefix} indiriliyor: {clean}")

        url = fetch_image_url(clean)
        if not url:
            print(f"    ✗  Görsel bulunamadı: {clean}")
            failed += 1
        elif download_image(url, dest):
            print(f"    ✓  Kaydedildi → {dest.name}")
            success += 1
        else:
            print(f"    ✗  İndirilemedi: {url[:60]}...")
            failed += 1

        # DDG rate-limit koruması: her indirme arası 5-9 sn + her 40 tarifte 5 dk mola
        if i % 40 == 0:
            print(f"☕ {i} tarif tamamlandı. IP engeli yememek için 5 dakika mola veriliyor...")
            time.sleep(300)
        else:
            time.sleep(random.uniform(5.0, 9.0))

    print()
    print("=" * 50)
    print(f"Tamamlandı — Toplam: {total} | ✓ {success} | ⏭ {skipped} | ✗ {failed}")


if __name__ == "__main__":
    main()
