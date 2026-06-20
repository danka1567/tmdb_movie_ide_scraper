from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
import re
import os

app = Flask(__name__)

def get_tmdb_ids():
    tmdb_ids = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        page = browser.new_page()

        for page_num in range(1, 6):
            url = f"https://www.themoviedb.org/list/634-top-250-imdb?page={page_num}"

            print(f"Loading {url}")

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(5000)

            html = page.content()

            matches = re.findall(r"/movie/(\d+)", html)

            tmdb_ids.update(matches)

        browser.close()

    return sorted(tmdb_ids, key=int)

@app.route("/")
def home():
    ids = get_tmdb_ids()

    urls = [
        f"https://primesrc.me/embed/movie?tmdb={movie_id}"
        for movie_id in ids
    ]

    return jsonify({
        "count": len(ids),
        "urls": urls
    })

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
