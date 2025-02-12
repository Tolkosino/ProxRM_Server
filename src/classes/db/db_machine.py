from config import Config

import facades.proxFacade as proxFacade
import pymysql
import logging
import time

class DB_Machine():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conf = Config()
        self.conf_database = self.conf.get_database()
        self.HOST = self.conf_database["DB_HOST"]
        self.USER = self.conf_database["DB_USER"]
        self.PASSWORD = self.conf_database["DB_PASSWORD"]
        self.DATABASE = self.conf_database["DB_DATABASE"]

    def _connect_db(self):
        """ Create database connection."""
        for i in range(10):
            try:
                conn = pymysql.connect(
                    host=self.HOST,
                    user=self.USER,
                    password=self.PASSWORD,
                    database=self.DATABASE,
                    autocommit=True
                )
                return conn, conn.cursor()
            except pymysql.MySQLError as e:
                self.logger.warning(f"DB-Connection failed. ({i+1}/10). Error: {e}")
                time.sleep(5)
        self.logger.critical("Couldn't connect to Database!")
        raise Exception("Couldn't connect to Database!")

    def _remove_deleted_vms(self, current_existent_vms):
        #Checks if local DB has any DBs that aren't presen in pve anymore and removes them
        conn, cursor = self._connect_db()
        cursor.execute("SELECT id FROM wol_machines")
        result = cursor.fetchall()

        for db_entry in result:
            if(db_entry[0] not in current_existent_vms):
                _delete_vm(str(db_entry[0]),)

    def _delete_vm(self, vm_id):
        #Delete vm by id in local DB
        conn, cursor = self._connect_db()
        sql = "DELETE FROM wol_machines WHERE id = %s"
        cursor.execute(sql, vm_id)
        conn.commit()
        self.logger.info(f"Deleted machine from db. (ID {vm_id})")

    def _add_vm(self, vm, name, tags):
        #Add vm to local db
        conn, cursor = self._connect_db()
        sql = "INSERT INTO wol_machines (id, name, tags) VALUES (%s, %s, %s)"
        val = (vm, name, tags)
        cursor.execute(sql, val)
        conn.commit()
        self.logger.info(f"Added machine to db. {val}")
        
    def _update_vm(self, vm_name, vm_tags, vm_id):
        #Update vm in local db by id
        conn, cursor = self._connect_db()
        sql = "UPDATE wol_machines SET name = %s, tags = %s WHERE id = %s"
        cursor.execute(sql, (vm_name, vm_tags, vm_id))
        conn.commit()
        self.logger.info(f"Updated machine. (ID {vm_id}) ")

    def _reload_local_database(self):
        #main control function to update local vm db | Starts the whole process of checking for new/old vms etc.
        conn, cursor = self._connect_db()
        current_existent_vms = []
        vms = proxFacade.get_vms()
        
        # vm = vm-ID as key in dict is vmid and 'vm' is key
        for vm in vms:
            sql = "SELECT * FROM wol_machines WHERE id = %s "
            val = (vm,)
            cursor.execute(sql, val)
            res = cursor.fetchall()
            if(not len(res) == 0):
                if("tags" in vms[vm]):
                    self._update_vm(vms[vm]['name'], vms[vm]['tags'], vm)
                else:
                    self._update_vm(vms[vm]['name'], "", vm)                        
            else:   
                if("tags" in vms[vm]):
                    self._add_vm(vm, vms[vm]['name'], vms[vm]["tags"])
                else:
                    self._add_vm(vm, vms[vm]['name'], "")   
            current_existent_vms.append(int(vm))

        self._remove_deleted_vms(current_existent_vms)