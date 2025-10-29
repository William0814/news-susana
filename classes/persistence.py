import os
import datetime as dt
from typing import Iterable, Dict, Any, List
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import classes.converter_date as converter
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class DataNewsScraping:
    def __init__(self, database_url=DATABASE_URL):
        self.engine = create_engine(database_url)
        self._ini_schema()

    def _ini_schema(self):
        command_create = """
        CREATE TABLE IF NOT EXISTS news_items (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            source TEXT,
            resume TEXT,
            publishedat TEXT,
            createdat TIMESTAMPTZ DEFAULT now()
        );
        """
        with self.engine.begin() as c:
            c.exec_driver_sql(command_create)

    def save_items(self, items: Iterable[Dict[str, Any]]) -> int:
        sql = text("""
        INSERT INTO news_items (title, url, source, resume, publishedat, createdat)
        VALUES (:title, :url, :source, :resume, :publishedat, now())
        """)

        payLoads = []
        for item in items:
            payLoads.append({
                "title": (item.get("title") or "").strip(),
                "url": (item.get("url") or "").strip(),
                "source": (item.get("source") or "").strip(),
                "resume": (item.get("resume") or "").strip(),
                "publishedat": (item.get("date") or "").strip()
            })
        if not payLoads:
            return 0
        with self.engine.begin() as c:
            result = c.execute(sql, payLoads)
            return result.rowcount or 0
        
    def latest(self, limit: int = 30) -> List[Dict[str, Any]]:
        query = text("""
        SELECT title, url, source, resume, publishedat
        FROM news_items
        ORDER BY createdat DESC NULLS FIRST
        LIMIT :n
        """)
        with self.engine.begin() as c:
            rows = c.execute(query, {"n": limit}).mappings().all()
        return [dict(row) for row in rows]

    

