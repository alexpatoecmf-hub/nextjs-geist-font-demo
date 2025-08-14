# -*- coding: utf-8 -*-
import sqlite3
import os
import time
import json

class LearningModule:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'zoe_learning.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute('PRAGMA journal_mode=WAL;')
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                data TEXT,
                ts INTEGER NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                url TEXT,
                ts INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def train_model(self):
        now = int(time.time())
        dados_exemplo = [
            ('url_visitada', '{"nome":"github.com","url":"https://github.com"}', now),
            ('url_visitada', '{"nome":"python.org","url":"https://www.python.org"}', now),
            ('url_visitada', '{"nome":"github.com","url":"https://github.com"}', now),
            ('url_visitada', '{"nome":"docs.github.com","url":"https://docs.github.com"}', now),
        ]
        cur = self.conn.cursor()
        cur.executemany("INSERT INTO events (type, data, ts) VALUES (?,?,?)", dados_exemplo)
        self.conn.commit()
        return "Treinamento simulado concluído (dados de demonstração inseridos)."

    def log_event(self, event_type, data):
        ts = int(time.time())
        cur = self.conn.cursor()
        cur.execute("INSERT INTO events (type, data, ts) VALUES (?,?,?)",
                    (event_type, json.dumps(data) if not isinstance(data, str) else data, ts))
        self.conn.commit()

    def check_for_suggestion(self):
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM events WHERE type='url_visitada' ORDER BY ts DESC LIMIT 50")
        rows = cur.fetchall()
        domain_counts = {}
        for (dstr,) in rows:
            try:
                d = json.loads(dstr)
                domain = d.get('nome', '')
                if domain:
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
            except Exception:
                continue
        if not domain_counts:
            return None
        top_domain = max(domain_counts, key=domain_counts.get)
        top_count = domain_counts[top_domain]
        if top_count >= 3:
            now = int(time.time())
            cur.execute("SELECT COUNT(*) FROM suggestions WHERE url=? AND ts > ?", (f'https://{top_domain}', now - 7*24*3600))
            c = cur.fetchone()[0]
            if c == 0:
                text = f"Você visitou {top_domain} com frequência. Quer abrir agora?"
                url = f"https://{top_domain}"
                cur.execute("INSERT INTO suggestions (text, url, ts) VALUES (?,?,?)", (text, url, now))
                self.conn.commit()
                return {"suggestion_text": text, "url": url}
        return None
