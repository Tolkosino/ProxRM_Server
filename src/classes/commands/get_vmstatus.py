from classess.commands.commandBase import CommandBase

class get_vmstatus(CommandBase):
    
    def execute(self, **kwargs):
        import requests
        vmid = kwargs.get("vmid")

        """Retrieve the status of a specific VM."""
        url = f"https://{self.prox_host}:8006/api2/json/nodes/{self.nodename}/qemu/{vmid}/status/current"

        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            data = response.json().get('data', {})
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
            return status
        
        except requests.RequestException as e:
            self.logger.warning(f"Failed to fetch VM status for {vmid}: {e}")
            return None