import selectors
import socket
import libclient  # Assuming this is your module

class connection:
    def __init__(self):
        # Initialize the selector if it isn't already initialized
        if not hasattr(self, 'sel') or self.sel is None:
            self.sel = selectors.DefaultSelector()
        print(f"self.sel initialized to: {self.sel}")

    def _create_request(self, value, action, session_id):
        if value != "pve":
            vmid = int(value)
        else:
            vmid = "pve"
            
            
        if (isinstance(vmid, int) or (vmid == "pve")) and (action == "get_VMStatus" or (action == "set_VMAction;stop" or action == "set_VMAction;start")):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, value=value, session_id=session_id),
            )
        else:
            return dict(
                type="binary/custom-client-binary-type",
                encoding="binary",
                content=bytes(action + value + session_id, encoding="utf-8"),
            )

    def _start_connection(self, host, port, request):
        # Ensure self.sel is initialized before using it
        if not hasattr(self, 'sel') or self.sel is None:
            self.sel = selectors.DefaultSelector()  # Reinitialize if necessary

        addr = (host, port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)

        # Check if selector is closed
        try:
            self.sel.get_map()  # Attempt to call get_map to verify that the selector is not closed
        except Exception as e:
            print(f"Error accessing self.sel.get_map(): {e}")
            print("Reinitializing self.sel to prevent further issues.")
            self.sel = selectors.DefaultSelector()  # Reinitialize if it's invalid or closed

        # Close any existing connections before establishing a new one
        for key in list(self.sel.get_map().values()):  # Ensure a list here, to avoid modifying while iterating
            if key.fileobj != sock:
                print(f"Closing and unregistering socket: {key.fileobj}")
                key.fileobj.close()  # Close old socket
                self.sel.unregister(key.fileobj)  # Unregister old socket

        # Attempt to connect
        try:
            sock.connect_ex(addr)
        except Exception as e:
            print(f"Failed to connect: {e}")

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = libclient.Message(self.sel, sock, addr, request)
        self.sel.register(sock, events, data=message)

    def establish_connection(self, action, value):  
        #host = "192.168.178.36"
        host = "itwalter.de"
        port = 3580

        #session_id = libclient.session_id
        
        session_id = "REQUESTED"
   
        if(host == "itwalter.de"):
            res = socket.getaddrinfo("itwalter.de", 3580)
            for addr in res:
                host = addr[4][0]
                
        request = self._create_request(self, action, value, session_id)
        self._start_connection(self, host, port, request)
        
        try:
            while True:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        result = message.process_events(mask)
                    except Exception:
                        message.close()
                if not self.sel.get_map():
                    break
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            print(f"Closing selector: {self.sel}")
            # Avoid closing selector immediately here, instead call it when the application is done
            # self.sel.close()  
            return result
