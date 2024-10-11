import logging
import json
import pprint
import pandas as pd

import os
from config import Config

class LogLister:
    def __init__(self, logged_host = "") -> None:
        config = Config()
        self.log_dir = config.LOG_PATH
        self.logged_host = logged_host
        
    def getLoggedHosts(self):

        logged_hosts = [d for d in os.listdir(self.log_dir) if os.path.isdir(os.path.join(self.log_dir, d))]
        return logged_hosts
    
    def listAllLogs(self, logged_host):
        log_list = []
        for root, dirs, logs in os.walk(self.log_dir):
            for log in logs:
                if log.endswith('_log') and log.startswith(f'{logged_host}'):
                    log_list.append(self.extract_log_name(log))
        return log_list
    

    def extract_log_name(self, input_string):
        first_index = input_string.find('_')
        last_index = input_string.rfind('_')

        # If both underscores are found, extract the substring between them
        if first_index != -1 and last_index != -1 and first_index != last_index:
            return input_string[first_index + 1:last_index]
        else:
            return ""  # Return an empty string if there are no underscores or only one underscore



if __name__ == "__main__":
    dirList = LogLister()
    print(dirList.getLoggedHosts())
    pprint.pprint(dirList.listAllLogs(logged_host="192.168.0.84"))