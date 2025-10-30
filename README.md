# 📰 Susana News — Automated Legal News Scraper

> _“Law, clarity, and automation — all in one Flask.”_

Susana News is a **Python + Flask** web application that dynamically aggregates and publishes legal news from official German sources such as **[djb.de/familienrecht](https://www.djb.de/familienrecht)**.  
The app runs on **Railway**, stores data in **PostgreSQL**, and refreshes weekly through a **GitHub Actions** workflow.

---

## 🚀 Features

- **Dynamic news aggregation** from legal websites (DJB and others).  
- **Smart scraping** powered by `requests` + `BeautifulSoup4`.  
- **Automatic deduplication** via PostgreSQL upserts.  
- **Clean and responsive UI** (Bootstrap-based magazine layout).  
- **Weekly auto-refresh** via GitHub Actions + Telegram notifications.  
- **Modular design** — scraping logic, persistence, and web views fully decoupled.

---

## 🧠 Architecture

```text
+-------------+        +-------------+        +----------------+
| Flask App   | <----> | PostgreSQL  | <----> | Railway Hosting |
+-------------+        +-------------+        +----------------+
      ↑
      │
      │  (HTTP GET /cron/scrape?secret=...)
      │
+-------------+
| GitHub CI   |  (Weekly Trigger)
+-------------+

