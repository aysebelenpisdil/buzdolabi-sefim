"""
E-posta servisi - Magic link gönderimi için SMTP entegrasyonu.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def send_magic_link(to_email: str, token: str) -> bool:
    """
    Magic link e-postası gönderir.

    Args:
        to_email: Alıcı e-posta adresi
        token: Magic link token

    Returns:
        True başarılı, False hata durumunda
    """
    if not settings.SMTP_ENABLED:
        logger.warning("SMTP disabled, cannot send magic link email")
        return False

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.error("SMTP_USER and SMTP_PASSWORD must be set when SMTP_ENABLED is True")
        return False

    # Gmail uygulama şifresi boşluk içerebilir; SMTP için boşluksuz kullan
    smtp_user = str(settings.SMTP_USER).strip()
    smtp_password = str(settings.SMTP_PASSWORD).replace(" ", "").strip()
    from_email = (settings.SMTP_FROM or settings.SMTP_USER).strip()
    magic_link_url = f"{settings.FRONTEND_URL}/#/login?token={token}"

    subject = "Buzdolabı Şefi - Giriş Bağlantınız"

    plain_text = f"""Merhaba,

Buzdolabı Şefi uygulamasına giriş yapmak için aşağıdaki bağlantıya tıklayın:

{magic_link_url}

Bu bağlantı 10 dakika içinde geçerliliğini yitirecektir.

Eğer bu talebi siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.

Buzdolabı Şefi
"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="text-align: center; margin-bottom: 24px;">
        <div style="width: 48px; height: 48px; background: #10b981; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 20px;">F</div>
        <h1 style="margin: 16px 0 8px; font-size: 24px; color: #111;">Buzdolabı Şefi</h1>
    </div>
    <p style="margin-bottom: 16px;">Merhaba,</p>
    <p style="margin-bottom: 24px;">Buzdolabı Şefi uygulamasına giriş yapmak için aşağıdaki butona tıklayın:</p>
    <p style="text-align: center; margin: 32px 0;">
        <a href="{magic_link_url}" style="display: inline-block; padding: 14px 32px; background: #10b981; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">Giriş Yap</a>
    </p>
    <p style="font-size: 14px; color: #666;">
        Veya bu bağlantıyı tarayıcınıza kopyalayın:<br>
        <a href="{magic_link_url}" style="color: #10b981; word-break: break-all;">{magic_link_url}</a>
    </p>
    <p style="font-size: 13px; color: #888; margin-top: 32px;">
        Bu bağlantı 10 dakika içinde geçerliliğini yitirecektir.
    </p>
    <p style="font-size: 13px; color: #888;">
        Eğer bu talebi siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.
    </p>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{from_email}>"
    msg["To"] = to_email

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        logger.info(f"Magic link email sent to {to_email}")
        return True
    except Exception as e:
        logger.exception(f"Failed to send magic link email to {to_email}: {e}")
        return False
