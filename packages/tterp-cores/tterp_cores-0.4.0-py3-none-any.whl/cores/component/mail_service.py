from email.mime.text import MIMEText
from smtplib import SMTP

from fastapi import HTTPException

from cores.config import mail_config
from cores.logger.enhanced_logging import LogCategory, logger

# typical values for text_subtype are plain, html, xml
# text_subtype = 'plain'
# content = """\
# Test SMTTP Python script
# """

# subject = "Sent from vinasupport.com"


def send_mail(
    subject,
    receiver_emails,
    content,
    text_subtype="plain",
    mail_username: str = None,
    mail_password: str = None,
):
    try:
        msg = MIMEText(content, text_subtype)
        msg["Subject"] = subject
        # some SMTP servers will do this automatically, not all
        if not mail_username:
            mail_from_address = mail_config.MAIL_FROM_ADDRESS
            mail_username = mail_config.MAIL_USERNAME
        else:
            mail_from_address = mail_username
        if not mail_password:
            mail_password = mail_config.MAIL_PASSWORD
        msg["From"] = mail_from_address
        msg["To"] = ", ".join(receiver_emails)
        conn = SMTP(mail_config.MAIL_HOST, mail_config.MAIL_PORT)
        conn.login(mail_username, mail_password)
        conn.sendmail(mail_from_address, receiver_emails, msg.as_string())
        conn.quit()
        return True

    except Exception:
        import traceback

        logger.error(
            "Error sending email",
            category=LogCategory.SYSTEM,
            extra_fields={"traceback": traceback.format_exc()},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error sending email: {traceback.format_exc()}",
        )
