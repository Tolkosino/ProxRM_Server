import pymysql
import time
import urllib3
import db_machineHandler

urllib3.disable_warnings()

HOST = "funnywol_db"
USER = "root"
PASSWORD = "Start123#"
DATABASE = "wolserver"

def get_db_connection():
    """ Erstellt eine Datenbankverbindung mit Wartezeit für MySQL-Start """
    for i in range(10):  # Maximal 10 Versuche
        try:
            conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE,autocommit=True)
            return conn
        except pymysql.MySQLError as e:
            print(f"DB-Verbindung fehlgeschlagen ({i+1}/10). Fehler: {e}")
            time.sleep(5)  # 5 Sekunden warten, bevor erneut versucht wird
    raise Exception("Konnte keine Verbindung zur Datenbank herstellen.")

def setup_db():
    """ Erstellt die Datenbank und Tabellen, falls sie nicht existieren """
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, autocommit=True)
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS wolserver")
    conn.select_db(DATABASE)  # Datenbank wechseln

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wol_users (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
            username VARCHAR(255) NOT NULL, 
            permissions VARCHAR(255), 
            password VARCHAR(255) NOT NULL, 
            session_id VARCHAR(255)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wol_machines (
            id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
            name VARCHAR(255) NOT NULL, 
            tags VARCHAR(255)
        )
    """)

    # Falls Benutzer noch nicht existiert, einen Standardbenutzer hinzufügen
    cursor.execute("SELECT COUNT(*) FROM wol_users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO wol_users (username, password, permissions) VALUES ('admin', 'passw0rd', 'admin')")
    
    print("Datenbank wurde erfolgreich eingerichtet.")

    db_machineHandler.check_latest_vm_definitions()
    
    
setup_db()
