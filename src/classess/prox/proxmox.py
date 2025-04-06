import requests
import urllib3
import logging
from classess.config.config import Config
from wakeonlan import send_magic_packet

class Proxmox:
    
    def __init__(self):
        urllib3.disable_warnings()
        self.logger = logging.getLogger(__name__)
        
        self.conf = Config()
        self.conf_proxmox = self.conf.get_proxmox()
        self.nodename = self.conf_proxmox["NODENAME"]
        self.prox_host = self.conf_proxmox["PROX_HOST"]
        self.prox_token = self.conf_proxmox["PROX_TOKEN"]
        self.prox_secret = self.conf_proxmox["PROX_SECRET"]
        self.prox_mac_address = self.conf_proxmox["MAC"]
        self.headers = {
            "Authorization": f"PVEAPIToken={self.prox_token}={self.prox_secret}"
        }

    def get_all_vms(self):
        """Retrieve all VMs from the cluster."""
        url = f"https://{self.prox_host}:8006/api2/json/cluster/resources?type=vm"

        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            vms = {}
            for vm in response.json().get('data', []):
                vms[vm['vmid']] = {"name": vm['name'], "tags": vm.get('tags', [])}
            return vms
        except requests.RequestException as e:
            self.logger.critical(f"Failed to fetch VMs: {e}")
            raise RuntimeError(f"Failed to fetch VMs: {e}")

    def get_vm_status(self, vmid):
        """Retrieve the status of a specific VM."""
        url = f"https://{self.prox_host}:8006/api2/json/nodes/{self.nodename}/qemu/{vmid}/status/current"

        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            data = response.json().get('data', {})

            return {
                "status": data.get("qmpstatus"),
                "maxmem_GB": data.get("maxmem", 0) / 1e9,
                "maxdisk_GB": data.get("maxdisk", 0) / 1e9,
                "netin": data.get("netin"),
                "netout": data.get("netout"),
                "diskwrite": data.get("diskwrite"),
                "diskread": data.get("diskread"),
                "cpus": data.get("cpus"),
                "uptime": data.get("uptime"),
            }
        except requests.RequestException as e:
            self.logger.warning(f"Failed to fetch VM status for {vmid}: {e}")
            return None

    def _send_wol_package(self):
        """Simulate Wake-on-LAN."""
        send_magic_packet(self.prox_mac_address)
        self.logger.info("Wake-on-LAN signal sent to server.")
        return "Wake-on-LAN signal sent to server."

    def set_host_action(self, action):
        """Start or stop the Proxmox host."""
        if action == "start":
            return self._send_wol_package()
        elif action == "stop":
            url = f"https://{self.prox_host}:8006/api2/json/nodes/pve/status"
            body = {"command": "shutdown", "node": "pve"}

            try:
                response = requests.post(url, headers=self.headers, verify=False, json=body)
                response.raise_for_status()
                return "Host shutdown command sent."
            except requests.RequestException as e:
                self.logger.critical(f"Failed to shutdown host: {e}")
                raise RuntimeError(f"Failed to shutdown host: {e}")

    def set_vm_action(self, action, vmid):
        """Start or stop a VM."""
        if not vmid:
            return "Enter a valid vmid"
        
        vm_status = self.get_vm_status(vmid)
        if not vm_status:
            return f"Failed to retrieve VM {vmid} status."

        base_uri = f"https://{self.prox_host}:8006/api2/json/nodes/{self.nodename}/qemu/{vmid}/status"

        match(action):
            
            case "start":
                if vm_status["status"] == "running":
                    self.logger.debug(f"VM {vmid} is already running. No action taken.")
                    return "VM is already running."

                endpoint = "/resume" if vm_status["status"] == "paused" else "/start"
                url = base_uri + endpoint
            
            case "stop":
                if vm_status["status"] != "running":
                    self.logger.debug(f"VM {vmid} is not running. No action taken.")
                    return "VM is not running."

                url = base_uri + "/stop"

            case _:
                return "Invalid action specified."

        try:
            response = requests.post(url, headers=self.headers, verify=False)
            response.raise_for_status()
            return f"VM {vmid} {action} command sent."
        except requests.RequestException as e:
            self.logger.warning(f"Failed to {action} VM {vmid}: {e}")
            return f"Failed to {action} VM {vmid}."