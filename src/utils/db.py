"""
SQLite + SQLCipher database interface for session logs.
SES-02: encrypted storage (AES-256 via SQLCipher).
"""
import os, time, logging

logger = logging.getLogger(__name__)


class SessionDB:
    def __init__(self, db_path: str, key: str = None):
        self._path = db_path
        self._key  = key or os.environ.get("EDGEWATCH_DB_KEY", "changeme-in-production")
        self._conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        try:
            # Try pysqlcipher3 (encrypted)
            from pysqlcipher3 import dbapi2 as sqlcipher
            os.makedirs(os.path.dirname(self._path) if os.path.dirname(self._path) else ".", exist_ok=True)
            self._conn = sqlcipher.connect(self._path)
            self._conn.execute(f"PRAGMA key='{self._key}'")
            self._conn.execute("PRAGMA cipher_page_size=4096")
            logger.info(f"Connected to encrypted DB: {self._path}")
        except ImportError:
            import sqlite3
            self._conn = sqlite3.connect(self._path)
            logger.warning("pysqlcipher3 not available, using unencrypted SQLite (install on Pi)")

    def _create_tables(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_ts REAL,
                end_ts   REAL,
                alert_count INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS alerts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                ts         REAL,
                type       TEXT,
                severity   TEXT,
                value      REAL,
                message    TEXT
            );
            CREATE TABLE IF NOT EXISTS env_readings (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                ts         REAL,
                temp_c     REAL,
                humidity   REAL,
                co2_ppm    REAL,
                tvoc_ppb   REAL,
                lux        REAL
            );
        """)
        self._conn.commit()

    def start_session(self, session_id: str):
        self._conn.execute(
            "INSERT OR REPLACE INTO sessions (id, start_ts) VALUES (?,?)",
            (session_id, time.time()))
        self._conn.commit()

    def end_session(self, session_id: str):
        self._conn.execute(
            "UPDATE sessions SET end_ts=? WHERE id=?",
            (time.time(), session_id))
        self._conn.commit()

    def log_env(self, session_id: str, data: dict):
        self._conn.execute(
            "INSERT INTO env_readings (session_id,ts,temp_c,humidity,co2_ppm,tvoc_ppb,lux) "
            "VALUES (?,?,?,?,?,?,?)",
            (session_id, time.time(),
             data.get("temp_c"), data.get("humidity"), data.get("co2_ppm"),
             data.get("tvoc_ppb"), data.get("lux")))
        self._conn.commit()

    def log_alert(self, session_id: str, data: dict):
        self._conn.execute(
            "INSERT INTO alerts (session_id,ts,type,severity,value,message) VALUES (?,?,?,?,?,?)",
            (session_id, data.get("ts", time.time()), data.get("type"),
             data.get("severity"), data.get("value",0), data.get("message","")))
        self._conn.increment_count = True
        self._conn.commit()

    def get_session_alerts(self, session_id: str) -> list:
        cur = self._conn.execute(
            "SELECT ts,type,severity,value FROM alerts WHERE session_id=? ORDER BY ts",
            (session_id,))
        return cur.fetchall()

    def close(self):
        if self._conn:
            self._conn.close()
