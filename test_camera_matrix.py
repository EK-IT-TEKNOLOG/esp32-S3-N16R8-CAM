# Run this in Thonny. Tests pixel_format x frame_size combinations, each with
# a FRESH Camera() construction (no reconfigure()), fb_count=1,
# grab_mode=WHEN_EMPTY, xclk_freq=20MHz - the settings already confirmed to
# work for RGB565/QQVGA. This tells us whether JPEG itself is the problem,
# or whether it's specifically the jump to a bigger frame size (VGA).

import time
from camera import Camera, PixelFormat, FrameSize, GrabMode

PIN_KWARGS = dict(
    data_pins=[11, 9, 8, 10, 12, 18, 17, 16],
    vsync_pin=6, href_pin=7, pclk_pin=13, xclk_pin=15,
    sda_pin=4, scl_pin=5,
)

combos = [
    ("RGB565", PixelFormat.RGB565, "QQVGA", FrameSize.QQVGA),
    ("RGB565", PixelFormat.RGB565, "QVGA",  FrameSize.QVGA),
    ("RGB565", PixelFormat.RGB565, "VGA",   FrameSize.VGA),
    ("JPEG",   PixelFormat.JPEG,   "QQVGA", FrameSize.QQVGA),
    ("JPEG",   PixelFormat.JPEG,   "QVGA",  FrameSize.QVGA),
    ("JPEG",   PixelFormat.JPEG,   "VGA",   FrameSize.VGA),
]

for fmt_name, fmt, size_name, size in combos:
    print(f"\n--- {fmt_name} / {size_name} ---")
    try:
        with Camera(
            **PIN_KWARGS,
            xclk_freq=20_000_000,
            pixel_format=fmt,
            frame_size=size,
            fb_count=1,
            grab_mode=GrabMode.WHEN_EMPTY,
        ) as cam:
            img = None
            for _ in range(20):
                img = cam.capture()
                if img:
                    break
                time.sleep_ms(100)
            if img:
                print(f"OK: captured {len(img)} bytes")
            else:
                print("FAIL: capture() kept returning None")
    except Exception as e:
        print(f"FAIL at construction: {e}")
    time.sleep(1)  # let the hardware fully settle between tests
