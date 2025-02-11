import io
import json
import selectors
import struct
import sys
import proxmox_handler
import db_userHandler
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

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {mode!r}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            print(f"Sending {self._send_buffer!r} to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
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
        print(f"Closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"Error: selector.unregister() exception for "
                f"{self.addr}: {e!r}"
            )

        try:
            self.sock.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.addr}: {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
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
            print(f"Received request {self.request!r} from {self.addr}")
        else:
            # Binary or unknown content-type
            self.request = data
            print(
                f"Received {self.jsonheader['content-type']} "
                f"request from {self.addr}"
            )
        # Set selector to listen for write events, we're done reading.
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
         
        action = self.request.get("action")
        value = self.request.get("value")
        session_id = self.request.get("session_id")
        
        answer = self._exec_remoteTask(action, value, session_id)
 
        content = {"result": answer}    
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response
    
    def get_connection(self):
        session, apiheaders = proxmox_handler.proxmox_connect()
        if session == "FAILED:":
            proxmox_handler.send_wolPackage() ## Host is offline
        else:
            return session, apiheaders
    
    def set_vmAction(self, action, value, session_id):
        vmID = value
        
        if db_userHandler.check_session_id(session_id, ""):
            session, apiheaders = self.get_connection()
            if vmID == "pve":
                return proxmox_handler.set_hostAction(action, session, apiheaders)
            return proxmox_handler.set_vmAction(action, vmID ,session, apiheaders)
        elif session_id == "REQUESTED":
            return "Access Denied but Session id Requested"
        else:
            return "Access Denied"
            
    def get_vmStatus(self, value, session_id):
        vmID = value
        
        if db_userHandler.check_session_id(session_id):
            session, apiheaders = self.get_connection()
            response = proxmox_handler.get_vmStatus(session, apiheaders, vmID)
            res = ' '
            print(f"getStatus response be like {response}")
            res = res.join(str(response))
            return res
        elif session_id == "REQUESTED":
            return "Access Denied but Session id Requested"
        else:
            return "Access Denied"
        
    def authenticate_user(self, param):
        username = param.split(";")[0]
        password = param.split(";")[1]
                
        if not db_userHandler.auth_user(username, password) == False:
            session_key = uuid5()
            return f"authn_{username}_accept;{session_key}" ##User authenticated
        else:
            return f"authn_{password}_deny" ##Login denied
        
    def get_VMsForUser(self, value, session_id):
        vms = db_userHandler.get_vms_for_user_permission(session_id)
        return ";".join(vms)
        
    def _exec_remoteTask(self, original_task, value, session_id):
        task = original_task.split(";")[0]
        match task:                                     
            case "get_VMList":                          ##Should be smth like "get_VMList;[session_id]"
                res = self.get_VMsForUser(value, session_id) 
            case "get_VMStatus":                        ##Should be smth like "get_VMStatus;[session_id]"
                res = self.get_vmStatus(value, session_id)
            case "set_VMAction":                        ##Should be smth like "set_VMAction;start;[session_id]" or "set_VMAction;stop;[session_id]"
                res = self.set_vmAction(original_task.split(";")[1], value, session_id)
            case "auth_User":                           ##Should be smth like "[username];[password]"
                res = self.authenticate_user(value)     
            case _: #default case if no match
                print("Unsupported value in vm task-selection!")
                res = "Unsupported value in vm task-selection!"
        return res
    
    
    '''
    Task = 
    set_vmAction;start;[session id]
    value =
    [vmid]
    
    Task = 
    set_vmAction;start
    value =
    [vmid];[session id]
    
    
    session_id
    Task
    Value
    
    
    '''