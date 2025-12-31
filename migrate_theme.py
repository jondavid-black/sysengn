import sqlite3
from sysengn.db.database import DB_PATH


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        if "theme_preference" not in columns:
            print("Adding theme_preference column to users table...")
            cursor.execute(
                "ALTER TABLE users ADD COLUMN theme_preference TEXT DEFAULT 'DARK'"
            )
            conn.commit()
            print("Migration successful.")
        else:
            print("Column theme_preference already exists.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
