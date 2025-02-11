import pymysql
import proxmox_handler

DB_HOST="funnywol_db"
DB_USER="root"
DB_PASSWORD="Start123#"
DATABASE="wolserver"

''' 
-----------
Machine handling
---------
'''
def check_and_delete_deleted_vms(current_existent_vms):
#Checks if local DB has any DBs that aren't presen in pve anymore and removes them
    dbconn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE,
        autocommit=True
    )
    db_cursor = dbconn.cursor()
    db_cursor.execute("SELECT id FROM wol_machines")
    result = db_cursor.fetchall()
    for db_entry in result:
        if(db_entry[0] not in current_existent_vms):
            delete_vm(str(db_entry[0]),)

def delete_vm(vm_id):
    #Delete vm by id in local DB
    dbconn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE,
        autocommit=True
    )
    db_cursor = dbconn.cursor()
    sql = "DELETE FROM wol_machines WHERE id = %s"
    db_cursor.execute(sql, vm_id)
    dbconn.commit()
    print("Deleted machine from db - ", vm_id)
    
def get_vms():
    #Get all vms from pve
    headers = proxmox_handler.proxmox_connect()
    vms = proxmox_handler.get_all_vms(headers)
    return vms

def add_vm(vm, name, tags):
    #Add vm to local db
    dbconn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE,
        autocommit=True
    )
    db_cursor = dbconn.cursor()
    sql = "INSERT INTO wol_machines (id, name, tags) VALUES (%s, %s, %s)"
    val = (vm, name, tags)
    db_cursor.execute(sql, val)
    dbconn.commit()
    print("Added machine to db", val)
    
def update_vm(vm_name, vm_tags, vm_id):
    #Update vm in local db by id
    dbconn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE,
        autocommit=True
    )
    db_cursor = dbconn.cursor()
    sql = "UPDATE wol_machines SET name = %s, tags = %s WHERE id = %s"
    db_cursor.execute(sql, (vm_name, vm_tags, vm_id))
    dbconn.commit()
    print("Updated machine - ", vm_id)

def check_latest_vm_definitions():
    #main control function to update local vm db | Starts the whole process of checking for new/old vms etc.
    dbconn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE,
        autocommit=True
    )
    db_cursor = dbconn.cursor()
    current_existent_vms = []
    vms = get_vms()
    
    # vm = vm-ID as key in dict is vmid and 'vm' is key
    for vm in vms:
        sql = "SELECT * FROM wol_machines WHERE id = %s "
        val = (vm,)
        db_cursor.execute(sql, val)
        res = db_cursor.fetchall()
        if(not len(res) == 0):
            if("tags" in vms[vm]):
                update_vm(vms[vm]['name'], vms[vm]['tags'], vm)
            else:
                update_vm(vms[vm]['name'], "", vm)                        
        else:   
            if("tags" in vms[vm]):
                add_vm(vm, vms[vm]['name'], vms[vm]["tags"])
            else:
                add_vm(vm, vms[vm]['name'], "")
            
        current_existent_vms.append(int(vm))
    check_and_delete_deleted_vms(current_existent_vms)