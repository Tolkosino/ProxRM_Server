from classes.commands.commandBase import CommandBase

class get_vmlist(CommandBase):
    
    def execute(self, **kwargs):
        from classes.db.user import DB_User
        
        self.logger.debug(f"{self.__name__} kwargs be like: ")
        for i, v in kwargs.items():
            self.logger.debug(f"{i} with value {v} ")

        session_id = kwargs.get("session_id")
        user_id = DB_User().get_user_id_by_session_id(session_id)
        vms = DB_User().get_vms_for_perms_of_user(user_id)
        res = ";".join(str(x) for x in vms)
        self.logger.debug(f"returning available vms for user: {res}")        
        
        return res

