import os
import importlib
import sys
import logging
from classess.loader.command_factory import CommandFactory 
from classess.commands.commandBase import CommandBase

#Appending plugins folder as search path for importlib
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

PLUGINS_PACKAGE = "commands"
LOGGER = logging.getLogger(__name__)
CURRDIR = os.path.dirname(__file__)

def load_plugins():
    #Rotating through all files in appended path to import various plugins later
    for filename in os.listdir(os.path.join(os.path.dirname(CURRDIR), PLUGINS_PACKAGE)):
        if filename.endswith(".py") and filename not in ["__init__.py", "commandBase.py"]:
            module_name = f"classess.{PLUGINS_PACKAGE}.{filename[:-3]}"
            LOGGER.info(f"Importing module: {module_name} ...")
            module = importlib.import_module(module_name)

            for name, obj in vars(module).items():
                LOGGER.debug(f"Checking {name}: {obj} ({type(obj)})")  # Debugging the class check
                # Ensure obj is a class and subclass of BaseCommand
                if isinstance(obj, type):  # Check if obj is a class
                    LOGGER.debug(f"{name} is a class.")
                    # Explicitly check if it's a subclass of BaseCommand (skip BaseCOmmand itself)
                    if obj is not CommandBase and issubclass(obj, CommandBase):
                        LOGGER.debug(f"Registering {name} as {name.lower()}")  # Debugging the registration
                        CommandFactory.register_command(name.lower(), obj)
                    else:
                        LOGGER.debug(f"{name} does not meet the subclass condition.")  # For debugging only

load_plugins()