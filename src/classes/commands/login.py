from classes.commands.commandBase import CommandBase

class login(CommandBase):

    def execute(self, **kwargs):
        self.logger.debug("This is before DB_User import")
        from classes.db.user import DB_User
        self.logger.debug("This is after import")
        username = kwargs.get("action")
        password = kwargs.get("vmid")
        self.logger.debug(f"{username}, {password}")

        session_id = DB_User().login_user(username, password)
        self.logger.debug(f"{session_id}")

        if not session_id == "WRONG PASSWORD":
            self.logger.debug(f"{username} authenticated.")
            return f"authn_{username}_accept;{session_id}" ##User authenticated
        else:
            self.logger.debug(f"{username} provided wrong password.")
            return f"authn_{password}_deny" ##Login denied
        self.logger.debug("This is basically impossible")
