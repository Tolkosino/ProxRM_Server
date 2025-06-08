import logging
from classes.server.Server import Server
from classes.db.controller import DB_Controller
from classes.db.machine import DB_Machine
from classes.config.config import Config
from classes.loader import registry

def main():
    """Setup and main execution loop."""
    config = Config()
    conf_logger = config.get_logging()
    conf_proxrm_server = config.get_proxrm_server()

    logging.basicConfig(filename=conf_logger["LOGFILE"], level=conf_logger["LOGLEVEL"])
    logger = logging.getLogger(__name__)

    logger.info(f"Load DB Connection and setup as needed...")
    db_controller = DB_Controller()
    db_controller.setup_db()
    machine_handler = DB_Machine()
    machine_handler.reload_local_database()
    
    logger.info(f"Starting Server on {conf_proxrm_server["HOST"]}:{conf_proxrm_server["PORT"]}")
    server = Server(conf_proxrm_server["HOST"], conf_proxrm_server["PORT"], conf_logger["LOGFILE"])
    server.start()

if __name__ == "__main__":
    main()
