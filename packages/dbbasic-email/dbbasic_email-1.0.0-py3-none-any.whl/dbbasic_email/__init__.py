"""
dbbasic-email: Simple email queue with Unix mail support

Local mail (Unix-style) + External email (SMTP) via dbbasic-queue
"""

import os
import time
import smtplib
import secrets
from email.message import EmailMessage
from pathlib import Path

__version__ = "1.0.0"

MAIL_DIR = os.getenv('MAIL_DIR', 'var/mail')
SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.getenv('SMTP_PORT', '25'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_ADDR = os.getenv('FROM_ADDR', 'noreply@example.com')


def mail(username, subject, body):
    """
    Send local mail to user (Unix mail)

    Args:
        username (str): Local username
        subject (str): Email subject
        body (str): Email body (plain text)

    Returns:
        str: Message ID
    """
    mailbox = Path(MAIL_DIR) / username
    mailbox.parent.mkdir(parents=True, exist_ok=True)

    message_id = f"<{secrets.token_hex(8)}@localhost>"

    with mailbox.open('a') as f:
        f.write(f"From system {time.ctime()}\n")
        f.write(f"Subject: {subject}\n")
        f.write(f"Message-ID: {message_id}\n")
        f.write(f"\n{body}\n\n")

    return message_id


def send_email(to, subject, body, from_addr=None):
    """
    Queue external email for SMTP delivery

    Args:
        to (str): Email address
        subject (str): Email subject
        body (str): Email body (plain text)
        from_addr (str, optional): From address

    Returns:
        str: Job ID
    """
    try:
        from dbbasic_queue import enqueue

        from_addr = from_addr or FROM_ADDR

        job_id = enqueue('send_email', {
            'to': to,
            'from': from_addr,
            'subject': subject,
            'body': body
        })

        return job_id
    except ImportError:
        raise ImportError("dbbasic-queue required for send_email(). Install with: pip install dbbasic-queue")


def send_template(to, template, context):
    """
    Send email using template

    Args:
        to (str): Email address
        template (str): Template name
        context (dict): Template variables

    Returns:
        str: Job ID
    """
    template_path = Path(f'templates/email/{template}.txt')
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template}")

    template_text = template_path.read_text()

    lines = template_text.split('\n')
    subject = ''
    body_lines = []
    in_body = False

    for line in lines:
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()
        elif line == '':
            in_body = True
        elif in_body:
            body_lines.append(line)

    body = '\n'.join(body_lines)

    subject = subject.format(**context)
    body = body.format(**context)

    return send_email(to, subject, body)


def read_mail(username, limit=50):
    """
    Read user's mailbox (local mail)

    Args:
        username (str): Username
        limit (int): Max messages to return

    Returns:
        list: List of message dicts
    """
    mailbox = Path(MAIL_DIR) / username
    if not mailbox.exists():
        return []

    messages = []
    current_msg = None

    with mailbox.open('r') as f:
        for line in f:
            if line.startswith('From '):
                if current_msg:
                    messages.append(current_msg)
                current_msg = {
                    'date': line.replace('From system ', '').strip(),
                    'subject': '',
                    'message_id': '',
                    'body': ''
                }
            elif current_msg:
                if line.startswith('Subject:'):
                    current_msg['subject'] = line.replace('Subject:', '').strip()
                elif line.startswith('Message-ID:'):
                    current_msg['message_id'] = line.replace('Message-ID:', '').strip()
                elif line.strip():
                    current_msg['body'] += line

        if current_msg:
            messages.append(current_msg)

    return list(reversed(messages))[:limit]


def _smtp_send_handler(payload):
    """
    Queue worker handler for sending SMTP email

    Called by dbbasic-queue worker
    """
    msg = EmailMessage()
    msg['From'] = payload['from']
    msg['To'] = payload['to']
    msg['Subject'] = payload['subject']
    msg.set_content(payload['body'])

    if SMTP_USER:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.send_message(msg)

    return {'sent_at': time.time(), 'to': payload['to']}


QUEUE_HANDLERS = {
    'send_email': _smtp_send_handler
}

__all__ = ['mail', 'send_email', 'send_template', 'read_mail', 'QUEUE_HANDLERS']
