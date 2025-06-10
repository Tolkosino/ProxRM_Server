from classes.db.user import DB_User
from classes.loader.command_factory import CommandFactory
import logging


class ProxFacade:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def executeAction(self, cmd_set):
        command = cmd_set.get('command') # login 
        action = cmd_set.get('action') # start|stop
        vmid = cmd_set.get('vmid') # 102
        session_id = cmd_set.get('session_id') # 6546516-asd858746sd-12316tsdf
        res = None
        command = command.lower()
        
        if command not in ["login","logout"]:
            userId = DB_User().get_user_id_by_session_id(session_id)
            
            self.logger.debug(CommandFactory.get_commands())

            if userId and DB_User().check_permissions(userId, vmid) and command in CommandFactory.get_commands():
                self.logger.debug(f"{userId} has permissions")
                command = CommandFactory.create_command(command)
                res = command.execute(vmid=vmid, action=action, session_id=session_id)
            elif userId and command in ["get_hoststatus","get_vmlist"]:
                command = CommandFactory.create_command(command)
                res = command.execute(vmid=vmid, action=action, session_id=session_id)
            else:
                return "Access Denied"
            
        elif command in CommandFactory.get_commands() and command in ["login","logout"]:
                self.logger.debug("This is in correct if for login")
                command = CommandFactory.create_command(command)
                res = command.execute(vmid=vmid, action=action, session_id=session_id)
        self.logger.debug(f"this is res {res}")
        return "FAILURE IN COMMAND EXECUTION" if res is None else res
    
    def get_all_vms(self):
        """Retrieve all VMs from the cluster."""
        from classes.config.config import Config
        import requests

        conf = Config()
        conf_proxmox = conf.get_proxmox()
        prox_token = conf_proxmox["PROX_TOKEN"]
        prox_secret = conf_proxmox["PROX_SECRET"]
        prox_host = conf_proxmox["PROX_HOST"]
        headers = {
            "Authorization": f"PVEAPIToken={prox_token}={prox_secret}"
        }
    
        url = f"https://{prox_host}:8006/api2/json/cluster/resources?type=vm"

        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            vms = {}

            for vm in response.json().get('data', []):
                vms[vm['vmid']] = {"name": vm['name'], "tags": vm.get('tags', [])}

            return vms

        except requests.RequestException as e:
            self.logger.critical(f"Failed to fetch VMs: {e}")
            raise RuntimeError(f"Failed to fetch VMs: {e}")
        

    def get_all_nodes(self):
        """Retrieve all VMs from the cluster."""
        from classes.config.config import Config
        import requests

        conf = Config()
        conf_proxmox = conf.get_proxmox()
        prox_token = conf_proxmox["PROX_TOKEN"]
        prox_secret = conf_proxmox["PROX_SECRET"]
        prox_host = conf_proxmox["PROX_HOST"]
        headers = {
            "Authorization": f"PVEAPIToken={prox_token}={prox_secret}"
        }
    
        url = f"https://{prox_host}:8006/api2/json/cluster/resources?type=node"

        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            nodes = []

            for node in response.json().get('data', []):
                nodes.append(node["node"])

            return nodes

        except requests.RequestException as e:
            self.logger.critical(f"Failed to fetch Nodes: {e}")
            raise RuntimeError(f"Failed to fetch Nodes: {e}")
        
