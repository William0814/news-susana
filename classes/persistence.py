import os
import datetime as dt
from typing import Iterable, Dict, Any, List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class DataNewsScraping:
    def __init__(self, database_url=DATABASE_URL):
        self.engine = create_engine(database_url)
        self._ini_schema()

    def _ini_schema(self):
        command_create = """
        CREATE TABLE IF NOT EXISTS news_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            source TEXT,
            resume TEXT,
            publishedAt TIMESTAMPZ,
            createdAt TIMESTAMPZ DEFAULT now()
        );"""
        with self.engine.begin() as c:
            c.execute(command_create)

    def save_items(self, items: Iterable[Dict[str, Any]]) -> int:
        sql = Text("""
        INSERT INTO news_items (title, url, source, resume, publishedAt, createdAt)
        VALUES (:title, :url, :source, :resume, :publishedAt, now())
        """)

        payLoads = []
        for item in items:
            payLoads.append({
                "title": (item.get("title") or "").strip(),
                "url": (item.get("url") or "").strip(),
                "source": (item.get("source") or "").strip(),
                "resume": (item.get("resume") or "").strip(),
                "publishedAt": dt.datetime.fromisoformat(item.get("publishedAt") or item.get("date")),
            })
        if not payLoads:
            return 0
        with self.engine.begin() as c:
            result = c.execute(sql, payLoads)
            return result.rowcount or 0
        
    def latest(self, limit: int = 12) -> List[Dict[str, Any]]:
        query = Text("""
        SELECT title, url, source, resume, publishedAt
        FROM news_items
        ORDER BY publishedAt DESC NULLS LAST, id DESC
        LIMIT :n
        """)
        with self.engine.begin() as c:
            rows = c.execute(query, {"n": limit}).mappings().all()
        return [dict(row) for row in rows]
    

