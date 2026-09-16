# Diagnostic script - run this in Thonny instead of capture_photo.py.
# It does NOT touch the camera module, so it can't hit the
# "Failed to capture initial frame" error - it just checks the two
# most common causes of that error on generic ESP32-S3 CAM boards:
#   1) PSRAM not actually active
#   2) Camera sensor not answering on the expected I2C pins

import gc
import machine

print("---- Memory ----")
free = gc.mem_free()
print(f"gc.mem_free() = {free} bytes ({free / 1024 / 1024:.2f} MB)")
if free < 1_000_000:
    print("-> This looks like SRAM only. PSRAM is NOT active.")
    print("   A VGA/JPEG capture needs PSRAM for the frame buffer(s).")
else:
    print("-> PSRAM looks active. Good.")

print()
print("---- I2C scan on Freenove/ESP32-S3-EYE pins (SDA=4, SCL=5) ----")
try:
    i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)
    devices = i2c.scan()
    print("Found:", [hex(a) for a in devices])
    if devices:
        print("-> A device answered. 0x30 or 0x3c is typical for OV2640/OV5640.")
        print("   Pins are probably correct; the problem is likely elsewhere")
        print("   (PSRAM, XCLK frequency, or power to the camera module).")
    else:
        print("-> Nothing answered. Your board almost certainly does NOT use")
        print("   the Freenove/ESP32-S3-EYE pinout capture_photo.py assumes.")
except Exception as e:
    print("I2C scan failed to even run:", e)

print()
print("---- Also trying common alternate SDA/SCL pin pairs ----")
candidates = [
    (21, 22),  # classic AI-Thinker-style SIOD/SIOC on some S3 clones
    (17, 18),
    (15, 14),
    (2, 1),
    (40, 39),
]
for sda, scl in candidates:
    try:
        i2c = machine.I2C(0, scl=machine.Pin(scl), sda=machine.Pin(sda), freq=100000)
        devices = i2c.scan()
        if devices:
            print(f"SDA={sda}, SCL={scl} -> found {[hex(a) for a in devices]}")
        else:
            print(f"SDA={sda}, SCL={scl} -> nothing")
    except Exception as e:
        print(f"SDA={sda}, SCL={scl} -> error: {e}")
