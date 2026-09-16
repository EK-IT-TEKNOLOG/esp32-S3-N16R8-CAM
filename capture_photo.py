# Run this ON the ESP32-S3 in Thonny (Run > Run current script, board must be
# flashed with firmware from https://github.com/cnadler86/micropython-camera-API,
# which is the repo already cloned next to this file).
#
# It takes one photo and stores it in the ESP32's own flash filesystem.
# To get the file onto your laptop afterwards, use Thonny's file browser:
#   View > Files  ->  right-click "photo.jpg" under "MicroPython device"
#   -> "Download to ..." and pick a folder on your computer.
#
# This board's sensor is an OV5640 (confirmed via I2C scan, address 0x3c).
# Its hardware JPEG capture path is broken on this board/firmware combo
# (pixel_format=JPEG fails at construction, at every resolution - confirmed
# by testing), while RGB565 capture works fine at any resolution.
# Workaround: capture raw RGB565 and encode it to JPEG in software using the
# `jpeg` module (mp_jpeg), which this firmware also bundles.

import jpeg
from camera import Camera, PixelFormat, FrameSize, GrabMode

FILENAME = "/photo.jpg"

# Pins from the Freenove/ESP32-S3-EYE table - confirmed correct for this
# board (I2C sensor answered on SDA=4, SCL=5).
PIN_KWARGS = dict(
    data_pins=[11, 9, 8, 10, 12, 18, 17, 16],
    vsync_pin=6, href_pin=7, pclk_pin=13, xclk_pin=15,
    sda_pin=4, scl_pin=5,
)

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

print(f"Captured {width}x{height} RGB565 frame ({len(raw)} bytes). Encoding to JPEG...")

# The camera's raw RGB565 output is big-endian by default (esp32-camera
# convention). If the saved photo comes out with scrambled/wrong colors,
# switch this to "RGB565_LE".
encoder = jpeg.Encoder(width=width, height=height, pixel_format="RGB565_BE", quality=85)
jpeg_data = encoder.encode(raw)

with open(FILENAME, "wb") as f:
    f.write(jpeg_data)

print(f"Saved {len(jpeg_data)} bytes to {FILENAME} on the ESP32.")
print("Now open View > Files in Thonny and download it to your computer.")
