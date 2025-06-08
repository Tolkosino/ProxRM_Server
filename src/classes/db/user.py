from src.classes.db.helper import DatabaseConnection
from src.classes.config.config import Config
import uuid
import bcrypt
import logging

class DB_User:
    def __init__(self):
        """Initializes the database user manager with configuration settings."""
        self.logger = logging.getLogger(__name__)
        self.conf = Config()
        self.conf_database = self.conf.get_database()
        self.DATABASE_INFO = [
            self.conf_database["DB_HOST"],
            self.conf_database["DB_USER"],
            self.conf_database["DB_PASSWORD"],
            self.conf_database["DB_DATABASE"],
            self.conf_database["DB_PORT"]
        ]

    def _hash_password(self, password):
        """Hashes a plaintext password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def create_user(self, username, cleartext_password, permissions):
        """Creates a new user with a hashed password and assigned permissions."""
        hashedpw = self._hash_password(cleartext_password)
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            sql = "INSERT INTO wol_users (username, password, permissions) VALUES (%s, %s, %s)"
            val = (username, hashedpw, permissions)
            success = cursor.execute(sql, val)
            if success == 1:
                self.logger.info(f"Added user '{username}' with permissions: {permissions}")
                return f"User created | {username}"
            else:
                self.logger.warning(f"Error on user creation for {username}")
                return f"Error on user creation | {username}"

    def delete_user(self, user_id):
        """Deletes a user from the database by their ID."""
        username = self.get_user(user_id=user_id)
        if username is None:
            self.logger.warning(f"User with id {user_id} not found")
            return None
        
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            sql = "DELETE FROM wol_users WHERE id = %s"
            val = (user_id,)
            success = cursor.execute(sql, val)
            if success == 1:
                self.logger.info(f"Removed user with id: '{user_id}'")
                return f"User deleted | {username}"
            else:
                self.logger.warning(f"Error deleting user {username} with id {user_id}")
                return None

    def _update_user_session(self, user_id, session_id):
        """Updates the session ID of a user in the database."""
        username = self.get_user(user_id=user_id)
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            sql = "UPDATE wol_users SET session_id = %s WHERE id = %s"
            val = (session_id, user_id)
            success = cursor.execute(sql, val)
            if success == 1:
                self.logger.info(f"Session updated for user {username}")
                return True
            else:
                self.logger.warning(f"Session update failed for user {username} (id: {user_id})")
                return False

    def logout_user(self, session_id):
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            sql = "UPDATE wol_users SET session_id = NULL WHERE session_id = %s "
            val = (session_id,)
            success = cursor.execute(sql, val)
            if success:
                return "Successfully logged out"


    def login_user(self, username, password):
        """Authenticates a user and returns a new session ID if successful."""
        user_id = self.get_user(username=username)
        if not user_id:
            return None
        
        sql = "SELECT password FROM wol_users WHERE id = %s"
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute(sql, (user_id,))
            hashed_password = cursor.fetchone()
            self.logger.info(f"got passwords: {password} and hashed {hashed_password[0]}")
            if hashed_password and bcrypt.checkpw(password.encode(), hashed_password[0].encode()):
                return self._create_session_id(user_id)
            else:
                self.logger.info(f"Wrong password for user: {username}")
                return "WRONG PASSWORD"

    def _create_session_id(self, user_id):
        """Generates a new session ID and updates the user session."""
        session_id = str(uuid.uuid4())
        return session_id if self._update_user_session(user_id, session_id) else "ERROR ON SESSION UPDATE"

    def get_user(self, username=None, session_id=None, user_id=None):
        """Retrieves a user's ID or username based on the provided parameter."""
        if username is not None:
            return self._get_user_by_username(username)
        elif session_id is not None:
            return self._get_user_id_by_session_id(session_id)
        elif user_id is not None:
            return self._get_username_by_id(user_id)

    def _get_username_by_id(self, user_id):
        """Retrieves the username of a user given their user ID."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute("SELECT username FROM wol_users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def _get_user_by_username(self, username):
        """Retrieves the user ID of a user given their username."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute("SELECT id FROM wol_users WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_user_id_by_session_id(self, session_id):
        """Retrieves the user ID associated with a given session ID."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute("SELECT id FROM wol_users WHERE session_id = %s", (session_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def check_permissions(self, user_id, vmId):
        """Checks if the user has permission to access a given virtual machine."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute("SELECT permissions FROM wol_users WHERE id = %s", (user_id,))
            user_permissions = cursor.fetchone()
            self.logger.debug(f"Permissioncheck with userid {user_id} got this permissions {user_permissions}")
            if user_permissions and "admin" in user_permissions[0]:
                return True
            
            cursor.execute("SELECT tags FROM wol_machines WHERE id = %s", (vmId,))
            vm_tags = cursor.fetchone()
            self.logger.debug(f"Permissioncheck for vm with id {vmId} results in folowing permissions: {vm_tags}")
            if not vm_tags or not user_permissions:
                return False
            return bool(set(user_permissions[0].split(',')) & set(vm_tags[0].split(',')))

    def get_vms_for_perms_of_user(self, user_id):
        """Returns all virtual machines a user has permission to access."""
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute("SELECT permissions FROM wol_users WHERE id = %s", (user_id,))
            user_permissions = cursor.fetchone()
            cursor.execute("SELECT id, tags, name FROM wol_machines")
            machines = cursor.fetchall()
            
            if not user_permissions:
                return []
            elif 'admin' in user_permissions:
                return [f"{machine[0]}-{machine[2]}" for machine in machines]
            else:
                accessible_vms = [f"{machine[0]}-{machine[2]}" for machine in machines if set(user_permissions[0].split(',')) & set(machine[1].split(','))]
                
                self.logger.debug(f"Machines for user |{user_id}| found: {accessible_vms}")
                return accessible_vms

    def check_session_id(self, session_id):
        userid = self.get_user_id_by_session_id(session_id)
        if userid:
            return True
        return False