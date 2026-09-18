# Run this ON the ESP32-S3 in Thonny to isolate networking problems from
# the camera/JPEG code - it just connects to your server and sends a short
# message, no camera capture involved, so you can iterate fast.
#
# Pair with: python -c "import socket; s=socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(('0.0.0.0', 5000)); s.listen(1); print('listening...'); c,a=s.accept(); print('got', c.recv(100), 'from', a)"
# or just leave receive_photo_server.py / receive_photo_raw_server.py running.

import network
import socket
import time

SSID = "your-wifi-name"
PASSWORD = "your-wifi-password"
SERVER_HOST = "192.168.1.100"  # <-- the IP printed by ipconfig for the
                                #     adapter your hotspot actually uses
SERVER_PORT = 5000


def connect_wifi():
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to WiFi '{SSID}'...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    ip, subnet, gateway, dns = wlan.ifconfig()
    print("Connected.")
    print("  ESP32 IP:     ", ip)
    print("  Subnet mask:  ", subnet)
    print("  Gateway:      ", gateway)
    print("Compare the first 3 numbers of ESP32 IP against SERVER_HOST -")
    print("they must match (e.g. both 192.168.137.x) or there is no route.")


connect_wifi()

print(f"\nConnecting to {SERVER_HOST}:{SERVER_PORT} ...")
try:
    addr = socket.getaddrinfo(SERVER_HOST, SERVER_PORT)[0][-1]
    s = socket.socket()
    s.settimeout(5)
    s.connect(addr)
    s.write(b"hello from esp32\n")
    print("Connected and sent test message successfully!")
    s.close()
except OSError as e:
    print("Connection FAILED:", e)
    print("\nCheck, in order:")
    print("  1. Is a server actually listening on that host:port right now?")
    print("     (receive_photo_server.py or the one-liner above)")
    print("  2. Does SERVER_HOST match the IP of the adapter Windows/Android")
    print("     is actually using for the hotspot? Run `ipconfig` on the PC")
    print("     and match against the ESP32 IP printed above (same first 3")
    print("     octets).")
    print("  3. Is Windows Firewall blocking inbound connections on this")
    print("     port for the hotspot's network profile?")
