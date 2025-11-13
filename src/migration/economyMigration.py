from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.db_provider import DatabaseProvider

def migrate(db: "DatabaseProvider"):
    
    cursor = db.db.execute_command_and_return_cursor("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if "coins" in columns:
        print(f"Skip migration. Coins already exists")
        return
    
    try:
        db.db.execute_command("""
                            ALTER TABLE users ADD COLUMN coins INTEGER
                            """)
        
        db.db.execute_command("""
                            UPDATE users SET coins = 0 WHERE coins IS NULL
                            """)
        db.db.database.commit()
        print(f"Migration complete")
    except Exception as e:
        print(f"Database may be already migrated: {e}")
    