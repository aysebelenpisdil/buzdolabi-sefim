import json
import logging
from datetime import datetime
from app.database import get_db, init_db as _init_db

logger = logging.getLogger(__name__)


class DatabaseService:

    async def init_db(self):
        await _init_db()

    async def record_interaction(self, user_id: str, recipe_title: str,
                                  interaction_type: str,
                                  context_ingredients: list[str] | None = None) -> int:
        db = await get_db()
        try:
            ctx_json = json.dumps(context_ingredients, ensure_ascii=False) if context_ingredients else None
            cursor = await db.execute(
                """INSERT INTO recipe_interactions (user_id, recipe_title, interaction_type, context_ingredients)
                   VALUES (?, ?, ?, ?)""",
                (user_id, recipe_title, interaction_type, ctx_json)
            )
            await db.commit()
            return cursor.lastrowid
        finally:
            await db.close()

    async def log_consumption(self, user_id: str, recipe_title: str,
                               meal_type: str, portion_size: float = 1.0,
                               rating: int | None = None,
                               notes: str | None = None) -> int:
        db = await get_db()
        try:
            cursor = await db.execute(
                """INSERT INTO consumption_logs (user_id, recipe_title, meal_type, portion_size, rating, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, recipe_title, meal_type, portion_size, rating, notes)
            )
            await db.commit()
            return cursor.lastrowid
        finally:
            await db.close()

    async def get_user_features(self, user_id: str) -> dict:
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT * FROM user_features WHERE user_id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return {
                    "user_id": user_id, "email": "", "total_likes": 0,
                    "total_skips": 0, "total_cooked": 0, "avg_portion": None,
                    "preferred_meal_type": None, "weekly_repeat_count": 0,
                    "like_skip_ratio": None, "top_liked_recipes": [],
                    "weekly_repeats": [],
                }

            features = dict(row)

            total_likes = features.get("total_likes", 0)
            total_skips = features.get("total_skips", 0)
            features["like_skip_ratio"] = (
                round(total_likes / total_skips, 2)
                if total_skips > 0 else None
            )

            cursor = await db.execute(
                """SELECT recipe_title, COUNT(*) as cnt
                   FROM recipe_interactions
                   WHERE user_id = ? AND interaction_type = 'like'
                   GROUP BY recipe_title ORDER BY cnt DESC LIMIT 10""",
                (user_id,)
            )
            features["top_liked_recipes"] = [r["recipe_title"] for r in await cursor.fetchall()]

            features["weekly_repeats"] = await self.get_weekly_repeats(user_id, _db=db)

            return features
        finally:
            await db.close()

    async def get_weekly_repeats(self, user_id: str, _db=None) -> list[str]:
        db = _db or await get_db()
        try:
            cursor = await db.execute(
                """SELECT recipe_title FROM consumption_logs
                   WHERE user_id = ? AND consumed_at >= datetime('now', '-7 days')
                   GROUP BY recipe_title HAVING COUNT(*) >= 2""",
                (user_id,)
            )
            return [r["recipe_title"] for r in await cursor.fetchall()]
        finally:
            if not _db:
                await db.close()

    async def get_interaction_history(self, user_id: str,
                                       limit: int = 50, offset: int = 0) -> list[dict]:
        db = await get_db()
        try:
            cursor = await db.execute(
                """SELECT id, recipe_title, interaction_type, created_at
                   FROM recipe_interactions
                   WHERE user_id = ?
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (user_id, limit, offset)
            )
            return [dict(r) for r in await cursor.fetchall()]
        finally:
            await db.close()

    async def get_consumption_history(self, user_id: str,
                                       limit: int = 50, offset: int = 0) -> list[dict]:
        db = await get_db()
        try:
            cursor = await db.execute(
                """SELECT id, recipe_title, consumed_at, meal_type, portion_size, rating, notes
                   FROM consumption_logs
                   WHERE user_id = ?
                   ORDER BY consumed_at DESC LIMIT ? OFFSET ?""",
                (user_id, limit, offset)
            )
            return [dict(r) for r in await cursor.fetchall()]
        finally:
            await db.close()

    async def get_recipe_interaction_status(self, user_id: str, recipe_title: str) -> dict:
        """Get current like/skip status for a recipe."""
        db = await get_db()
        try:
            cursor = await db.execute(
                """SELECT interaction_type FROM recipe_interactions
                   WHERE user_id = ? AND recipe_title = ?
                     AND interaction_type IN ('like', 'skip')
                   ORDER BY created_at DESC LIMIT 1""",
                (user_id, recipe_title)
            )
            row = await cursor.fetchone()
            return {"status": row["interaction_type"] if row else None}
        finally:
            await db.close()


    async def delete_interaction(self, user_id: str, interaction_id: int) -> bool:
        db = await get_db()
        try:
            cursor = await db.execute(
                "DELETE FROM recipe_interactions WHERE id = ? AND user_id = ?",
                (interaction_id, user_id)
            )
            await db.commit()
            return cursor.rowcount > 0
        finally:
            await db.close()

    async def get_fridge_ingredients(self, user_id: str) -> list[str]:
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT ingredient FROM fridge_ingredients WHERE user_id = ? ORDER BY ingredient",
                (user_id,)
            )
            return [r["ingredient"] for r in await cursor.fetchall()]
        finally:
            await db.close()

    async def save_fridge_ingredients(self, user_id: str, ingredients: list[str]) -> None:
        db = await get_db()
        try:
            await db.execute("DELETE FROM fridge_ingredients WHERE user_id = ?", (user_id,))
            for ing in ingredients:
                if ing and str(ing).strip():
                    await db.execute(
                        "INSERT INTO fridge_ingredients (user_id, ingredient) VALUES (?, ?)",
                        (user_id, str(ing).strip())
                    )
            await db.commit()
        finally:
            await db.close()


database_service = DatabaseService()
