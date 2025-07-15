from classes.commands.commandBase import CommandBase

class logout(CommandBase):    

    def execute(self, **kwargs):
        from classes.db.user import DB_User
        session_id = kwargs.get("session_id")
        return DB_User().logout_user(session_id)