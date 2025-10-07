import requests
import ipaddress
import logging
from flask import request, abort

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("cloudflare_access.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

CLOUDFLARE_IP_LIST_URL = "https://api.cloudflare.com/client/v4/ips"
cloudflare_networks = []


def fetch_cloudflare_ips():
    """Cloudflare IP listesini indirir ve belleğe yükler."""
    global cloudflare_networks
    try:
        response = requests.get(CLOUDFLARE_IP_LIST_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            ipv4_cidrs = data["result"]["ipv4_cidrs"]
            cloudflare_networks = [ipaddress.ip_network(cidr) for cidr in ipv4_cidrs]
            logging.info("Cloudflare IP ranges loaded successfully.")
        else:
            logging.error("Failed to retrieve Cloudflare IP list (API returned unsuccessful response).")

    except Exception as e:
        logging.exception(f"Error while fetching Cloudflare IPs: {e}")


def is_cloudflare_ip():
    """Gelen isteğin Cloudflare IP'lerinden gelip gelmediğini kontrol eder."""
    try:
        remote_ip = ipaddress.ip_address(request.remote_addr)
        return any(remote_ip in net for net in cloudflare_networks)
    except Exception as e:
        logging.exception(f"IP check error: {e}")
        return False


def restrict_to_cloudflare(log=True):
    """
    Flask route'ları için decorator olarak kullanılabilir.
    Sadece Cloudflare IP'lerinden gelen istekleri kabul eder.
    """
    if is_cloudflare_ip():
        real_ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(',')[0].strip()
        if log:
            logging.info(f"Allowed access. Real IP: {real_ip}")
    else:
        if log:
            logging.warning(f"Blocked IP access: {request.remote_addr}")
        abort(403)
