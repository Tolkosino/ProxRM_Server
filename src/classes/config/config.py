import logging

class config:

    def load():
        return {
            "LOGFILE" : "12-02-2025.log",
            "LOGLEVEL" : logging.INFO,
            "HOST" : "127.0.0.1",
            "PORT" : 35560,
            "NODENAME": "pve",
            "PROX_HOST": "192.168.178.224",
            "PROX_TOKEN": "root@pam!anotherOne",
            "PROX_SECRET": "63cf9982-50e7-4127-93f7-73c4b7789cd6",
            "DB_HOST" : "funnywol_db",
            "DB_USER" : "root",
            "DB_PASSWORD" : "Start123",
            "DB_DATABASE" : "wolserver",
        }