# Run this ON the ESP32-S3 in Thonny. The fastest option: no HTTP at all,
# just a raw TCP connection carrying a 4-byte big-endian length prefix
# followed by the JPEG bytes, sent in a single socket write.
#
# Needs receive_photo_raw_server.py (not receive_photo_server.py) running
# on your computer - this is NOT an HTTP request, a plain HTTP server
# cannot parse it.

import time
import socket
import struct
import network
import jpeg
from camera import Camera, PixelFormat, FrameSize, GrabMode

SSID = "your-wifi-name"
PASSWORD = "your-wifi-password"
SERVER_HOST = "192.168.1.100"  # your computer's IP
SERVER_PORT = 5001

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


def send_jpeg_raw(host, port, data):
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    try:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except (AttributeError, OSError):
        pass
    s.write(struct.pack(">I", len(data)) + data)  # length header + body, one write
    s.close()


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

print(f"Sending {len(jpeg_data)} bytes to {SERVER_HOST}:{SERVER_PORT} (raw TCP) ...")
t0 = time.ticks_ms()
send_jpeg_raw(SERVER_HOST, SERVER_PORT, jpeg_data)
elapsed = time.ticks_diff(time.ticks_ms(), t0)
print(f"Done in {elapsed} ms.")
