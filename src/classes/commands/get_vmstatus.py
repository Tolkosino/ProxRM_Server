from classes.commands.commandBase import CommandBase

class get_vmstatus(CommandBase):
    
    def execute(self, **kwargs):
        import requests
        vmid = kwargs.get("vmid")

        self.logger.debug(f"get_vmstatus kwargs be like: ")
        for i, v in kwargs.items():
            self.logger.debug(f"{i} with value {v} ")

        """Retrieve the status of a specific VM."""
        url = f"https://{self.prox_host}:8006/api2/json/nodes/{self.nodename}/qemu/{vmid}/status/current"

        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            data = response.json().get('data', {})
            self.logger.debug(f"imagine, data pulled from vm be like: ")
            for i, v in data.items():
                self.logger.debug(f"{i} with value {v} ")
    
            status = {
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

            self.logger.debug(f"returning: {status} ")

            return status
        
        except requests.RequestException as e:
            self.logger.warning(f"Failed to fetch VM status for {vmid}: {e}")
            return None