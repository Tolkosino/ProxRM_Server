from helper import DatabaseConnection
from config import Config
from uuid import uuid5
import hashlib
import logging

class DB_User():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conf = Config()
        self.conf_database = self.conf.get_database()
        self.DATABASE_INFO = [self.conf_database["DB_HOST"],
                              self.conf_database["DB_USER"],
                              self.conf_database["DB_PASSWORD"],
                              self.conf_database["DB_DATABASE"]
                             ]

    def _hash_password(password):
        """hash passwords"""
        sha512 = hashlib.sha512()
        sha512.update(password)
        return sha512.hexdigest()
    
    def create_user(self, username, cleartext_password, permissions):
        """Create user with provided information after hashing password"""
        hashedpw = self._hash_password(cleartext_password)
        
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            sql = "INSERT INTO wol_users (username, password, permissions) VALUES (%s, %s, %s)"
            val = (username, hashedpw, permissions)
            success = cursor.execute(sql, val)
            if success == 1:
                self.logger.info(f"Added user '{username}' with permissions on tags: {permissions}")
                return f"User created | {username}"
            else:
                self.logger.warning(f"Error on user creation for user {username}")
                return f"Error on user creation | {username}"

    def delete_user(self, user_id):
        """Delete user by id"""
        username = self.get_user(user_id=user_id)

        with DatabaseConnection(self.DATABASE_INFO) as cursor:    
            sql = "DELETE FROM wol_users WHERE id = %s"
            val = (id, )
            success = cursor.execute(sql, val)
            if success == 1:
                self.logger.info(f"Removed user with id: '{id}' ")
                return f"User deleted | {username}"
            else:
                self.logger.warning(f"Error on user deletion for user {username} with id {user_id}")
                return f"Error on user deletion for user {username} with id {user_id}"
            
    def _update_user_session(self, user_id, session_id):
        username = self.get_user(user_id=user_id)
        sql = "UPDATE wol_users SET session_id = %s WHERE user_id = %s"
        val = (session_id, user_id)
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            rowsAff = cursor.execute(sql, val)
            if rowsAff == 1:
                self.logger.info(f"session updated for user {username}")
                return True
            else:
                self.logger.warning(f"Something went wrong during session update for user {username} with id: {user_id}. session to set: {session_id}")
                return False
    
    def _login_user(self, username, password):
        """authenticates user and returns new session id"""
        user_id = self.get_user(username=username)
        sql = "SELECT password FROM wol_users WHERE user_id = %s"
        val = (password,)
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute(sql, val)
            db_password = cursor.fetchone() #Maybe not correct, needs debugging
            if password == db_password:
                return self._create_session_id(user_id)
            else:
                self.logger.info(f"Wrong password for user: {username}")
                return "WRONG PASSWORD"
    
    def _create_session_id(self, user_id):
        session_id = uuid5()
        success = self._update_user_session(user_id, session_id)
        if success:
            return session_id
        else:
            return "ERROR ON SESSION UPDATE"

    def get_user(self, username = None, session_id = None, user_id = None):
        """returns user_id of user, except if user_id is provided then username will be returned."""
        if username is not None:
            return self._get_user_by_username(username)
        elif session_id is not None:
            return self._get_user_id_by_session_id(session_id)
        elif user_id is not None:
            return self._get_username_by_id(user_id)

    def _get_username_by_id(self, user_id):
        """get user by id and return username"""
        sql = "SELECT username FROM wol_users WHERE user_id = %s"
        val = (user_id,)
        with DatabaseConnection(self.DATABASE_INFO) as cursor:
            cursor.execute(sql, val)
            result = cursor.fetchone()
            return result

    def _get_user_by_username(self, username):
            """get user by username and return user id"""
            sql = "SELECT user_id FROM wol_users WHERE username = %s"
            val = (username,)
            with DatabaseConnection(self.DATABASE_INFO) as cursor:
                cursor.execute(sql, val)
                result = cursor.fetchone()
                return result    
        
    def _get_user_id_by_session_id(self, session_id):
            """get user by session_id and return user id"""
            sql = "SELECT user_id FROM wol_users WHERE session_id = %s"
            val = (session_id,)
            with DatabaseConnection(self.DATABASE_INFO) as cursor:
                cursor.execute(sql, val)
                result = cursor.fetchone()
                if not len(result) == 0:
                    return result
                else:
                    self.logger.info(f"INVALID SESSION_ID detected. {session_id}. Maybe a old session or multiple logins from different devices?")
                    return "SPOOFED SESSION_ID"    

    def authenticate_user(self, username = None, password = None, session_id = None, vmId = None):
        """Login user if username and password is provided. Checks for user permission if session_id and vmId is provided. 
        Returns Tuple of Action taken and result.
         Possible Results:
          ("AUTHENTICATED",True) - Is logged in and has permission on vm 
          ("AUTHENTICATED",False) - Is logged in and doesn't have permission
          ("SPOOFED SESSION_ID",FALSE) - session_id not recognized as valid session for any user.
        """
        if (username is not None) and (password is not None):
            session_id = self._login_user(username, password)
            return ("LOGIN", session_id)
        elif (session_id is not None) and (vmId is not None):
            user_id = self._get_user_id_by_session_id(session_id)
            if not user_id == "SPOOFED SESSION_ID": 
                hasPermissions = self._check_permissions(user_id, vmId)
                if hasPermissions:
                    return ("AUTHENTICATED",True)
                else:
                    return ("AUTHENTICATED",False)
            else:
                return ("SPOOFED SESSION_ID",False)
        else:
            self.logger.warning("Usage error in user authentication. Wrong set of Params were given.")



    ''' 
    //////////
    PART BELOW NEEDS FURTHER DEVELOPMENT
    //////////    
    '''

    def _check_permissions(user_id, vmId):
        """checks user permission on specific vm. Returns True|False if user has perms."""
        pass

    def _get_vms_for_perms_of_user(user_id):
        """Returns alls vms a user could possibly take actions on based on his current permissions"""
        pass

    
