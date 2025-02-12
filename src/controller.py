import sys
import logging
from classes.server import Server
from config import Config

def main():
    """Setup and main execution loop."""
    conf_logger = Config.get_logging()
    conf_proxrm_server = Config.get_proxrm_server

    logging.basicConfig(filename=conf_logger["LOGFILE"], level=conf_logger["LOGLEVEL"])
    logger = logging.getLogger(__name__)

    if len(sys.argv) != 2:
        logger.critical(f"Wrong parameters, usage: {sys.argv[0]} <port>")
        sys.exit(1)
    else:
        logger.info(f"Starting Server on {conf_proxrm_server["HOST"]}:{conf_proxrm_server["PORT"]}")
        Server.start()

if __name__ == "__main__":
    main()