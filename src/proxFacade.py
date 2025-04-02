from classess.prox.proxmox import Proxmox
from classess.db.user import DB_User
import logging
import uuid

class ProxFacade:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.proxmox = Proxmox()
        pass
    
    def executeAction(self, cmd_set):
        command = cmd_set.get('command') # login 
        action = cmd_set.get('action') # start|stop
        vmid = cmd_set.get('vmid') # 102
        session_id = cmd_set.get('session_id') # 6546516-asd858746sd-12316tsdf
        
        match command:                                     
            case "get_VMList":                          ##Should be smth like "get_VMList;[session_id]"
                res = self.get_VMsForUser(session_id) 
            case "get_VMStatus":                        ##Should be smth like "get_VMStatus;[session_id]"
                res = self.get_vmStatus(vmid, session_id)
            case "set_VMAction":                        ##Should be smth like "set_VMAction;start;[session_id]" or "set_VMAction;stop;[session_id]"
                res = self.set_vmAction(action, vmid, session_id)
            case "login":                           ##Should be smth like "[username];[password]"
                res = self.authenticate_user(action, vmid)     #action, vmid translates to username password
            case "logout":
                res = self.logout_user(session_id)
            case "create_vm":
                res = "not imblemended iet"
                pass
                #self.create_vm(cmd_set)
            case _: #default case if no match
                self.logger.warning(f"Unsupported value in vm task-selection! {command} - recieved")
                res = "Unsupported value in vm task-selection!"
        return res

    def create_vm(cmd_set):
        pass

    def logout_user(self, session_id):
        return DB_User().logout_user(session_id)

    def set_vmAction(self, action, vmID, session_id):
        userId = DB_User().get_user_id_by_session_id(session_id)
        if userId and DB_User().check_permissions(userId, vmID):
            if vmID == "pve":
                return self.proxmox.set_host_action(action)
            return self.proxmox.set_vm_action(action, vmID)
        elif session_id == "REQUESTED":
            return "Access Denied but Session id Requested"
        else:
            self.logger.info("Wrong credentials recieved. Access denied.")
            return "Access Denied"
            
    def get_vmStatus(self, vmID, session_id):        
        userId = DB_User().get_user_id_by_session_id()
        if userId and DB_User().check_permissions(userId, vmID):
            response = self.proxmox.get_vmStatus(vmID)
            res = ' '
            self.logger.debug(f"getStatus response be like {response}")
            res = res.join(str(response))
            return res
        elif session_id == "REQUESTED":
            return "Access Denied but Session id Requested"
        else:
            self.logger.info("Access denied.")
            return "Access Denied"
        
    def authenticate_user(self, username, password):
        session_id = DB_User().login_user(username, password)

        if not session_id == "WRONG PASSWORD":
            self.logger.debug(f"{username} authenticated.")
            return f"authn_{username}_accept;{session_id}" ##User authenticated
        else:
            self.logger.debug(f"{username} provided wrong password.")
            return f"authn_{password}_deny" ##Login denied
        
    def get_VMsForUser(self, session_id):
        user_id = DB_User().get_user_id_by_session_id(session_id)
        vms = DB_User().get_vms_for_perms_of_user(user_id)
        return ";".join(str(x) for x in vms)
    def get_vms(self):
        return Proxmox().get_all_vms()
