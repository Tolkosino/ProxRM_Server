from classes.commands.commandBase import CommandBase

class set_vmaction(CommandBase):

    def execute(self, **kwargs):
        import requests
        vmid = kwargs.get("vmid")
        action = kwargs.get("action")

        """Start or stop a VM."""
        if not vmid:
            return "Enter a valid vmid"
        
        vm_status = self.get_status(vmid)
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
        

    def get_status(self, vmid):
        import requests

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
                "uptime": data.get("uptime")
            }
        
        except requests.RequestException as e:
            self.logger.warning(f"Failed to fetch VM status for {vmid}: {e}")
            return None