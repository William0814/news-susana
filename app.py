from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from classes.parsers_djb import DJBUnified
from classes.persistence import DataNewsScraping


load_dotenv()

app = Flask(__name__)

store = DataNewsScraping()
CRON_SECRET = os.getenv("CRON_SECRET") or "dev-secret"


@app.route('/')
def home_news():
    items = store.latest(limit=20)
    return render_template('index.html', items=items, page_title="Aktuelle Nachrichten")

@app.route('/suchen')
def search():
    query = (request.args.get('q') or '').strip()
    items = []
    if query:
        all_items = store.latest(limit=50)
        q = query.lower()
        items = [
            item for item in all_items
            if q in (item.get('title') or '').lower() or
               q in (item.get('resume') or '').lower()
        ]

    return render_template('index.html', items=items, page_title= f"Suchergebnisse für {query}" if query else "Suchen")

@app.route('/cron/scrape')
def cron_scrape():
    if request.args.get("secret") != CRON_SECRET:
        return "Unauthorized", 401
    
    scraper = DJBUnified(max_items=30, follow_detail=False)
    items = scraper.fetch_items()
    inserted = store.save_items(items)
    return jsonify({"inserted": inserted, "fetched": len(items)})

if __name__ == "__main__":
    app.run(debug=True)