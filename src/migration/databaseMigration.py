from typing import TYPE_CHECKING
from src.migration.economyMigration import migrate as migrate_economy
if TYPE_CHECKING:
    from src.db_provider import DatabaseProvider

def migrate_database(db: "DatabaseProvider"):
    migrate_economy(db)
    
        