
import json
import logging
import ipaddress
from datetime import datetime, timezone
from pathlib import Path
from http.server import BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ip_logger")

PDF_PATH = (
    Path(__file__).resolve().parent.parent
    / "public"
    / "1792834085440_733yqhhte7zif2ogf0qr1b0l7rtdmhus_wm.pdf"
)


class handler(BaseHTTPRequestHandler):

    def log_request_ip(self, method):
        raw_ip = (
            self.headers.get("x-real-ip")
            or self.headers.get("x-forwarded-for", "").split(",")[0].strip()
        )

        try:
            client_ip = str(ipaddress.ip_address(raw_ip))
        except ValueError:
            client_ip = None

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip": client_ip,
            "path": self.path.split("?", 1)[0],
            "method": method,
        }

        logger.info(json.dumps(entry))

    def do_GET(self):
        self.log_request_ip("GET")

        if not PDF_PATH.is_file():
            self.send_error(404, "PDF not found")
            return

        try:
            pdf_data = PDF_PATH.read_bytes()
        except OSError:
            logger.exception("Failed to read PDF")
            self.send_error(500, "Could not read PDF")
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header(
            "Content-Disposition",
            'inline; filename="document.pdf"'
        )
        self.send_header("Content-Length", str(len(pdf_data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(pdf_data)

    def do_HEAD(self):
        self.log_request_ip("HEAD")

        if not PDF_PATH.is_file():
            self.send_error(404, "PDF not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(PDF_PATH.stat().st_size))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
