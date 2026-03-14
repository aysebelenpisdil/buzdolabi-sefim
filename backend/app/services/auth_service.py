import uuid
import logging
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)

serializer = URLSafeTimedSerializer(settings.SESSION_SECRET)


class AuthService:

    async def create_or_get_user(self, email: str) -> dict:
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT id, email, display_name, created_at FROM users WHERE email = ?",
                (email,)
            )
            row = await cursor.fetchone()
            if row:
                return dict(row)

            user_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            await db.execute(
                "INSERT INTO users (id, email, created_at) VALUES (?, ?, ?)",
                (user_id, email, now)
            )
            await db.commit()
            return {"id": user_id, "email": email, "display_name": None, "created_at": now}
        finally:
            await db.close()

    async def generate_magic_link(self, user_id: str) -> str:
        token = serializer.dumps(user_id, salt="magic-link")
        expires_at = (datetime.utcnow() + timedelta(seconds=settings.MAGIC_LINK_EXPIRY)).isoformat()

        db = await get_db()
        try:
            await db.execute(
                "INSERT INTO magic_links (user_id, token, expires_at) VALUES (?, ?, ?)",
                (user_id, token, expires_at)
            )
            await db.commit()
        finally:
            await db.close()

        logger.info(f"Magic link generated for user {user_id}")
        return token

    async def verify_magic_link(self, token: str) -> dict | None:
        try:
            user_id = serializer.loads(token, salt="magic-link", max_age=settings.MAGIC_LINK_EXPIRY)
        except Exception:
            logger.warning("Invalid or expired magic link token")
            return None

        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT id, user_id FROM magic_links WHERE token = ? AND used = 0",
                (token,)
            )
            link = await cursor.fetchone()
            if not link:
                return None

            await db.execute("UPDATE magic_links SET used = 1 WHERE id = ?", (link["id"],))

            now = datetime.utcnow().isoformat()
            await db.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now, user_id))
            await db.commit()

            cursor = await db.execute(
                "SELECT id, email, display_name, created_at FROM users WHERE id = ?",
                (user_id,)
            )
            user = await cursor.fetchone()
            return dict(user) if user else None
        finally:
            await db.close()

    async def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        expires_at = (datetime.utcnow() + timedelta(days=settings.SESSION_EXPIRY_DAYS)).isoformat()

        db = await get_db()
        try:
            await db.execute(
                "INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)",
                (session_id, user_id, expires_at)
            )
            await db.commit()
        finally:
            await db.close()

        return session_id

    async def validate_session(self, session_id: str) -> dict | None:
        if not session_id:
            return None

        db = await get_db()
        try:
            cursor = await db.execute("""
                SELECT s.id as session_id, s.expires_at, s.is_active,
                       u.id as user_id, u.email, u.display_name, u.created_at
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.id = ? AND s.is_active = 1
            """, (session_id,))
            row = await cursor.fetchone()
            if not row:
                return None

            if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
                await db.execute("UPDATE sessions SET is_active = 0 WHERE id = ?", (session_id,))
                await db.commit()
                return None

            return {
                "id": row["user_id"],
                "email": row["email"],
                "display_name": row["display_name"],
                "created_at": row["created_at"],
                "session_expires_at": row["expires_at"],
            }
        finally:
            await db.close()

    async def logout(self, session_id: str):
        db = await get_db()
        try:
            await db.execute("UPDATE sessions SET is_active = 0 WHERE id = ?", (session_id,))
            await db.commit()
        finally:
            await db.close()


auth_service = AuthService()
