from helper import DatabaseConnection
from config import Config
from facades import ProxFacade
import logging


class DB_Machine():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conf = Config()
        self.conf_database = self.conf.get_database()
        self.DATABASE_INFO = [self.conf_database["DB_HOST"],
                              self.conf_database["DB_USER"],
                              self.conf_database["DB_PASSWORD"],
                              self.conf_database["DB_DATABASE"]
                             ]
        
    def _remove_deleted_vms(self, prox_existent_vms):
        """Compares VMs in proxmox with VMs existent in local DB, deletes the delta from local DB."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute("SELECT id FRON wol_machines")
            local_existent_vms = cursor.fetchall()[0]
            delta_to_delete_vms = list(filter(lambda vm: vm not in prox_existent_vms, local_existent_vms))
            for vmid in delta_to_delete_vms: 
                self.local_delete_vm(vmid)
            else:
                self.logger.warning(f"Local existing VM couldn't be deleted from db. {vmid}")

    def local_delete_vm(self, vmid):
        """Delete VM by id in local DB"""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            sql = "DELETE FROM wol_machines WHERE id = %s"
            cursor.execute(sql, vmid)
            self.logger.info(f"Deleted machine from db. (ID {vmid})")

    def local_update_vm(self, vm_name, vm_tags, vmid):
        """Update vm in local db by id"""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            sql = "UPDATE wol_machines SET name = %s, tags = %s WHERE id = %s"
            cursor.execute(sql, (vm_name, vm_tags, vmid))
            self.logger.info(f"Updated machine. (ID {vmid}) ")

    def local_add_vm(self, vm, name, tags):
        """Add VM to local db"""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            sql = "INSERT INTO wol_machines (id, name, tags) VALUES (%s, %s, %s)"
            val = (vm, name, tags)
            cursor.execute(sql, val)
            self.logger.info(f"Added machine to db. {val}")


    def _reload_local_database(self):
        """starts the whole process of checking for new/old vms"""
        self.logger.info("startet update of local vm db")
        proxFacade = ProxFacade()
        current_existent_vms = []
        vms = proxFacade.get_vms()

        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            #vm is vmID. Key in the dictionary is also vmID, therefore vm is used as key.
            for vm in vms:
                sql = "SELECT * FROM wol_machines WHERE id = %s"
                val = (vm,)
                cursor.execute(sql, val)
                res = cursor.fetchall()
                if(not len(res) == 0):
                    if("tags" in vms[vm]):
                        self.local_update_vm(vms[vm]['name'], vms[vm]['tags'], vm)
                    else:
                        self.local_update_vm(vms[vm]['name'], "", vm)                        
                else:   
                    if("tags" in vms[vm]):
                        self.local_add_vm(vm, vms[vm]['name'], vms[vm]["tags"])
                    else:
                        self.local_add_vm(vm, vms[vm]['name'], "")   
                current_existent_vms.append(int(vm))

            self._remove_deleted_vms(current_existent_vms)