"""
CLI commands for dbbasic-email

Commands are automatically discovered by dbbasic-cli
"""

import sys
from datetime import datetime


def queue_command(args):
    """Show email queue status"""
    print("📧 Email Queue\n")

    try:
        from dbbasic_queue import _read_tsv

        rows = _read_tsv()
        email_jobs = [row for row in rows if len(row) >= 2 and row[1] == 'send_email']

        if not email_jobs:
            print("No emails in queue")
            return

        stats = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0}

        for row in email_jobs:
            if len(row) >= 4:
                status = row[3]
                if status in stats:
                    stats[status] += 1

        print(f"Total:     {len(email_jobs)}")
        print(f"Pending:   {stats['pending']}")
        print(f"Completed: {stats['completed']}")
        print(f"Failed:    {stats['failed']}")

    except ImportError:
        print("Error: dbbasic-queue not installed")
    except Exception as e:
        print(f"Error: {e}")


def inbox_command(args):
    """View user's local mailbox"""
    if not args:
        print("Usage: dbbasic email:inbox <username>")
        return

    username = args[0]
    limit = 20

    if '-n' in args:
        idx = args.index('-n')
        if idx + 1 < len(args):
            limit = int(args[idx + 1])

    from . import read_mail

    print(f"📬 Inbox for {username}\n")

    try:
        messages = read_mail(username, limit=limit)

        if not messages:
            print("No messages")
            return

        for i, msg in enumerate(messages, 1):
            print(f"{i}. {msg['subject']}")
            print(f"   Date: {msg['date']}")
            print(f"   {msg['body'][:100]}...")
            print()

    except Exception as e:
        print(f"Error: {e}")


def send_command(args):
    """Send a test email"""
    if len(args) < 3:
        print("Usage: dbbasic email:send <to> <subject> <body>")
        print("\nExample:")
        print('  dbbasic email:send user@example.com "Hello" "Test message"')
        return

    to = args[0]
    subject = args[1]
    body = args[2]

    from . import send_email

    try:
        job_id = send_email(to, subject, body)
        print(f"✓ Email queued: {job_id}")
        print("Worker will send it via SMTP")
    except Exception as e:
        print(f"Error: {e}")


def local_command(args):
    """Send local mail to user"""
    if len(args) < 3:
        print("Usage: dbbasic email:local <username> <subject> <body>")
        print("\nExample:")
        print('  dbbasic email:local john "Test" "Hello from CLI"')
        return

    username = args[0]
    subject = args[1]
    body = args[2]

    from . import mail

    try:
        message_id = mail(username, subject, body)
        print(f"✓ Mail delivered to {username}")
        print(f"  Message ID: {message_id}")
    except Exception as e:
        print(f"Error: {e}")


def worker_command(args):
    """Run email worker (process SMTP queue)"""
    print("📧 Starting email worker...")
    print("Press Ctrl+C to stop\n")

    try:
        from dbbasic_queue import process_jobs
        from . import QUEUE_HANDLERS
        import time

        while True:
            process_jobs(QUEUE_HANDLERS, max_attempts=3)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n✓ Worker stopped")
    except ImportError:
        print("Error: dbbasic-queue not installed")
    except Exception as e:
        print(f"Error: {e}")


# Register commands with dbbasic CLI
COMMANDS = {
    'email:queue': queue_command,
    'email:inbox': inbox_command,
    'email:send': send_command,
    'email:local': local_command,
    'email:worker': worker_command,
}
