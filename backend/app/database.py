import aiosqlite
import os
import logging
from app.config import settings

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    settings.DATABASE_PATH
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    dietary_preferences TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS magic_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES users(id),
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS recipe_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES users(id),
    recipe_title TEXT NOT NULL,
    interaction_type TEXT NOT NULL CHECK(interaction_type IN ('like', 'skip', 'view', 'cook', 'save')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_ingredients TEXT
);

CREATE TABLE IF NOT EXISTS consumption_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES users(id),
    recipe_title TEXT NOT NULL,
    consumed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    portion_size REAL DEFAULT 1.0,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_magic_links_token ON magic_links(token);
CREATE INDEX IF NOT EXISTS idx_interactions_user ON recipe_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON recipe_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_interactions_recipe ON recipe_interactions(recipe_title);
CREATE INDEX IF NOT EXISTS idx_consumption_user ON consumption_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_consumption_date ON consumption_logs(consumed_at);

CREATE TABLE IF NOT EXISTS fridge_ingredients (
    user_id TEXT NOT NULL REFERENCES users(id),
    ingredient TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, ingredient)
);
CREATE INDEX IF NOT EXISTS idx_fridge_user ON fridge_ingredients(user_id);
"""

USER_FEATURES_VIEW_SQL = """
CREATE VIEW IF NOT EXISTS user_features AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(DISTINCT CASE WHEN ri.interaction_type = 'like' THEN ri.recipe_title END) as total_likes,
    COUNT(DISTINCT CASE WHEN ri.interaction_type = 'skip' THEN ri.recipe_title END) as total_skips,
    COUNT(DISTINCT CASE WHEN ri.interaction_type = 'cook' THEN ri.recipe_title END) as total_cooked,
    CAST(AVG(cl.portion_size) AS REAL) as avg_portion,
    (SELECT meal_type FROM consumption_logs
     WHERE user_id = u.id GROUP BY meal_type
     ORDER BY COUNT(*) DESC LIMIT 1) as preferred_meal_type,
    (SELECT COUNT(*) FROM (
        SELECT recipe_title FROM consumption_logs
        WHERE user_id = u.id
          AND consumed_at >= datetime('now', '-7 days')
        GROUP BY recipe_title HAVING COUNT(*) >= 2
    )) as weekly_repeat_count
FROM users u
LEFT JOIN recipe_interactions ri ON u.id = ri.user_id
LEFT JOIN consumption_logs cl ON u.id = cl.user_id
GROUP BY u.id;
"""


async def _migrate_fridge_from_interactions(db):
    """Populate fridge_ingredients from latest context_ingredients per user (one-time, only if user has no fridge yet)."""
    import json
    cursor = await db.execute(
        """SELECT ri.user_id, ri.context_ingredients FROM recipe_interactions ri
           WHERE ri.context_ingredients IS NOT NULL AND ri.context_ingredients != ''
           AND NOT EXISTS (SELECT 1 FROM fridge_ingredients fi WHERE fi.user_id = ri.user_id)
           ORDER BY ri.created_at DESC"""
    )
    seen_users = set()
    rows = await cursor.fetchall()
    for row in rows:
        user_id = row[0]
        if user_id in seen_users:
            continue
        seen_users.add(user_id)
        try:
            ingredients = json.loads(row[1])
            if not ingredients:
                continue
            for ing in ingredients:
                if isinstance(ing, str) and ing.strip():
                    await db.execute(
                        """INSERT OR IGNORE INTO fridge_ingredients (user_id, ingredient)
                           VALUES (?, ?)""",
                        (user_id, ing.strip())
                    )
        except (json.JSONDecodeError, TypeError):
            continue


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = await get_db()
    try:
        await db.executescript(SCHEMA_SQL)
        # Migrate constraint to include 'save' if not already done.
        # Drop the view first — SQLite rejects DROP TABLE while a view references it.
        cursor = await db.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='recipe_interactions'"
        )
        row = await cursor.fetchone()
        if row and "'save'" not in row[0]:
            await db.executescript("""
                BEGIN;
                DROP VIEW IF EXISTS user_features;
                CREATE TABLE IF NOT EXISTS recipe_interactions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL REFERENCES users(id),
                    recipe_title TEXT NOT NULL,
                    interaction_type TEXT NOT NULL CHECK(interaction_type IN ('like','skip','view','cook','save')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    context_ingredients TEXT
                );
                INSERT OR IGNORE INTO recipe_interactions_new SELECT * FROM recipe_interactions;
                DROP TABLE recipe_interactions;
                ALTER TABLE recipe_interactions_new RENAME TO recipe_interactions;
                CREATE INDEX IF NOT EXISTS idx_interactions_user ON recipe_interactions(user_id);
                CREATE INDEX IF NOT EXISTS idx_interactions_type ON recipe_interactions(interaction_type);
                CREATE INDEX IF NOT EXISTS idx_interactions_recipe ON recipe_interactions(recipe_title);
                COMMIT;
            """)
        await db.executescript(USER_FEATURES_VIEW_SQL)
        await _migrate_fridge_from_interactions(db)
        await db.commit()
        logger.info(f"Database initialized at {DB_PATH}")
    finally:
        await db.close()
