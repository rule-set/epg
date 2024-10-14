import sqlite3


def setup_database():
    conn = sqlite3.connect("epg.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS programmes (
            tvg_id TEXT,
            tvg_name TEXT,
            title TEXT,
            start TEXT,
            stop TEXT
        )
    """
    )
    conn.commit()
    conn.close()


setup_database()
