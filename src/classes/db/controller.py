from classes.db.helper import DatabaseConnection
from classes.config.config import Config
import pymysql
import urllib3
import logging
import time

class DB_Controller:
    """Database Controller for initializing and managing database schema."""

    def __init__(self):
        """Initializes the database configuration and sets up the database if necessary."""
        urllib3.disable_warnings()
        self.logger = logging.getLogger(__name__)
        
        conf = Config()
        conf_database = conf.get_database()
        self.HOST = conf_database["DB_HOST"]
        self.USER = conf_database["DB_USER"]
        self.PASSWORD = conf_database["DB_PASSWORD"]
        self.DATABASE = conf_database["DB_DATABASE"]
        self.PORT = conf_database["DB_PORT"]

    def setup_db(self):
        """Creates database and tables if they do not exist."""
        try:
            for attempt in range(1, 11):  # Retry up to 10 times
                try:
                    self.conn = pymysql.connect(
                        host=self.HOST,
                        user=self.USER,
                        port=self.PORT,
                        password=self.PASSWORD,
                        autocommit=True
                    )
                    cursor = self.conn.cursor()
                except pymysql.MySQLError as e:
                    self.logger.warning(f"DB connection failed (attempt {attempt}/10). Error: {e}")
                    time.sleep(5)

            
            cursor.execute("CREATE DATABASE IF NOT EXISTS wolserver")
            cursor.execute("USE wolserver")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wol_users (
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    username VARCHAR(255) NOT NULL, 
                    permissions VARCHAR(255),
                    host_permissions VARCHAR(255), 
                    password VARCHAR(255) NOT NULL, 
                    session_id VARCHAR(255)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wol_machines (
                    id INT PRIMARY KEY, 
                    name VARCHAR(255) NOT NULL, 
                    tags VARCHAR(255)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wol_nodes (
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    name VARCHAR(255) NOT NULL
                )
            """)

            cursor.execute("SELECT COUNT(*) FROM wol_users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO wol_users (username, password, permissions) 
                    VALUES (%s, %s, %s)
                """, ('admin', 'passw0rd', 'admin'))

            self.logger.info("Database setup completed successfully.")
        except pymysql.MySQLError as e:
            self.logger.critical(f"Database setup failed: {e}")
            raise