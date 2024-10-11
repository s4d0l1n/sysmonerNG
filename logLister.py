import logging
import json
import pprint
import pandas as pd
import os
from config import Config

# Class responsible for listing logs for specific hosts
class LogLister:
    def __init__(self, logged_host = "") -> None:
        # Load configuration to get the log directory path
        config = Config()
        self.log_dir = config.LOG_PATH  # Directory where logs are stored
        self.logged_host = logged_host  # Optional parameter to filter logs for a specific host

    # Method to get a list of all logged hosts (subdirectories under the log directory)
    def getLoggedHosts(self):
        # List directories inside the log directory, representing logged hosts
        logged_hosts = [d for d in os.listdir(self.log_dir) if os.path.isdir(os.path.join(self.log_dir, d))]
        return logged_hosts
    
    # Method to list all logs for a specific host
    def listAllLogs(self, logged_host):
        log_list = []  # Initialize an empty list to store the logs

        # Traverse the log directory and its subdirectories
        for root, dirs, logs in os.walk(self.log_dir):
            # Loop through the logs found in the directory
            for log in logs:
                # Filter logs that end with '_log' and start with the logged host's name
                if log.endswith('_log') and log.startswith(f'{logged_host}'):
                    # Extract the log name (formatted appropriately) and add to the list
                    log_list.append(self.extract_log_name(log))
        return log_list
    
    # Helper method to extract the meaningful part of the log name
    def extract_log_name(self, input_string):
        # Find the first and last underscore in the log filename
        first_index = input_string.find('_')
        last_index = input_string.rfind('_')

        # If both underscores are found, extract the substring between them
        if first_index != -1 and last_index != -1 and first_index != last_index:
            return input_string[first_index + 1:last_index]
        else:
            return ""  # Return an empty string if the format is not as expected


# Main block to test the functionality of the LogLister class
if __name__ == "__main__":
    # Create an instance of LogLister
    dirList = LogLister()

    # Print the list of logged hosts (subdirectories in the log directory)
    print(dirList.getLoggedHosts())

    # Pretty print all logs for a specific host (e.g., '192.168.0.84')
    pprint.pprint(dirList.listAllLogs(logged_host="192.168.0.84"))

    # Pretty print the list of logged hosts again
    pprint.pprint(dirList.getLoggedHosts())
