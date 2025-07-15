from classes.commands.commandBase import CommandBase

class login(CommandBase):

    def execute(self, **kwargs):
        from classes.db.user import DB_User

        username = kwargs.get("action")
        password = kwargs.get("vmid")
        session_id = DB_User().login_user(username, password)

        if session_id is not None:
            self.logger.debug(f"{username} logged in.")
            return f"authn_{username}_accept;{session_id}"
        else:
            return f"authn_{username}_deny" ##Login denied
        self.logger.debug("This is basically impossible")
