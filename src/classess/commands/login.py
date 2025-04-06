from classess.commands.commandBase import CommandBase

class login(CommandBase):

    def execute(self, **kwargs):
        from classess.db.user import DB_User
        username = kwargs.get("username")
        password = kwargs.get("password")

        session_id = DB_User().login_user(username, password)

        if not session_id == "WRONG PASSWORD":
            self.logger.debug(f"{username} authenticated.")
            return f"authn_{username}_accept;{session_id}" ##User authenticated
        else:
            self.logger.debug(f"{username} provided wrong password.")
            return f"authn_{password}_deny" ##Login denied