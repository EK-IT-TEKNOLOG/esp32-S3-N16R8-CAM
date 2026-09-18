# Run this ON the ESP32-S3 in Thonny (same board/setup as capture_photo.py).
#
# Connects to WiFi, captures one photo, and uploads it to a server over
# HTTP using the MicroPython `requests` library.
#
# One-time setup (from the Thonny REPL, board connected to WiFi):
#   import network
#   wlan = network.WLAN(network.WLAN.IF_STA)
#   wlan.active(True)
#   wlan.connect("your-ssid", "your-password")
#   # wait until wlan.isconnected() is True, then:
#   import mip
#   mip.install("requests")
#
# Pair this with receive_photo_server.py running on your computer to test.

import time
import network
import requests
import jpeg
from camera import Camera, PixelFormat, FrameSize, GrabMode

SSID = "your-wifi-name"
PASSWORD = "your-wifi-password"
SERVER_URL = "http://192.168.1.100:5000/upload"  # your computer's IP:port

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

# Same big-endian/little-endian caveat as capture_photo.py - switch to
# "RGB565_LE" if colors come out scrambled.
encoder = jpeg.Encoder(width=width, height=height, pixel_format="RGB565_BE", quality=85)
jpeg_data = encoder.encode(raw)

print(f"Sending {len(jpeg_data)} bytes to {SERVER_URL} ...")
response = requests.post(
    SERVER_URL,
    data=jpeg_data,
    headers={"Content-Type": "image/jpeg"},
)
print("Server responded:", response.status_code, response.text)
response.close()
