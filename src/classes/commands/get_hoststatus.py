from classes.commands.commandBase import CommandBase

class get_hoststatus(CommandBase):

    def execute(self, **kwargs):
        import requests
        action = kwargs.get("action")
        
        """Start or stop the Proxmox host."""

        url = f"https://{self.prox_host}:8006/api2/json/nodes/pve/version"

        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            if not response.json()["data"]["version"] == "":
                return "running"
            else:
                return "stopped"
        except requests.RequestException as e:
            self.logger.warning(f"Failed to get host status, i guess its offline then?: {e}")
            return "stopped"
            