class CommandFactory:
    import logging
    #Private dict that stores registered plugins provided by registry.py

    _events = {}
    _logger =  logging.getLogger(__name__)
    #Using the @classmethod decorator makes the method belong to the class instead of its instance.
    #This simplifies calling the method globally without creating an instance of EventFactory() each time.


    @classmethod
    def register_command(cls, name, event_cls):
        cls._logger.debug(f"Registering Plugin: {name}")
        cls._events[name] = event_cls

    #Creates and returns an instance of the event handler based on the event type registered

    @classmethod
    def create_command(cls, type):
        if type not in cls._events:
            print(cls._events)
            raise ValueError(f"Unknown Notification type: {type}")
        return cls._events[type]()
    
    @classmethod
    def get_commands(cls):
        return cls._events