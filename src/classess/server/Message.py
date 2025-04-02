import io
import json
import selectors
import struct
import sys
from proxFacade import ProxFacade
import logging
from uuid import uuid5

class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self.logger = logging.getLogger(__name__)

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            self.logger.critical(f"Invalid events mask mode {mode!r}!")
            raise ValueError(f"Invalid events mask mode {mode!r}!")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            self.logger.debug("Resource temporarily unavailable (errno EWOULDBLOCK)")
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                self.logger.critical("Peer closed!")
                raise RuntimeError("Peer closed!")

    def _write(self):
        if self._send_buffer:
            self.logger.debug(f"Sending {self._send_buffer!r} to {self.addr}")

            try:
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                self.logger.debug("Resource temporarily unavailable (errno EWOULDBLOCK)")
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                if sent and not self._send_buffer:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message
    
    def _create_response_binary_content(self):
        response = {
            "content_bytes": b"First 10 bytes of request: "
            + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

    def close(self):
        self.logger.info(f"Closing connection to {self.addr}")

        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            self.logger.warning(f"Error: selector.unregister() exception for {self.addr}: {e!r}")

        try:
            self.sock.close()
        except OSError as e:
            self.logger.warning(f"Error: socket.close() exception for {self.addr}: {e!r}")
        finally:
            self.sock = None

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    self.logger.warning(f"Missing required header '{reqhdr}'.")
                    raise ValueError(f"Missing required header '{reqhdr}'.")

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            self.logger.info(f"Received request {self.request!r} from {self.addr}")
        else:
            self.request = data
            self.logger.debug(f"Received {self.jsonheader['content-type']} request from {self.addr}")

        self._set_selector_events_mask("w")

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            # Binary or unknown content-type
            response = self._create_response_binary_content()
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message

    def _create_response_json_content(self):
         
        command = self.request.get("command")
        action = self.request.get("action")
        vmid = self.request.get("vmid")
        session_id = self.request.get("session_id")
        
        answer = self._exec_remoteTask(self.request)
 
        content = {"result": answer}    
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response
    
    def _exec_remoteTask(self, cmd_set):
        proxFacade = ProxFacade()
        return proxFacade.executeAction(cmd_set)


    '''
    every request has:
    {
        session_id = [session_id]
        vm = [vmid]
    }

    with following pairs of Task and action:
    {
        Task = [set_vmAction]
        Action = [start|stop]
    },
    {    
        Task = [get_VMList]
        Action = []
    },
    {    
        Task = [get_VMStatus]
        Action = []
    },
    {
        Task = [auth_User]
        Action = [[username];[password]]
    }   
    '''