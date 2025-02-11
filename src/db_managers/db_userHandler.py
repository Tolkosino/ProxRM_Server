import hashlib
import pymysql
from uuid import uuid5

DB_HOST="funnywol_db",
DB_USER="root",
DB_PASSWORD="Start123#",
DATABASE="wolserver"

'''
 -----------
 User handling
 ---------
'''  
def hash_password(password):
    #hash password
    sha512 = hashlib.sha512()
    sha512.update(password)
    return sha512.hexdigest()

def create_user(username, cleantext_password, permissions):
    #Create new users
    dbconn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE
    )
    db_cursor = dbconn.cursor()
    hashed_password = hash_password(cleantext_password)
    sql = "INSERT INTO wol_users (username, password, permissions) VALUES (%s, %s, %s)"
    val = (username, hashed_password, permissions)
    db_cursor.execute(sql, val)
    dbconn.commit()
    print(f"Added user '{username}' with permissions on tags: {permissions}")

def delete_user(id):
    #Delete user by id
    dbconn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE
    )
    db_cursor = dbconn.cursor()    
    sql = "DELETE FROM wol_users WHERE id = %s"
    val = (id, )
    db_cursor.execute(sql, val)
    dbconn.commit()
    print(f"Removed user-id '{id}' ")
    
def check_session_id(session_id, username):
    #checks if a user is existent with session_id as provided
    dbconn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE
    )
    db_cursor = dbconn.cursor()
    sql = "SELECT username FROM wol_users WHERE session_id = %s "
    '''
        db_cursor.execute(sql, session_id)
        res = db_cursor.fetchall()
        if res is not None:
            return True
        else:
            return False
            
    '''
    return False

def check_user_permissions(session_id, vm_id):
    dbconn = pymysql.connect(
        host="funnywol_db",
        user="root",
        password="Start123#",
        database="wolserver"
    )
    db_cursor = dbconn.cursor()
    sql = "SELECT permissions FROM wol_users WHERE session_id = %s"
    val = (session_id, )
    db_cursor.execute(sql, val)
    user_permissions = db_cursor.fetchall()
    if('admin' not in user_permissions):
        sql = "SELECT tags FROM wol_machines WHERE id = %s"
        val = (vm_id, )
        db_cursor.execute(sql, val)
        vm_permissions = db_cursor.fetchall()
        
        for user_perm in user_permissions:
            if(user_perm in vm_permissions):
                return True #User has permissions to perform action
        return False #User has NO permission toi perform action if this code is worked on.
    else:
        return True #Has admin privileges

def get_vms_for_user_permission(session_id):
    dbconn = pymysql.connect(
        host="funnywol_db",
        user="root",
        password="Start123#",
        database="wolserver"
    )
    db_cursor = dbconn.cursor()
    sql = "SELECT permissions,username FROM wol_users WHERE session_id = %s"
    val = (session_id, )
    db_cursor.execute(sql, val)
    res = db_cursor.fetchall()
    user_permissions = res[0]
    username = res[1]
    
    if('admin' not in user_permissions):
        if isinstance(user_permissions, list):
            vms = []
            for tag in user_permissions: ##user has multiple permissions
                sql = "SELECT id,name FROM wol_machines WHERE tags LIKE %s"
                val = (f"%{tag}%", )
                db_cursor.execute(sql, val)
                vms.extend(db_cursor.fetchall())
            print(f"{username} with multiple permissions was returned this list of vms: {vms}") 
            return vms
        
        elif user_permissions is not None: #user has one permission    
            sql = "SELECT * FROM wol_machines WHERE tags LIKE %s"
            val = (f"%{user_permissions}%", )
            db_cursor.execute(sql, val)
            vms = db_cursor.fetchall()
            print(f"{username} was returned this list of vms: {vms}")    
            return vms
           
    else: #user has admin permissions
        sql = "SELECT id,name FROM wol_machines"
        db_cursor.execute(sql)
        vms = db_cursor.fetchall()
        print(f"adminuser {username} was returned this list of vms: {vms}")
        return vms
            
def auth_user(username, password):
    #checks if a user, selected by username, has the same passwd as provided
    dbconn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE
    )
    db_cursor = dbconn.cursor()
    sql = "SELECT * FROM wol_users WHERE username = %s "
    db_cursor.execute(sql, username)
    res = db_cursor.fetchall()
    db_pass_hash = res[3]
    converted_passwd = hashlib.sha512(password)
    if(converted_passwd.hexdigest() == db_pass_hash):
        session_id = uuid5()
        sql = "UPDATE wol_users SET session_id = %s, WHERE username = %s"
        val = (session_id, username)
        db_cursor.execute(sql, val)
        dbconn.commit()
        return session_id
    else:
        return False