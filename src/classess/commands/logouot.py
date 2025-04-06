from classess.commands import commandBase

class set_hostaction(commandBase):    

    def execute(self, **kwargs):
        from classess.db.user import DB_User
        session_id = kwargs.get("session_id")
        
        return DB_User().logout_user(session_id)