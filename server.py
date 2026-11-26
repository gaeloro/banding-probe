"""Server versi mungil untuk latihan CI/CD (L141) — stdlib murni.

Menyajikan versi aplikasi dari berkas versi.txt di sisinya, agar perubahan
versi yang ter-commit terlihat langsung setelah deploy.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BERKAS_VERSI = Path(__file__).with_name("versi.txt")


def baca_versi() -> str:
    return BERKAS_VERSI.read_text(encoding="utf-8").strip()


class Penangan(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/versi":
            badan = json.dumps(
                {"aplikasi": "gerbang-cd", "versi": baca_versi()}
            ).encode()
            self._kirim(200, badan)
        elif self.path == "/kesehatan":
            self._kirim(200, b'{"sehat": true}')
        else:
            self._kirim(404, b'{"galat": "tidak ditemukan"}')

    def _kirim(self, kode, badan):
        self.send_response(kode)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(badan)))
        self.end_headers()
        self.wfile.write(badan)

    def log_message(self, *args):  # senyapkan log akses
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 18141), Penangan).serve_forever()
