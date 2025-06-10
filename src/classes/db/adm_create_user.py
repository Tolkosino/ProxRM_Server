import time
import pymysql
import tomli
import bcrypt

class DatabaseConnection:
    """Context manager for managing MySQL database connections with automatic retries."""

    def __init__(self, database_info):
        """
        Initializes the database connection manager.

        :param database_info: Tuple containing (host, user, password, database, port).
        """
        self.HOST, self.USER, self.PASSWORD, self.DATABASE, self.PORT = database_info
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
                print(f"DB connection failed (attempt {attempt}/10). Error: {e}")
                time.sleep(5)
        
        print("Failed to connect to the database after 10 attempts.")
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

class Config():
    def __init__(self):
         self._load()

    def _load(self):
        with open("src/config.toml", mode="rb") as fp:
            self.config = tomli.load(fp)

    def get_database(self):
        return self.config["database"]
    
    def get_proxmox(self):
        return self.config["proxmox"]
    
    def get_proxrm_server(self):
            return self.config["proxrm_server"]
    
    def load(self):
        return self._load() 
    
def create_user( username, cleartext_password, permissions):
    """Creates a new user with a hashed password and assigned permissions."""
    hashedpw = hash_password(cleartext_password)
    conf = Config()
    conf_database = conf.get_database()
    
    DATABASE_INFO = [
        conf_database["DB_HOST"],
        conf_database["DB_USER"],
        conf_database["DB_PASSWORD"],
        conf_database["DB_DATABASE"],
        conf_database["DB_PORT"]
    ] 

    with DatabaseConnection(DATABASE_INFO) as cursor:
        sql = "INSERT INTO wol_users (username, password, permissions) VALUES (%s, %s, %s)"
        val = (username, hashedpw, permissions)
        success = cursor.execute(sql, val)
        if success == 1:
            print(f"Added user '{username}' with permissions: {permissions}")
            return f"User created | {username}"
        else:
            print(f"Error on user creation for {username}")
            return f"Error on user creation | {username}"

def hash_password(password):
    """Hashes a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()      

username = input("Username: ")
password = input("Password: ")
permissions = input("Permissions: ")

create_user(username, password, permissions)