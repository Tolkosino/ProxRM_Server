from classess.db.user import DB_User
from classess.loader.command_factory import CommandFactory
import logging


class ProxFacade:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def executeAction(self, cmd_set):
        command = cmd_set.get('command') # login 
        action = cmd_set.get('action') # start|stop
        vmid = cmd_set.get('vmid') # 102
        session_id = cmd_set.get('session_id') # 6546516-asd858746sd-12316tsdf
        res = None
        command = command.lower()
        
        if command not in ["login","logout"]:
            userId = DB_User().get_user_id_by_session_id(session_id)
            
            self.logger.debug(CommandFactory.get_commands())
            if userId and DB_User().check_permissions(userId, vmid) and command in CommandFactory.get_commands():
                self.logger.debug(f"{userId} has permissions")
                command = CommandFactory.create_command(command)
                res = command.execute(vmid=vmid, action=action, session_id=session_id)
            else:
                return "Access Denied"
        elif command in CommandFactory.get_commands() and command in ["login","logout"]:
                command = CommandFactory.create_command(command)
                res = command.execute(vmid=vmid, action=action, session_id=session_id)

        return "FAILURE IN COMMAND EXECUTION" if res is None else res