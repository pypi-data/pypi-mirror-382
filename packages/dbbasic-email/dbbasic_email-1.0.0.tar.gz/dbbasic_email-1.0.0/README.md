# dbbasic-email

Simple email queue with Unix mail support.

> "Email is Unix mail. Queuing is sendmail. Templates are heredocs."

## Features

- **Local Mail**: Unix-style mailboxes for internal notifications (instant delivery)
- **External Email**: SMTP delivery via dbbasic-queue (async, retry logic)
- **Simple Templates**: Plain text templates with string formatting
- **Zero Config**: Works with localhost SMTP out of the box
- **Minimal**: ~200 lines, stdlib only (queue optional)

## Installation

```bash
pip install dbbasic-email
```

For external email (SMTP queue):
```bash
pip install dbbasic-email[queue]
```

## Quick Start

### Local Mail (Internal Notifications)

```python
from dbbasic_email import mail

# Send to user on same app
mail('john', 'New comment', 'Jane commented on your post')
# → Appends to var/mail/john (instant)

# Read mailbox
from dbbasic_email import read_mail
messages = read_mail('john', limit=20)
for msg in messages:
    print(f"{msg['subject']}: {msg['body']}")
```

### External Email (SMTP)

```python
from dbbasic_email import send_email

# Queue for delivery
job_id = send_email(
    to='user@gmail.com',
    subject='Welcome!',
    body='Thanks for signing up'
)
# Returns immediately (queued)
```

### Templates

```python
from dbbasic_email import send_template

# templates/email/welcome.txt
send_template('user@gmail.com', 'welcome', {
    'username': 'john',
    'app_url': 'https://myapp.com'
})
```

## Configuration

Set environment variables for SMTP:

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your@gmail.com
export SMTP_PASSWORD=your-app-password
export FROM_ADDR=noreply@myapp.com
```

For local development:
```bash
python -m smtpd -n -c DebuggingServer localhost:1025
export SMTP_HOST=localhost SMTP_PORT=1025
```

## CLI Commands

```bash
# Send local mail
dbbasic email:local john "Test" "Hello from CLI"

# View inbox
dbbasic email:inbox john

# Send external email (queued)
dbbasic email:send user@example.com "Hello" "Test"

# View queue status
dbbasic email:queue

# Run worker (process SMTP queue)
dbbasic email:worker
```

## How It Works

### Local Mail (Unix-style)

```
mail('john', subject, body)
  ↓
Append to var/mail/john (mbox format)
  ↓
Instant delivery
```

### External Email (SMTP)

```
send_email(to, subject, body)
  ↓
Queue via dbbasic-queue
  ↓
Worker picks up
  ↓
Send via SMTP (with retries)
```

## Philosophy

Email is **not a cloud service**. Unix had local mail working in 1971. The web made it complicated. Let's return to simplicity.

- **Unix Mail First**: Local delivery to var/mail/{user}
- **SMTP When Needed**: External email via SMTP (like sendmail)
- **Queue Integration**: Uses dbbasic-queue for async delivery
- **Plain Text First**: Templates are just string formatting
- **No Service Required**: Works without external email service

## Full Documentation

See the [specification](http://dbbasic.com/email-spec) for complete details.

## License

MIT
