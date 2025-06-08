import requests
nodename = "pve"
prox_host =  "192.168.178.224"
prox_token = "root@pam!anotherotherone"
prox_secret = "238c1131-ceb6-4bc6-9f90-1e558cf6cdb4"

headers = {
    "Authorization": f"PVEAPIToken={prox_token}={prox_secret}"
}

url = f"https://{prox_host}:8006/api2/json/nodes/pve/version"
response = requests.get(url, headers=headers, verify=False)
response.raise_for_status()
print(response.json()["data"]["version"])