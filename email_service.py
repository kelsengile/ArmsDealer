# ──────────────────────────────────────────────────────────────────────────────────
# EMAIL_SERVICE.PY
# Centralised email sending for ArmsDealer notifications.
# Reads SMTP config from .env via os.environ (loaded by armsdealer.py).
# ──────────────────────────────────────────────────────────────────────────────────

import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


# ─────────────────────────────────────────
# SMTP CONFIG (from .env)
# ─────────────────────────────────────────

def _get_smtp_config():
    return {
        'host':     os.environ.get('SMTP_HOST', 'smtp.gmail.com'),
        'port':     int(os.environ.get('SMTP_PORT', 0)),   # 0 = auto-select
        'user':     os.environ.get('SMTP_USER', ''),
        'password': os.environ.get('SMTP_PASS', ''),
        'from':     os.environ.get('MAIL_FROM', os.environ.get('SMTP_USER', '')),
        'use_tls':  os.environ.get('SMTP_USE_TLS', 'true').lower() == 'true',
    }


def _send(to_email: str, subject: str, html_body: str) -> bool:
    """Send a single email. Returns True on success, False on failure.

    Port strategy (in priority order):
      443 — Gmail accepts SMTP here; works even when 587/465 are firewall-blocked
      465 — SMTP over SSL (implicit TLS)
      587 — STARTTLS (original default; kept as last resort)
    If SMTP_PORT is explicitly set in .env (non-zero), only that port is tried.
    """
    cfg = _get_smtp_config()
    if not cfg['user'] or not cfg['password']:
        # No SMTP credentials configured — skip silently
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = cfg['from']
    msg['To'] = to_email
    msg.attach(MIMEText(html_body, 'html'))

    host = cfg['host']
    explicit_port = cfg['port']

    # Build ordered list of (port, use_ssl) attempts
    if explicit_port:
        # Honour whatever is in .env
        use_ssl = explicit_port in (443, 465)
        attempts = [(explicit_port, use_ssl)]
    else:
        # Auto-select: try 443 first (punches through most firewalls),
        # then 465 (SSL), then 587 (STARTTLS)
        attempts = [(443, True), (465, True), (587, False)]

    last_exc = None
    for port, use_ssl in attempts:
        try:
            if use_ssl:
                with smtplib.SMTP_SSL(host, port, timeout=10) as server:
                    server.login(cfg['user'], cfg['password'])
                    server.sendmail(cfg['from'], to_email, msg.as_string())
            else:
                with smtplib.SMTP(host, port, timeout=10) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(cfg['user'], cfg['password'])
                    server.sendmail(cfg['from'], to_email, msg.as_string())
            print(f'[EmailService] Sent to {to_email} via port {port}')
            return True
        except Exception as exc:
            print(f'[EmailService] Port {port} failed: {exc}')
            last_exc = exc

    # All ports exhausted
    print(f'[EmailService] Failed to send to {to_email}: {last_exc}')
    return False


# ─────────────────────────────────────────
# NOTIFICATION PREFERENCE HELPERS
# ─────────────────────────────────────────

