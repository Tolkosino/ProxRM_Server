import requests
import urllib3
import logging
from config import Config

class prox():
    
    def __init__(self):
        urllib3.disable_warnings()
        self.logger = logging.getLogger(__name__)
        
        self.conf = Config()
        self.conf_proxmox = self.conf.get_proxmox()
        self.nodename = self.conf_proxmox["NODENAME"]
        self.prox_host = self.conf_proxmox["PROX_HOST"]
        self.prox_token = self.conf_proxmox["PROX_TOKEN"]
        self.prox_secret = self.conf_proxmox["PROX_SECRET"]

    def _proxmox_connect(self):    
        headers = { "Authorization": "PVEAPIToken="+self.prox_token+"="+self.prox_secret}
        baseuri = "https://" + self.prox_host + ":8006/api2/json/version"
        
        try:
            APIresponse = requests.get(baseuri, headers=headers, verify=False)
            
            if APIresponse.status_code == 200:
                versioninfo = APIresponse.json() # if there is an error in this case, the connection doesn't work
                return headers
            else:
                self.logger.critical(f"API request failed with status code {APIresponse.status_code}")
                return "FAILED:", APIresponse.status_code
        except:
            self.logger.critical(f"Couldn't extract default json header from API request. Request reported status Code: {APIresponse.status_code} ")
            raise RuntimeError(f"Couldn't extract default json header from API request. Request reported status Code: {APIresponse.status_code} ")

    def _get_all_vms(self, headers):
        baseuri = "https://" + self.prox_host + ":8006/api2/json/cluster/resources?type=vm"

        try:
            result = requests.get(baseuri, headers=headers, verify=False).json()
        except:
            self.logger.critical("API Request Failed while getting list of existent VMs")
            raise RuntimeError("API Request Failed while getting list of existent VMs")
        vms = {}
        data = result['data']

        for vm in data:
            if("tags" in vm):
                vms[vm['vmid']] = {"name": vm['name'], "tags": vm['tags']}
            else:
                vms[vm['vmid']] = {"name":vm['name']}                
        return vms
    
    def _get_vmStatus(self, headers, vmid):
        baseuri = "https://" + self.prox_host + ":8006/api2/json/nodes/" + self.nodename + "/qemu/" + vmid + "/status/current"
        try:
            APIresponse2 = requests.get(baseuri, headers=headers, verify=False)
        except:
            self.logger.critical("API Request Failed while getting status of VMs")
            raise RuntimeError("API Request Failed while getting status of VMs")

        if APIresponse2.status_code == 200:
            vmstatusinfo = APIresponse2.json()
            vmstatus = vmstatusinfo['data']['qmpstatus']
            maxmem = vmstatusinfo['data']['maxmem']
            maxdisk = vmstatusinfo['data']['maxdisk']
            netin = vmstatusinfo['data']['netin']
            netout = vmstatusinfo['data']['netout']
            diskwrite = vmstatusinfo['data']['diskwrite']
            diskread = vmstatusinfo['data']['diskread']
            cpus = vmstatusinfo['data']['cpus']
            uptime = vmstatusinfo['data']['uptime']
            
            maxdiskGB = maxdisk / 1000000000
            maxmemGB  = maxmem / 1000000000
            
            return vmstatus, maxmemGB, maxdiskGB, netin, netout, diskwrite, diskread, cpus, uptime
        else:
            self.logger.warning(f"API request failed while getting vm status with status code {APIresponse2.status_code}")
            return f"API request failed while getting vm status with status code {APIresponse2.status_code}"
       
    def _send_wolPackage(self):
        #send_magic_packet("6C:AE:8B:36:5F:A6")
        self.logger.info("Wecker klingelt beim Server")
        return "Wecker klingelt beim Server"

    def _set_hostAction(self, action, headers):
        if action == "start":
            self._send_wolPackage() 
        if action == "stop":
            body = {
                    "command": "shutdown", 
                    "node": "pve"
                    }
            baseuri = "https://" + self.prox_host + ":8006/api2/json/nodes/pve/status"
            try:
                APIresponse3 = requests.post(baseuri, headers=headers, verify=False, json=body)
            except:
                self.logger.critical("API Request Failed while shutdowning host-node")
                raise RuntimeError("API Request Failed while shutdowning host-node")
            
            if APIresponse3.status_code == 200:
                runstateinfo = APIresponse3.json()
                runstate = runstateinfo['data']
                self.logger.debug(f"Host shutdown sent. Current runstate: {runstate}")
                return "Host Shutdown sent."
            else:
                self.logger.warning(f"API request failed while shutdowning host-node with status code {APIresponse3.status_code}")
                return f"API request failed while shutdowning host-node with status code {APIresponse3.status_code}"

    def _set_vmAction(self, action, vmid, headers):
        vmstatus = self._get_vmStatus(headers, vmid)[0]
        
        if vmstatus != "running" and action == "start":
            if vmstatus == "paused":
                baseuri = "https://" + self.prox_host + ":8006/api2/json/nodes/" + self.nodename + "/qemu/" + vmid + "/status/resume"
            elif vmstatus == "stopped":
                baseuri = "https://" + self.prox_host + ":8006/api2/json/nodes/" + self.prox_secret + "/qemu/" + vmid + "/status/start"
            else:
                self.logger.debug("VM not detected as running but not in paused or stopped state - no action taken.")
                return("VM not detected as running but not in paused or stopped state - no action taken.")
                
            try:
                APIresponse3 = requests.post(baseuri, headers=headers, verify=False)
            except:
                self.logger.warning("API Request Failed while handling recieved action")
                return "Error: API Request Failed"
            
            if APIresponse3.status_code == 200:
                runstateinfo = APIresponse3.json()
                runstate = runstateinfo['data']
            else:
                self.logger.warning(f"API request failed while handling recieved action with status code {APIresponse3.status_code}")
                return f"API request failed while handling recieved action with status code {APIresponse3.status_code}"
            
        elif vmstatus == "running" and action == "stop":
            baseuri = "https://" + self.prox_host + ":8006/api2/json/nodes/" + self.prox_secret + "/qemu/" + vmid + "/status/stop"
            
            try:
                APIresponse3 = requests.post(baseuri, headers=headers, verify=False)
            except:
                self.logger.critical(f"API Request Failed while shutdowning vm (ID {vmid})")
                raise RuntimeError(f"API Request Failed while shutdowning vm (ID {vmid})")
                
            if APIresponse3.status_code == 200:
                runstateinfo = APIresponse3.json()
                runstate = runstateinfo['data']
                print(runstate)
            else:
                self.logger.warning(f"API request failed while shutdowning vm (ID {vmid}) with status code {APIresponse3.status_code}")
                return f"API request failed while shutdowning vm (ID {vmid}) with status code {APIresponse3.status_code}"
        else:
            self.logger.debug("Server should start but is already runnning. No action taken")
            print("Server should start but is already runnning. No action taken")