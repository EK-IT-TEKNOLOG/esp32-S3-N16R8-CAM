# Run this ON YOUR COMPUTER (plain CPython, standard library only) to
# receive photos from send_photo_raw_tcp.py.
#
# Protocol: connect, send a 4-byte big-endian length prefix, then that many
# bytes of JPEG data, then the sender closes the connection.
#
# Usage:
#   python receive_photo_raw_server.py
#
# Then set SERVER_HOST in send_photo_raw_tcp.py to this computer's LAN IP.

import socket

HOST = "0.0.0.0"
PORT = 5001


def recvall(conn, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("connection closed before all data was received")
        buf.extend(chunk)
    return bytes(buf)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(1)
        print(f"Listening on {HOST}:{PORT} ... (Ctrl+C to stop)")
        while True:
            conn, addr = srv.accept()
            with conn:
                length = int.from_bytes(recvall(conn, 4), "big")
                data = recvall(conn, length)
                with open("received_photo_raw.jpg", "wb") as f:
                    f.write(data)
                print(f"Saved {len(data)} bytes from {addr[0]} to received_photo_raw.jpg")


if __name__ == "__main__":
    main()
