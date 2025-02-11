#!/usr/bin/env python3

import selectors
import socket
import sys
import traceback
import libserver
import db_controller


sel = selectors.DefaultSelector()
print(",".join(sys.argv))
def accept_wrapper(sock):
    conn, addr = sock.accept()  
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <port>")
    sys.exit(1)

host = ""
port = int(sys.argv[1])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

print("Warte auf Datenbankinitialisierung...")
db_controller.setup_db()

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        f"Main: Error: Exception for {message.addr}:\n"
                        f"{traceback.format_exc()}"
                    )
                    message.close()
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
