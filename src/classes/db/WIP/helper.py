import pymysql
import time
import logging

class DatabaseConnection(object):
    """Simple context manager for database connection"""
        
    def __init__(self, database_info):
        self.HOST, self.USER, self.PASSWORD, self.DATABASE = database_info
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        for i in range(10):
            try:
                self.conn = pymysql.connect(
                    host=self.HOST,
                    user=self.USER,
                    password=self.PASSWORD,
                    database=self.DATABASE,
                    autocommit=True
                )
                return self.conn.cursor()
            except pymysql.MySQLError as e:
                self.logger.warning(f"DB-Connection failed. ({i+1}/10). Error: {e}")
                time.sleep(5)
        self.logger.critical("Couldn't connect to Database!")
        raise Exception("Couldn't connect to Database!")
    
    def __exit__(self, *args):
        self.conn.close()
    
    
    
    
    
    
    
    
    
    
    
    
    def _connect_db(self):
        """ Create database connection."""
