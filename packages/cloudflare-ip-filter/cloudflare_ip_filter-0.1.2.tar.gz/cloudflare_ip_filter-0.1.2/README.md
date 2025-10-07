# Cloudflare IP Restriction Middleware for Flask

This is a simple Flask middleware module that restricts access to your Flask application **only** to requests coming from Cloudflare's official IPv4 ranges.

---

## Features

- Automatically fetches the current list of Cloudflare IPv4 ranges from Cloudflare's API.
- Checks incoming request IPs against the Cloudflare IP ranges.
- Blocks any request from IPs outside Cloudflare's ranges with HTTP 403 Forbidden.
- Logs allowed and blocked requests in color-coded terminal output using `colorama`.
- Uses only the standard `request.remote_addr` for IP checking (does not rely on `X-Forwarded-For` for filtering, but logs the real IP if present).

---

## Requirements

- Python 3.7+
- Flask
- requests
- colorama

Install dependencies with:

```bash
pip install flask requests colorama
```

---

## Usage

1. Import and call `fetch_cloudflare_ips()` once at app startup to load IP ranges:

```python
from utils.ip_filter import fetch_cloudflare_ips, restrict_to_cloudflare

app = Flask(__name__)
fetch_cloudflare_ips()
```

2. Add `restrict_to_cloudflare` as a before-request hook to block unauthorized IPs:

```python
@app.before_request
def check_ip():
    restrict_to_cloudflare()
```

3. Your app will now only accept requests coming through Cloudflare's IPv4 proxies.

---

## How it works

- The module fetches Cloudflare's current IPv4 CIDR blocks from their API.
- Every incoming request's IP (`request.remote_addr`) is checked if it belongs to any of those CIDRs.
- If yes, access is allowed and the real client IP (from `X-Forwarded-For` header if present) is logged in green.
- Otherwise, the request is aborted with HTTP 403, and the blocked IP is logged in red.

---

## Notes

- This module **does not** handle IPv6 addresses.
- It assumes your Flask app is running behind Cloudflare proxy.
- The `X-Forwarded-For` header is only used for logging purposes, **not** for access control.
- You may want to run `fetch_cloudflare_ips()` periodically (e.g. daily) to keep IP ranges up to date.

---

## Example output

```
Cloudflare IP ranges loaded successfully.
✅ Allowed access. Real IP: 203.0.113.45
⛔️ Blocked IP access: 198.51.100.23
```

---

## License

MIT License

---

Feel free to contribute or ask questions!
