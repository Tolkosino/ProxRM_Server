from classes.commands.commandBase import CommandBase

class login(CommandBase):

    def execute(self, **kwargs):
        from classes.db.user import DB_User

        self.logger.debug(f"{self.__name__} kwargs be like: ")
        for i, v in kwargs.items():
            self.logger.debug(f"{i} with value {v} ")

        username = kwargs.get("action")
        password = kwargs.get("vmid")

        session_id = DB_User().login_user(username, password)

        if not session_id == "WRONG PASSWORD":
            self.logger.debug(f"{username} authenticated.")
            return f"authn_{username}_accept;{session_id}" ##User authenticated
        else:
            self.logger.debug(f"{username} provided wrong password.")
            return f"authn_{password}_deny" ##Login denied
        self.logger.debug("This is basically impossible")
