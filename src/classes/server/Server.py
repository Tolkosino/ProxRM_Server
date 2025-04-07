from classes.server.Message import Message
import selectors
import socket
import traceback
import logging

class Server:
    
    def __init__(self,  HOST: str, PORT: int, logfile : str):
        self.logger = logging.getLogger(__name__)
        self.sel = selectors.DefaultSelector()
        self.HOST = HOST
        self.PORT = PORT
        self.logger.info(f"Server assigned Address: {self.HOST}:{self.PORT}")

    def start(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((self.HOST, self.PORT))
        lsock.listen()
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)
        self._run()

    def _accept_wrapper(self, sock):
        conn, addr = sock.accept()  
        self.logger.info(f"Accepted connection from {addr}")
        conn.setblocking(False)
        message = Message(self.sel, conn, addr)
        self.sel.register(conn, selectors.EVENT_READ, data=message)

    def _run(self):
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self._accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            self.logger.critical(f"Error: Exception for {message.addr}:\n {traceback.format_exc()}"
                            )
                            message.close()
        except KeyboardInterrupt:
            self.logger.info("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()