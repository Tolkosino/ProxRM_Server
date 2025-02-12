import sys
import logging
from src.classes.server.server import Server
import src.classes.config.config as config

def main():
    """Setup and main execution loop."""
    config = config.load()

    logging.basicConfig(filename=config["LOGFILE"], level=config["LOGLEVEL"])
    logger = logging.getLogger(__name__)

    if len(sys.argv) != 2:
        logger.critical(f"Wrong parameters, usage: {sys.argv[0]} <port>")
        sys.exit(1)
    else:
        logger.info(f"Starting Server on {config["HOST"]}:{config["PORT"]}")
        Server.start()

if __name__ == "__main__":
    main()