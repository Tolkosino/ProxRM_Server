from classes.db.helper import DatabaseConnection
from classes.config.config import Config
from proxFacade import ProxFacade
import logging

class DB_Machine:
    def __init__(self):
        """Initializes the database machine manager with configuration settings."""
        self.logger = logging.getLogger(__name__)
        self.conf = Config()
        self.conf_database = self.conf.get_database()
        self.DATABASE_INFO = (
            self.conf_database["DB_HOST"],
            self.conf_database["DB_USER"],
            self.conf_database["DB_PASSWORD"],
            self.conf_database["DB_DATABASE"],
            self.conf_database["DB_PORT"]
        )

    def _remove_deleted_vms(self, prox_existent_vms):
        """Removes VMs from the local database that no longer exist in Proxmox."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute("SELECT id FROM wol_machines")
            local_existent_vms = {row[0] for row in cursor.fetchall()}  # Use a set for fast lookups

        delta_to_delete_vms = local_existent_vms - set(prox_existent_vms)
        for vmid in delta_to_delete_vms:
            self.local_delete_vm(vmid)

    def local_delete_vm(self, vmid):
        """Deletes a VM by ID in the local database."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute("DELETE FROM wol_machines WHERE id = %s", (vmid,))
        self.logger.info(f"Deleted machine from DB (ID {vmid})")

    def local_update_vm(self, name, tags, vmid):
        """Updates VM information in the local database."""

        self.logger.debug(f"trying to update machine with following Infos provided - name: {name} - vm-id - {vmid} - tags - {tags}")
        if not tags: tags = ""
        
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute(
                "UPDATE wol_machines SET name = %s, tags = %s WHERE id = %s",
                (name, tags, vmid),
            )
        self.logger.info(f"Updated machine (ID {vmid})")

    def local_add_vm(self, vmid, name, tags):
        """Adds a new VM entry to the local database."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            self.logger.debug(f"trying to add machine with following Infos provided - name: {name} - vm-id - {vmid} - tags - {tags}")
            if not tags: tags = ""
            cursor.execute(
                "INSERT INTO wol_machines (id, name, tags) VALUES (%s, %s, %s)",
                (vmid, name, tags),
            )
        self.logger.info(f"Added machine to DB (ID {vmid})")

    def reload_local_database(self):
        """Synchronizes the local database with Proxmox VMs."""
        self.logger.info("Starting update of local VM database")
        machines = None
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute("SELECT id, tags, name FROM wol_machines")
            machines = cursor.fetchall()
        
        dict_machines = dict()
        current_existent_vms = set()
        self.logger.debug(f"VM-Set collected from Proxmox: {machines}")
        for machine in machines:
            dict_machines[machine[0]] = {"tags": machine[1], "name": machine[2]}

        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            for vm, details in dict_machines.items():
                cursor.execute("SELECT id FROM wol_machines WHERE id = %s", (vm,))
                exists = cursor.fetchone()

                vm_name = details.get("name", "")
                vm_tags = details.get("tags", "")

                if exists:
                    self.local_update_vm(vm_name, vm_tags, vm)
                else:
                    self.local_add_vm(vm, vm_name, vm_tags)

                current_existent_vms.add(vm)

        self._remove_deleted_vms(current_existent_vms)
