import socket
import ssl
from datetime import datetime
import sys

# List of domains to check (you can also load from a file)
DOMAINS = [
    "google.com",
]

ALERT_THRESHOLD_DAYS = 30
PORT = 443


def get_ssl_expiry_date(hostname):
    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, PORT), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_str = cert['notAfter']
                expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                return expiry_date
    except Exception as e:
        print(f"[ERROR] Could not get certificate for {hostname}: {e}")
        return None


def check_cert_expiry(hostname):
    expiry_date = get_ssl_expiry_date(hostname)
    if not expiry_date:
        return

    days_left = (expiry_date - datetime.utcnow()).days

    if days_left < 0:
        print(f"[CRITICAL] {hostname}: Certificate expired {-days_left} days ago!")
    elif days_left <= ALERT_THRESHOLD_DAYS:
        print(f"[WARNING] {hostname}: Certificate expires in {days_left} days (on {expiry_date})")
    else:
        print(f"[OK] {hostname}: Certificate is valid for {days_left} more days (until {expiry_date})")


if __name__ == "__main__":
    print("🔍 Checking SSL certificate expiry...\n")
    for domain in DOMAINS:
        check_cert_expiry(domain)

