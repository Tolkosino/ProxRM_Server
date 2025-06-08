import requests

headers = {"Authorization": "PVEAPIToken=root@pam!anotherotherone=238c1131-ceb6-4bc6-9f90-1e558cf6cdb4"}
url = "https://192.168.178.224:8006/api2/json/cluster/resources?type=vm"

response = requests.get(url, headers=headers, verify=False)
vms = {}

for vm in response.json().get('data', []):
    vms[vm['vmid']] = {"name": vm['name'], "tags": vm.get('tags', [])}

for vmid, details in vms.items():
    vm_name = details.get("name", "")
    vm_tags = details.get("tags", "")
    print(vmid)
    print(vm_name)
    print(vm_tags)
