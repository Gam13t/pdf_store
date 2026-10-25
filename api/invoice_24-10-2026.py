
import json
import logging
import ipaddress
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ip_logger")

PDF_PATH = "/1792834085440_733yqhhte7zif2ogf0qr1b0l7rtdmhus_wm.pdf"


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        geo = {
            "country": self.headers.get("x-vercel-ip-country"),
            "region": self.headers.get("x-vercel-ip-country-region"),
            "city": self.headers.get("x-vercel-ip-city"),
            "latitude": self.headers.get("x-vercel-ip-latitude"),
            "longitude": self.headers.get("x-vercel-ip-longitude"),
            "postal_code": self.headers.get("x-vercel-ip-postal-code"),
        }
        # Vercel provides the client's IP through these headers.
        raw_ip = (
            self.headers.get("x-real-ip")
            or self.headers.get("x-forwarded-for", "").split(",")[0].strip()
        )

        try:
            client_ip = str(ipaddress.ip_address(raw_ip))
            ip_version = ipaddress.ip_address(raw_ip).version
        except ValueError:
            client_ip = None
            ip_version = None

        # Record the request in Vercel function logs.
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip": client_ip,
            "ip_version": ip_version,
            "path": self.path.split("?")[0],
            "method": "GET",
            "geo": geo,
        }

        logger.info(json.dumps(entry))

        # Redirect to the PDF after logging.
        self.send_response(302)
        self.send_header("Location", PDF_PATH)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_HEAD(self):
        # Support HEAD requests without returning a response body.
        self.send_response(302)
        self.send_header("Location", PDF_PATH)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