def _get_notif_prefs(db, user_id: int) -> dict:
    """Fetch notification prefs JSON from DB. Returns dict with defaults."""
    defaults = {
        'email_enabled':       True,
        'in_app_enabled':      True,
        'order_updates':       True,   # email on order status changes
        'security_alerts':     True,   # email on login
        'promotional_offers':  False,  # empty for now
        'quiet_hours_enabled': False,
        'quiet_from':          '22:00',
        'quiet_until':         '07:00',
    }
    try:
        row = db.execute(
            "SELECT notification_prefs FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row and row['notification_prefs']:
            saved = json.loads(row['notification_prefs'])
            defaults.update(saved)
    except Exception:
        pass
    return defaults


def _is_quiet_hours(prefs: dict) -> bool:
    """Return True if current time falls within quiet hours."""
    if not prefs.get('quiet_hours_enabled'):
        return False
    try:
        now_str = datetime.now().strftime('%H:%M')
        now_h, now_m = map(int, now_str.split(':'))
        from_h, from_m = map(int, prefs.get('quiet_from', '22:00').split(':'))
        until_h, until_m = map(int, prefs.get(
            'quiet_until', '07:00').split(':'))
        now_mins = now_h * 60 + now_m
        from_mins = from_h * 60 + from_m
        until_mins = until_h * 60 + until_m
        if from_mins <= until_mins:
            return from_mins <= now_mins < until_mins
        else:  # overnight window (e.g. 22:00 → 07:00)
            return now_mins >= from_mins or now_mins < until_mins
    except Exception:
        return False


def _should_send_email(db, user_id: int, category: str) -> bool:
    """
    Check whether an email should be sent for this user/category.
    category: 'order_updates' | 'security_alerts' | 'promotional_offers'
    """
    prefs = _get_notif_prefs(db, user_id)
    if not prefs.get('email_enabled', True):
        return False
    if not prefs.get(category, True):
        return False
    # Quiet hours suppresses non-critical (security is always sent)
    if category != 'security_alerts' and _is_quiet_hours(prefs):
        return False
    return True


# ─────────────────────────────────────────
# EMAIL TEMPLATES
# ─────────────────────────────────────────

_BASE_STYLE = """
    body { margin:0; padding:0; background:#0a0f0b; font-family: 'Courier New', monospace; color:#c8d8c0; }
    .wrap { max-width:600px; margin:0 auto; background:#111a12; border:1px solid #2a3a2a; }
    .header { background:#1a2a1a; padding:24px 32px; border-bottom:2px solid #a8c47a; }
    .header h1 { margin:0; font-size:20px; color:#a8c47a; letter-spacing:3px; text-transform:uppercase; }
    .header p  { margin:4px 0 0; font-size:11px; color:#5a7a5a; letter-spacing:2px; }
    .body  { padding:32px; }
    .body h2 { margin:0 0 16px; font-size:14px; color:#a8c47a; letter-spacing:2px; text-transform:uppercase; }
    .body p  { margin:0 0 12px; font-size:12px; line-height:1.7; color:#a0b898; }
    .table { width:100%; border-collapse:collapse; margin:16px 0; font-size:12px; }
    .table th { background:#1a2a1a; color:#a8c47a; padding:8px 12px; text-align:left; letter-spacing:1px; font-size:11px; }
    .table td { padding:8px 12px; border-bottom:1px solid #1e2e1e; color:#a0b898; }
    .badge { display:inline-block; padding:3px 10px; border-radius:2px; font-size:10px; letter-spacing:2px; text-transform:uppercase; font-weight:bold; }
    .badge-placed   { background:#1a3a1a; color:#a8c47a; border:1px solid #a8c47a44; }
    .badge-packing  { background:#3a2a00; color:#e8b84b; border:1px solid #e8b84b44; }
    .badge-shipping { background:#00203a; color:#5b9bd5; border:1px solid #5b9bd544; }
    .badge-delivered{ background:#1a3a2a; color:#4caf87; border:1px solid #4caf8744; }
    .badge-cancelled{ background:#3a1a1a; color:#c0392b; border:1px solid #c0392b44; }
    .footer { padding:16px 32px; border-top:1px solid #1e2e1e; font-size:10px; color:#3a5a3a; letter-spacing:1px; }
    .divider { border:none; border-top:1px solid #1e2e1e; margin:20px 0; }
"""


def _html_wrap(content: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>{_BASE_STYLE}</style></head>
<body>
<div class="wrap">
  <div class="header">
    <h1>&#9654; ArmsDealer</h1>
    <p>TACTICAL ARMS &amp; EQUIPMENT</p>
  </div>
  <div class="body">{content}</div>
  <div class="footer">
    &copy; ArmsDealer.com &nbsp;|&nbsp; This is an automated message. Do not reply.
  </div>
</div>
</body></html>"""


# ─────────────────────────────────────────
# PUBLIC FUNCTIONS
# ─────────────────────────────────────────

def send_order_confirmation(db, user_id: int, order_id: int, order_items: list,
                            total: float, payment_method: str, user_email: str,
                            username: str) -> bool:
    """Send checkout confirmation email to the user."""
    if not _should_send_email(db, user_id, 'order_updates'):
        return False

    rows_html = ''.join(
        f"<tr><td>{item.get('name', '—')}</td>"
        f"<td>{item.get('quantity', 1)}</td>"
        f"<td>₱{float(item.get('price', 0) * item.get('quantity', 1)):,.2f}</td></tr>"
        for item in order_items
    )

    pay_label = 'Wallet Balance' if payment_method == 'wallet' else 'Cash on Delivery'

    content = f"""
<h2>Order Confirmed</h2>
<p>Hello <strong>{username}</strong>,</p>
<p>Your order <strong>#{order_id}</strong> has been received and is now being processed.</p>
<table class="table">
  <thead><tr><th>ITEM</th><th>QTY</th><th>SUBTOTAL</th></tr></thead>
  <tbody>{rows_html}</tbody>
</table>
<hr class="divider">
<p>
  <strong>Total:</strong> ₱{total:,.2f}<br>
  <strong>Payment:</strong> {pay_label}<br>
  <strong>Status:</strong> <span class="badge badge-placed">Order Placed</span>
</p>
<p>You will receive updates as your order progresses through packing and shipping.</p>
"""
    return _send(user_email, f'[ArmsDealer] Order #{order_id} Confirmed', _html_wrap(content))


def send_order_status_update(db, user_id: int, order_id: int, new_status: str,
                             user_email: str, username: str) -> bool:
    """Send order status change email (packing / shipping / delivered)."""
    if not _should_send_email(db, user_id, 'order_updates'):
        return False

    status_messages = {
        'packing':   ('Order Being Packed', 'Your order is now being carefully packed and prepared for dispatch.'),
        'shipping':  ('Order Shipped',       'Your order is on its way! Expect delivery within the estimated timeframe.'),
        'delivered': ('Order Delivered',     'Your order has been delivered. Thank you for choosing ArmsDealer!'),
        'cancelled': ('Order Cancelled',     'Your order has been cancelled. If you paid via wallet, a refund has been issued.'),
    }

    if new_status not in status_messages:
        return False

    title, message = status_messages[new_status]
    badge_class = f'badge-{new_status}'

    content = f"""
<h2>{title}</h2>
<p>Hello <strong>{username}</strong>,</p>
<p>Your order <strong>#{order_id}</strong> status has been updated.</p>
<p>
  <strong>New Status:</strong> <span class="badge {badge_class}">{new_status.upper()}</span>
</p>
<hr class="divider">
<p>{message}</p>
<p>Log in to your account to view full order details.</p>
"""
    subject = f'[ArmsDealer] Order #{order_id} — {title}'
    return _send(user_email, subject, _html_wrap(content))


def send_login_notification(db, user_id: int, user_email: str, username: str,
                            ip_address: str = None) -> bool:
    """Send security login notification email."""
    if not _should_send_email(db, user_id, 'security_alerts'):
        return False

    now = datetime.now().strftime('%B %d, %Y at %H:%M')
    ip_info = f'<br><strong>IP Address:</strong> {ip_address}' if ip_address else ''

    content = f"""
<h2>New Login Detected</h2>
<p>Hello <strong>{username}</strong>,</p>
<p>A login to your ArmsDealer account was detected.</p>
<p>
  <strong>Time:</strong> {now}{ip_info}
</p>
<hr class="divider">
<p>If this was you, no action is needed. If you did not log in, please change your password immediately and contact support.</p>
"""
    return _send(user_email, '[ArmsDealer] Security — New Login Detected', _html_wrap(content))
