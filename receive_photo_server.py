# Run this ON YOUR COMPUTER (plain CPython, standard library only) to
# receive photos uploaded by send_photo_http.py.
#
# Usage:
#   python receive_photo_server.py
#
# Then set SERVER_URL in send_photo_http.py to:
#   http://<this computer's LAN IP>:5000/upload
# (find your LAN IP with `ipconfig` on Windows; must be on the same network
# as the ESP32.)

from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 5000


class UploadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length)
        with open("received_photo.jpg", "wb") as f:
            f.write(data)
        print(f"Saved {len(data)} bytes to received_photo.jpg")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), UploadHandler)
    print(f"Listening on 0.0.0.0:{PORT} ... (Ctrl+C to stop)")
    server.serve_forever()
