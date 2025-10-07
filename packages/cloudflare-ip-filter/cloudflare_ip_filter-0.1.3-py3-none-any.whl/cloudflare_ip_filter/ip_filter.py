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
    """Cloudflare IPv4 ve IPv6 adres aralıklarını indirir ve belleğe yükler."""
    global cloudflare_networks
    try:
        response = requests.get(CLOUDFLARE_IP_LIST_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            ipv4_cidrs = data["result"].get("ipv4_cidrs", [])
            ipv6_cidrs = data["result"].get("ipv6_cidrs", [])
            all_cidrs = ipv4_cidrs + ipv6_cidrs

            cloudflare_networks = [ipaddress.ip_network(cidr) for cidr in all_cidrs]
            logging.info(
                f"Cloudflare IP ranges loaded successfully. "
                f"({len(ipv4_cidrs)} IPv4, {len(ipv6_cidrs)} IPv6 networks)"
            )
        else:
            logging.error("Failed to retrieve Cloudflare IP list (API returned unsuccessful response).")

    except Exception as e:
        logging.exception(f"Error while fetching Cloudflare IPs: {e}")

def is_cloudflare_ip():
    """Gelen isteğin IPv4 veya IPv6 Cloudflare IP'lerinden gelip gelmediğini kontrol eder."""
    try:
        remote_ip = ipaddress.ip_address(request.remote_addr)
        return any(remote_ip in net for net in cloudflare_networks)
    except Exception as e:
        logging.exception(f"IP check error: {e}")
        return False

def restrict_to_cloudflare(log=True):
    """
    Flask route'ları için decorator olarak kullanılabilir.
    Sadece Cloudflare IPv4/IPv6 IP'lerinden gelen istekleri kabul eder.
    """
    if is_cloudflare_ip():
        real_ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(',')[0].strip()
        if log:
            logging.info(f"✅ Allowed access. Real IP: {real_ip}")
    else:
        if log:
            logging.warning(f"❌ Blocked IP access: {request.remote_addr}")
        abort(403)
