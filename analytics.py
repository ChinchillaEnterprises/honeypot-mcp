import sqlite3
import hashlib
import time
import os
from pathlib import Path

DB_PATH = os.environ.get("HONEYPOT_DB_PATH", str(Path(__file__).parent / "honeypot.db"))
FREE_TIER_LIMIT = 10

TOOL_PRICES = {
    "red_team_attack": 0.05,
    "score_content": 0.02,
    "deep_research": 0.10,
    "verse_assist": 0.03,
}

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            tool_name TEXT NOT NULL,
            caller_id TEXT NOT NULL,
            input_size INTEGER NOT NULL,
            response_time_ms INTEGER,
            success INTEGER NOT NULL DEFAULT 1,
            would_have_charged INTEGER NOT NULL DEFAULT 0,
            hypothetical_price REAL NOT NULL DEFAULT 0.0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rate_limits (
            caller_id TEXT NOT NULL,
            window_start REAL NOT NULL,
            call_count INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (caller_id, window_start)
        )
    """)
    conn.commit()
    return conn

def hash_caller(caller_info: str) -> str:
    return hashlib.sha256(caller_info.encode()).hexdigest()[:16]

def get_caller_count(caller_id: str) -> int:
    conn = _get_conn()
    row = conn.execute(
        "SELECT COUNT(*) FROM calls WHERE caller_id = ?", (caller_id,)
    ).fetchone()
    conn.close()
    return row[0] if row else 0

def check_rate_limit(caller_id: str, max_per_minute: int = 3) -> bool:
    conn = _get_conn()
    now = time.time()
    window_start = now - 60
    conn.execute(
        "DELETE FROM rate_limits WHERE window_start < ?", (window_start,)
    )
    row = conn.execute(
        "SELECT SUM(call_count) FROM rate_limits WHERE caller_id = ? AND window_start >= ?",
        (caller_id, window_start)
    ).fetchone()
    current = row[0] if row and row[0] else 0
    if current >= max_per_minute:
        conn.close()
        return False
    conn.execute(
        "INSERT OR REPLACE INTO rate_limits (caller_id, window_start, call_count) VALUES (?, ?, ?)",
        (caller_id, now, 1)
    )
    conn.commit()
    conn.close()
    return True

def check_daily_global_cap(max_daily: int = 500) -> bool:
    conn = _get_conn()
    today_start = time.time() - (time.time() % 86400)
    row = conn.execute(
        "SELECT COUNT(*) FROM calls WHERE timestamp >= ?", (today_start,)
    ).fetchone()
    conn.close()
    return (row[0] if row else 0) < max_daily

def log_call(
    tool_name: str,
    caller_id: str,
    input_size: int,
    response_time_ms: int,
    success: bool = True,
):
    conn = _get_conn()
    prior_count = get_caller_count(caller_id)
    exceeded = prior_count >= FREE_TIER_LIMIT
    size_multiplier = max(1.0, input_size / 1000)
    base_price = TOOL_PRICES.get(tool_name, 0.01)
    price = round(base_price * size_multiplier, 4) if exceeded else 0.0

    conn.execute(
        """INSERT INTO calls
           (timestamp, tool_name, caller_id, input_size, response_time_ms, success, would_have_charged, hypothetical_price)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (time.time(), tool_name, caller_id, input_size, response_time_ms, int(success), int(exceeded), price)
    )
    conn.commit()
    conn.close()
    return exceeded, price

def get_footer(exceeded: bool) -> str:
    if exceeded:
        return "\n\n---\nPowered by Chinchilla AI | chinchilla-ai.com"
    return ""

def daily_summary() -> dict:
    conn = _get_conn()
    today_start = time.time() - (time.time() % 86400)
    rows = conn.execute("""
        SELECT
            COUNT(*) as total_calls,
            COUNT(DISTINCT caller_id) as unique_callers,
            SUM(would_have_charged) as charged_events,
            SUM(hypothetical_price) as hypothetical_revenue,
            AVG(response_time_ms) as avg_response_ms
        FROM calls WHERE timestamp >= ?
    """, (today_start,)).fetchone()

    repeat = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT caller_id FROM calls
            WHERE timestamp >= ?
            GROUP BY caller_id HAVING COUNT(*) > 3
        )
    """, (today_start,)).fetchone()

    conn.close()
    return {
        "total_calls": rows[0] or 0,
        "unique_callers": rows[1] or 0,
        "would_have_charged_events": rows[2] or 0,
        "hypothetical_revenue": round(rows[3] or 0, 2),
        "avg_response_ms": round(rows[4] or 0, 1),
        "repeat_callers_3plus": repeat[0] or 0,
    }

def all_time_summary() -> dict:
    conn = _get_conn()
    rows = conn.execute("""
        SELECT
            COUNT(*) as total_calls,
            COUNT(DISTINCT caller_id) as unique_callers,
            SUM(would_have_charged) as charged_events,
            SUM(hypothetical_price) as hypothetical_revenue
        FROM calls
    """).fetchone()
    conn.close()
    return {
        "total_calls": rows[0] or 0,
        "unique_callers": rows[1] or 0,
        "would_have_charged_events": rows[2] or 0,
        "hypothetical_revenue": round(rows[3] or 0, 2),
    }
