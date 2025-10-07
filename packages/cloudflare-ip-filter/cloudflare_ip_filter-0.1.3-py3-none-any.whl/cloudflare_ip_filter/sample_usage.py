from flask import Flask
from cloudflare_ip_filter import fetch_cloudflare_ips, restrict_to_cloudflare

app = Flask(__name__)
fetch_cloudflare_ips()

@app.before_request
def check_ip():
    restrict_to_cloudflare(True)

@app.route('/')
def index():
    return "This page is protected by Cloudflare."
