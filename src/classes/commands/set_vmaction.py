from classes.commands.commandBase import CommandBase

class set_vmaction(CommandBase):

    def execute(self, **kwargs):
        import requests
        vmid = kwargs.get("vmid")
        action = kwargs.get("action")

        optional_start = ["force_cpu","machine","migratedfrom","migration_network","migration_type","skiplock","stateuri","targetstorage","timeout"]
        optional_reboot = ["timeout"]
        optional_reset = ["skiplock"]
        optional_resume = ["nocheck","skiplock"]
        optional_shutdown = ["forceStop","keepActive","skiplock","timeout"]
        optional_stop = ["keepActive","migratedfrom","overrule-shutdown","skiplock","timeout"]
        optional_suspend = ["skiplock","statestorage","todisk"]


        """Start or stop a VM."""
        if vmid:
            vm_status = self.get_status(vmid)

        if not vm_status:
            return f"Failed to retrieve VM {vmid} status."

        base_uri = f"https://{self.prox_host}:8006/api2/json/nodes/{self.nodename}/qemu/{vmid}/status"

        match(action):
            case "start":
                if vm_status["status"] == "running":
                    self.logger.debug(f"VM {vmid} is already running. No action taken.")
                    return "VM is already running."
                endpoint = "/start"
                url = base_uri + endpoint
                body = {}
                for arg in optional_start:
                    if kwargs.get(arg):
                        body[arg] = arg

            case "resume":
                if vm_status["status"] != "paused":
                    self.logger.debug(f"VM {vmid} is not paused. No action taken.")
                    return "VM is not paused."
                endpoint = "/resume"
                url = base_uri + endpoint
                body = {}
                for arg in optional_resume:
                    if kwargs.get(arg):
                        body[arg] = arg

            case "stop":
                if vm_status["status"] != "running":
                    self.logger.debug(f"VM {vmid} is not running. No action taken.")
                    return "VM is not running."
                url = base_uri + "/stop"
                body = {}
                for arg in optional_stop:
                    if kwargs.get(arg):
                        body[arg] = arg

            case "reboot":
                if vm_status["status"] == "running":
                    endpoint = "/reboot"
                else:
                    return "VM is not running, can't restart."
                url = base_uri + endpoint
                body = {}
                for arg in optional_reboot:
                    if kwargs.get(arg):
                        body[arg] = arg

            case "reset":
                if vm_status["status"] == "running":
                    endpoint = "/reset"
                else:
                    return "VM is not running, can't reset."
                url = base_uri + endpoint  
                body = {}
                for arg in optional_reboot:
                    if kwargs.get(arg):
                        body[arg] = arg

            case "suspend":
                if vm_status["status"] == "running":
                    endpoint = "/suspend"
                else:
                    return "VM is not running, can't suspend."
                url = base_uri + endpoint  
                body = {}
                for arg in optional_suspend:
                    if kwargs.get(arg):
                        body[arg] = arg
            
            case "shutdown":
                if vm_status["status"] == "running":
                    endpoint = "/shutdown"
                else:
                    return "VM is not running, can't shutdown."
                body = {}
                for arg in optional_shutdown:
                    if kwargs.get(arg):
                        body[arg] = arg

            case _:
                return "Invalid action specified."

        try:
            if not body == {}:
                response = requests.post(url, headers=self.headers, verify=False, json=body)
            else:
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