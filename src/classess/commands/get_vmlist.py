from classess.commands import commandBase

class get_allvms(commandBase):
    
    def execute(self, **kwargs):
        from classess.db.user import DB_User
        session_id = kwargs.get("session_id")
        user_id = DB_User().get_user_id_by_session_id(session_id)
        vms = DB_User().get_vms_for_perms_of_user(user_id)
        return ";".join(str(x) for x in vms)