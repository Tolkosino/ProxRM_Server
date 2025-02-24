from helper import DatabaseConnection

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
        self.DATABASE_INFO = [self.conf_database["DB_HOST"],
                              self.conf_database["DB_USER"],
                              self.conf_database["DB_PASSWORD"],
                              self.conf_database["DB_DATABASE"]
                             ]

        self.__setup_db()

    def __setup_db(self):
        """ Creates database and tables, if not existent."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:

            cursor.execute("CREATE DATABASE IF NOT EXISTS wolserver")

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
                    id INT NOT NULL PRIMARY KEY, 
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