import pymysql
import time
import logging

class DatabaseConnection:
    """Context manager for managing MySQL database connections with automatic retries."""

    def __init__(self, database_info):
        """
        Initializes the database connection manager.

        :param database_info: Tuple containing (host, user, password, database, port).
        """
        self.HOST, self.USER, self.PASSWORD, self.DATABASE, self.PORT = database_info
        self.logger = logging.getLogger(__name__)
        self.conn = None  # Initialize connection attribute

    def __enter__(self):
        """
        Establishes a database connection and returns a cursor.
        Retries up to 10 times in case of failure.

        :return: pymysql cursor object.
        :raises: Exception if connection fails after 10 attempts.
        """
        for attempt in range(1, 11):  # Retry up to 10 times
            try:
                self.conn = pymysql.connect(
                    host=self.HOST,
                    user=self.USER,
                    port=self.PORT,
                    password=self.PASSWORD,
                    database=self.DATABASE,
                    autocommit=True
                )
                return self.conn.cursor()
            except pymysql.MySQLError as e:
                self.logger.warning(f"DB connection failed (attempt {attempt}/10). Error: {e}")
                time.sleep(5)
        
        self.logger.critical("Failed to connect to the database after 10 attempts.")
        raise Exception("Couldn't connect to the Database!")

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the database connection upon exiting the context.

        :param exc_type: Exception type (if any).
        :param exc_value: Exception value (if any).
        :param traceback: Traceback object (if any).
        """
        if self.conn:
            self.conn.close()
            self.conn = None  # Free up memory
