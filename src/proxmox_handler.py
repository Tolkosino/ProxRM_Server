import requests
import urllib3

urllib3.disable_warnings()

nodename = "pve"
proxmoxhost = "192.168.178.224"
token_id = "root@pam!anotherOne"
token_secret = "63cf9982-50e7-4127-93f7-73c4b7789cd6"

def proxmox_connect():    

    headers = { "Authorization": "PVEAPIToken="+token_id+"="+token_secret}
    baseuri = "https://" + proxmoxhost + ":8006/api2/json/version"
    
    try:
        APIresponse = requests.get(baseuri, headers=headers, verify=False)
        # Checking if the API request was successful
        if APIresponse.status_code == 200:
            versioninfo = APIresponse.json()
            return headers
        else:
            #print(f"API request failed with status code {APIresponse.status_code}")
            return "FAILED:", "APIresponse.status_code"
    except:
        pass
    


def get_all_vms(headers):
    baseuri = "https://" + proxmoxhost + ":8006/api2/json/cluster/resources?type=vm"
    result = ""
    try:
        result = requests.get(baseuri, headers=headers, verify=False).json()
    except:
        print( "Error: API Request Failed")
        exit(1)
    vms = {}
    data = result['data']
    for vm in data:
        if("tags" in vm):
            vms[vm['vmid']] = {"name": vm['name'], "tags": vm['tags']}
        else:
            vms[vm['vmid']] = {"name":vm['name']}
            
    return vms
    
    

def get_vmStatus(headers, vmid):
    baseuri = "https://" + proxmoxhost + ":8006/api2/json/nodes/" + nodename + "/qemu/" + vmid + "/status/current"
    try:
        APIresponse2 = requests.get(baseuri, headers=headers, verify=False)
    except:
        print( "Error: API Request Failed")
        exit(1)

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
        return f"API request failed with status code {APIresponse2.status_code}"
       
def send_wolPackage():
    #send_magic_packet("6C:AE:8B:36:5F:A6")
    return "Wecker klingelt beim Server"

def set_hostAction(action, headers):
    if action == "start":
       send_wolPackage() 
    if action == "stop":
        body = {
                "command": "shutdown", 
                "node": "pve"
                }
        baseuri = "https://" + proxmoxhost + ":8006/api2/json/nodes/pve/status"
        try:
            APIresponse3 = requests.post(baseuri, headers=headers, verify=False, json=body)
        except:
            print( "Error: API Request Failed")
            exit(1)
        
        if APIresponse3.status_code == 200:
            runstateinfo = APIresponse3.json()
            runstate = runstateinfo['data']
            #print(runstate)
            return "Host Shutdown sent."
        else:
            print(f"API request failed with status code {APIresponse3.status_code}")
            pass

def set_vmAction(action, vmid, headers):
    vmstatus = get_vmStatus(headers, vmid)[0]
    
    if vmstatus != "running" and action == "start":
        if vmstatus == "paused":
            baseuri = "https://" + proxmoxhost + ":8006/api2/json/nodes/" + nodename + "/qemu/" + vmid + "/status/resume"
        elif vmstatus == "stopped":
            baseuri = "https://" + proxmoxhost + ":8006/api2/json/nodes/" + nodename + "/qemu/" + vmid + "/status/start"
        else:
            return( "VM not detected as running but not in paused or stopped state - no action taken.")
            
        try:
            APIresponse3 = requests.post(baseuri, headers=headers, verify=False)
        except:
            return "Error: API Request Failed"
        
        if APIresponse3.status_code == 200:
            runstateinfo = APIresponse3.json()
            runstate = runstateinfo['data']
        else:
            print(f"API request failed with status code {APIresponse3.status_code}")
            pass
    elif vmstatus == "running" and action == "stop":
        baseuri = "https://" + proxmoxhost + ":8006/api2/json/nodes/" + nodename + "/qemu/" + vmid + "/status/stop"
        
        try:
            APIresponse3 = requests.post(baseuri, headers=headers, verify=False)
        except:
            print( "Error: API Request Failed")
            exit(1)
            
        if APIresponse3.status_code == 200:
            runstateinfo = APIresponse3.json()
            runstate = runstateinfo['data']
            print(runstate)
        else:
            print(f"API request failed with status code {APIresponse3.status_code}")
    else:
        print( "Server sollte starten, läuft aber bereits. Keine Aktion ausgeführt.")