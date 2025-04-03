import logging
import tomli

class Config():
    def __init__(self):
         self._load()

    def _load(self):
        with open("config.toml", mode="rb") as fp:
            self.config = tomli.load(fp)
            self._set_logLevel()
        
    def _set_logLevel(self):
        match self.config["logging"]["LOGLEVEL"]:
            case "INFO":
                self.config["logging"]["LOGLEVEL"] = logging.INFO
            case "DEBUG":
                self.config["logging"]["LOGLEVEL"] = logging.DEBUG
            case "WARNING":
                self.config["logging"]["LOGLEVEL"] = logging.WARNING
            case "CRITICAL":
                self.config["logging"]["LOGLEVEL"] = logging.CRITICAL
            case _:
                self.config["logging"]["LOGLEVEL"] = logging.INFO

    def get_database(self):
        return self.config["database"]
    
    def get_proxmox(self):
        return self.config["proxmox"]
    
    def get_proxrm_server(self):
            return self.config["proxrm_server"]
        
    def get_logging(self):
            return self.config["logging"]
    
    def load(self):
        return self._load() 