# Run this in Thonny. It tries several XCLK frequencies and settings to find
# one that gets past "Failed to capture initial frame". We're doing this
# because the I2C scan found a sensor at 0x3c, which is the OV5640's address
# (OV2640 is 0x30) - OV5640 is fussier about clock speed than the OV2640
# the driver's defaults are tuned for.

import time
from camera import Camera, PixelFormat, FrameSize, GrabMode

# Pins from the Freenove/ESP32-S3-EYE table (confirmed correct: I2C sensor
# answered on SDA=4, SCL=5).
PIN_KWARGS = dict(
    data_pins=[11, 9, 8, 10, 12, 18, 17, 16],
    vsync_pin=6, href_pin=7, pclk_pin=13, xclk_pin=15,
    sda_pin=4, scl_pin=5,
)

xclk_freqs = [20_000_000, 24_000_000, 10_000_000, 8_000_000]

for freq in xclk_freqs:
    print(f"\n--- Trying xclk_freq={freq} ---")
    try:
        cam = Camera(
            **PIN_KWARGS,
            xclk_freq=freq,
            pixel_format=PixelFormat.RGB565,   # simpler than JPEG for this test
            frame_size=FrameSize.QQVGA,        # tiny, so timing/memory can't be the issue
            fb_count=1,
            grab_mode=GrabMode.WHEN_EMPTY,
        )
        print(f"SUCCESS at xclk_freq={freq}: sensor = {cam.sensor_name}")
        img = cam.capture()
        print(f"Captured {len(img)} bytes OK")
        cam.deinit()
        print(f"==> Use xclk_freq={freq} going forward.")
        break
    except Exception as e:
        print(f"Failed at xclk_freq={freq}: {e}")
    time.sleep(1)
else:
    print("\nNone of the XCLK frequencies worked.")
    print("Next thing to check: does this board expose a camera RESET pin")
    print("separate from the Freenove default (-1/unused)? Check the seller's")
    print("wiring diagram/silkscreen for a pin labeled CAM_RST or similar, and")
    print("pass it as reset_pin=<that GPIO> in the Camera(...) call.")
