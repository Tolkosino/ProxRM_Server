from abc import ABC, abstractmethod

#Base class all plugins must implement to force consistent behaviour. Ignore for everything other than plugin development.
#If a plugin is not inheriting from BaseEvent an Error will be produced.

@abstractmethod
class CommandBase:

    def __init__(self):
        from classes.config.config import Config
        import urllib3
        import logging
        
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

    # Abstract method that must be implemented by subclasses.
    # This is meant to be overridden by plugin-specific logic to send messages.
    # If not implemented in the subclass, a NotImplementedError will be raised.

    def execute(self, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")
