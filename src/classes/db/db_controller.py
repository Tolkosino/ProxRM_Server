import pymysql
import urllib3
import time
import logging
from config import Config

class DB_Controller:
    def __init__(self):
        urllib3.disable_warnings()
        self.conf = Config()
        self.conf_database = self.conf.get_database()
        
        self.logger = logging.getLogger(__name__)
        
        self.HOST = self.conf_database["DB_HOST"]
        self.USER = self.conf_database["DB_USER"]
        self.PASSWORD = self.conf_database["DB_PASSWORD"]
        self.DATABASE = self.conf_database["DB_DATABASE"]
        self.__setup_db()

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

    def __setup_db(self):
        """ Creates database and tables, if not existent."""
        conn, cursor = self._connect_db()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS wolserver")
        conn.select_db(self.DATABASE)  

        #Create table for users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wol_users (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
                username VARCHAR(255) NOT NULL, 
                permissions VARCHAR(255), 
                password VARCHAR(255) NOT NULL, 
                session_id VARCHAR(255)
            )
        """)
        
        #create table for machines
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wol_machines (
                id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                name VARCHAR(255) NOT NULL, 
                tags VARCHAR(255)
            )
        """)

        # if not existent, create default user
        cursor.execute("SELECT COUNT(*) FROM wol_users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO wol_users (username, password, permissions) VALUES ('admin', 'passw0rd', 'admin')")
        
        self.logger.info("DB created successfully.")

        #db_machine.check_latest_vm_definitions()