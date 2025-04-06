from classess.commands import commandBase

class get_allvms(commandBase):
    
    def execute(self, **kwargs):
        import requests
        
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