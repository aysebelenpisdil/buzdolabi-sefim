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
    interaction_type TEXT NOT NULL CHECK(interaction_type IN ('like', 'skip', 'view', 'cook')),
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
        await db.executescript(USER_FEATURES_VIEW_SQL)
        await db.commit()
        logger.info(f"Database initialized at {DB_PATH}")
    finally:
        await db.close()
