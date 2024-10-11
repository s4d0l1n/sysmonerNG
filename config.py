import json

class Config:
    def __init__(self) -> None:
        with open('/home/richard/Documents/pySysmoner/pySysmoner/sysmonerNG/config.json', 'r') as f:
            config = json.load(f)
            self.LOG_PATH = config['log_path']
            self.REDIS_HOST = config['redis_host']
            self.REDIS_PASSWORD = config['redis_password']
            self.REDIS_PORT = config['redis_port']



