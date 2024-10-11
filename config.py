import json

# Class to load configuration settings from a JSON file
class Config:
    def __init__(self) -> None:
        # Open and load the config.json file
        with open('/home/richard/Documents/pySysmoner/pySysmoner/sysmonerNG/config.json', 'r') as f:
            config = json.load(f)  # Load the JSON content into a Python dictionary
            
            # Assign the configuration values to instance variables
            self.LOG_PATH = config['log_path']        # Path where logs are stored
            self.REDIS_HOST = config['redis_host']    # Redis server hostname or IP
            self.REDIS_PASSWORD = config['redis_password']  # Redis server password
            self.REDIS_PORT = config['redis_port']    # Redis server port
