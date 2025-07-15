from classes.commands.commandBase import CommandBase

class set_hostaction(CommandBase):

    def execute(self, **kwargs):
        from classes.db.user import DB_User
        import requests

        action = kwargs.get("action")
        session_id = kwargs.get("session_id")
        username =  DB_User().get_user_id_by_session_id(session_id)

        """Start or stop the Proxmox host."""
        if action == "start":
            return self._send_wol_package()
        elif action == "stop":
            url = f"https://{self.prox_host}:8006/api2/json/nodes/pve/status"
            body = {"command": "shutdown", "node": "pve"}

            try:
                response = requests.post(url, headers=self.headers, verify=False, json=body)
                response.raise_for_status()
                self.logger.info(f"{username} - Host shutdown command sent.")
                return "Host shutdown command sent."
            except requests.RequestException as e:
                self.logger.critical(f"Failed to shutdown host: {e}")
                raise RuntimeError(f"Failed to shutdown host: {e}")
            
    def _send_wol_package(self):
        from wakeonlan import send_magic_packet

        send_magic_packet(self.prox_mac_address)
        self.logger.info("Wake-on-LAN signal sent to server.")
        return "Wake-on-LAN signal sent to server."