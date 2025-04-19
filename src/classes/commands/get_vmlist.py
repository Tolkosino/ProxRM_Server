from classes.commands.commandBase import CommandBase

class get_vmlist(CommandBase):
    
    def execute(self, **kwargs):
        from src.classes.db.user import DB_User
        
        self.logger.debug("")
        session_id = kwargs.get("session_id")
        user_id = DB_User().get_user_id_by_session_id(session_id)
        vms = DB_User().get_vms_for_perms_of_user(user_id)
        return ";".join(str(x) for x in vms)