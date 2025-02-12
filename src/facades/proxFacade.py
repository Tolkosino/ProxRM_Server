from classes.prox import proxmox

class ProxFacade:
    
    def __init__(self):
        pass
    
    def executeAction(self, task, value, session_id):
        original_task = task
        task = task.split(";")[0]
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
                self.logger.warning(f"Unsupported value in vm task-selection!")
                res = "Unsupported value in vm task-selection!"
        return res
    

    def get_connection(self):
        session, apiheaders = proxmox.proxmox_connect()
        if session == "FAILED:":
            proxmox.send_wolPackage()
        else:
            return session, apiheaders
    
    def set_vmAction(self, action, value, session_id):
        vmID = value
        
        if db_userHandler.check_session_id(session_id, ""):
            session, apiheaders = self.get_connection()
            if vmID == "pve":
                return proxmox.set_hostAction(action, session, apiheaders)
            return proxmox.set_vmAction(action, vmID ,session, apiheaders)
        elif session_id == "REQUESTED":
            return "Access Denied but Session id Requested"
        else:
            self.logger.info("Wrong credentials recieved. Access denied.")
            return "Access Denied"
            
            
    def get_vmStatus(self, value, session_id):
        vmID = value
        
        if db_userHandler.check_session_id(session_id):
            session, apiheaders = self.get_connection()
            response = proxmox.get_vmStatus(session, apiheaders, vmID)
            res = ' '
            self.logger.debug(f"getStatus response be like {response}")
            res = res.join(str(response))
            return res
        elif session_id == "REQUESTED":
            return "Access Denied but Session id Requested"
        else:
            self.logger.info("Wrong credentials recieved. Access denied.")
            return "Access Denied"
        
    def authenticate_user(self, param):
        username = param.split(";")[0]
        password = param.split(";")[1]
                
        if not db_userHandler.auth_user(username, password) == False:
            session_key = uuid5()
            self.logger.debug(f"{username} authenticated.")
            return f"authn_{username}_accept;{session_key}" ##User authenticated
        else:
            self.logger.debug(f"{username} provided wrong password.")
            return f"authn_{password}_deny" ##Login denied
        
    def get_VMsForUser(self, value, session_id):
        vms = db_userHandler.get_vms_for_user_permission(session_id)
        return ";".join(vms)