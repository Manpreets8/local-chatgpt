import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_WELCOME_EMAIL_HTML = """\
<div style="background:#0a0b0f;padding:40px 20px;font-family:-apple-system,
BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="max-width:420px;margin:0 auto;background:#111319;border:1px
  solid #262a35;border-radius:16px;padding:36px;">
    <div style="font-weight:600;font-size:16px;margin-bottom:24px;
    background:linear-gradient(135deg,#4f7dfb,#8b5cf6);
    -webkit-background-clip:text;background-clip:text;
    -webkit-text-fill-color:transparent;">Local ChatGPT</div>
    <h1 style="color:#e9eaf0;font-size:22px;margin:0 0 12px;">Welcome aboard!</h1>
    <p style="color:#8b93a7;font-size:14px;line-height:1.5;margin:0 0 24px;">
      Your account ({email}) is ready. You can now chat with Claude, upload
      documents, generate images, and everything you start is saved to your
      account and private to you.
    </p>
    <a href="{frontend_url}" style="display:inline-block;padding:12px 20px;
    background:linear-gradient(135deg,#4f7dfb,#8b5cf6);color:#fff;
    text-decoration:none;border-radius:10px;font-size:14px;font-weight:500;">
      Open Local ChatGPT
    </a>
  </div>
</div>
"""


class EmailNotConfiguredError(Exception):
    """Raised when no usable SMTP credentials are configured."""


class EmailService:
    """Sends transactional email via SMTP (Gmail by default) using only
    the standard library — no third-party email API, so there's no
    per-provider recipient/domain restriction to work around. Callers
    should treat failures as best-effort (see send_welcome_email_best_effort):
    a flaky mail server should never block something like signup."""

    def send_welcome_email(self, to_email: str) -> None:
        settings = get_settings()
        if not settings.smtp_username or not settings.smtp_password:
            raise EmailNotConfiguredError(
                "SMTP_USERNAME / SMTP_PASSWORD are not set. Add real values to your .env file."
            )

        message = MIMEMultipart("alternative")
        message["Subject"] = "Welcome to Local ChatGPT!"
        message["From"] = settings.smtp_username
        message["To"] = to_email
        message.attach(
            MIMEText(
                _WELCOME_EMAIL_HTML.format(email=to_email, frontend_url=settings.frontend_url),
                "html",
            )
        )

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_username, [to_email], message.as_string())


email_service = EmailService()


def send_welcome_email_best_effort(to_email: str) -> None:
    """For call sites that must never let an email failure break the
    primary operation (e.g. registration) — logs and swallows any error."""
    try:
        email_service.send_welcome_email(to_email)
    except EmailNotConfiguredError:
        logger.info("Skipping welcome email for %s — SMTP credentials not set.", to_email)
    except Exception:
        logger.exception("Failed to send welcome email to %s", to_email)


__all__ = [
    "email_service",
    "EmailService",
    "EmailNotConfiguredError",
    "send_welcome_email_best_effort",
]
