# Run this ON the ESP32-S3 in Thonny. Same as send_photo_http.py, but skips
# the MicroPython `requests` library (slow: extra allocations, multiple
# small socket writes, full response parsing) in favor of a hand-built
# HTTP request sent in a single socket write.
#
# Wire-compatible with receive_photo_server.py - no server changes needed.
#
# No `mip.install("requests")` needed for this version.

import time
import socket
import network
import jpeg
from camera import Camera, PixelFormat, FrameSize, GrabMode

SSID = "your-wifi-name"
PASSWORD = "your-wifi-password"
SERVER_HOST = "192.168.1.100"  # your computer's IP, no scheme/port
SERVER_PORT = 5000
SERVER_PATH = "/upload"

# Pins from the Freenove/ESP32-S3-EYE table - same as capture_photo.py.
PIN_KWARGS = dict(
    data_pins=[11, 9, 8, 10, 12, 18, 17, 16],
    vsync_pin=6, href_pin=7, pclk_pin=13, xclk_pin=15,
    sda_pin=4, scl_pin=5,
)


def connect_wifi():
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to WiFi '{SSID}'...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Connected, IP:", wlan.ifconfig()[0])


def post_jpeg_fast(host, port, path, data):
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    try:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except (AttributeError, OSError):
        pass  # not all ports expose TCP_NODELAY - fine to skip

    header = (
        "POST {path} HTTP/1.1\r\n"
        "Host: {host}\r\n"
        "Content-Type: image/jpeg\r\n"
        "Content-Length: {length}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(path=path, host=host, length=len(data)).encode()

    s.write(header + data)  # header+body in one write - avoids extra round trips

    response = b""
    while True:
        chunk = s.recv(512)
        if not chunk:
            break
        response += chunk
    s.close()
    return response


connect_wifi()

with Camera(
    **PIN_KWARGS,
    xclk_freq=20_000_000,
    pixel_format=PixelFormat.RGB565,
    frame_size=FrameSize.VGA,
    fb_count=1,
    grab_mode=GrabMode.WHEN_EMPTY,
) as cam:
    print("Camera initialized:", cam.sensor_name)
    width, height = cam.pixel_width, cam.pixel_height

    print("Capturing raw frame...")
    raw = bytes(cam.capture())
    cam.free_buffer()

print(f"Captured {width}x{height} RGB565 frame. Encoding to JPEG...")

encoder = jpeg.Encoder(width=width, height=height, pixel_format="RGB565_BE", quality=85)
jpeg_data = encoder.encode(raw)

print(f"Sending {len(jpeg_data)} bytes to http://{SERVER_HOST}:{SERVER_PORT}{SERVER_PATH} ...")
t0 = time.ticks_ms()
response = post_jpeg_fast(SERVER_HOST, SERVER_PORT, SERVER_PATH, jpeg_data)
elapsed = time.ticks_diff(time.ticks_ms(), t0)
print(f"Done in {elapsed} ms. Server response:")
print(response.decode("utf-8", "ignore"))
