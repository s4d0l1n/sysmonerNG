import os
import re
import redis
import json
import time
from config import Config

# Class to handle file operations related to logs
class FileHandler:
    def __init__(self):
        # Dictionary to keep track of open file handles for different clients
        self.files = {}

    # Method to sanitize file names by replacing non-alphanumeric characters with underscores
    def sanitize_filename(self, name):
        return re.sub(r'[^\w\-]', '_', name)

    # Method to write log data to multiple files (log, index, event ID, record ID)
    def write_log(self, log_source, client_ip, message, timestamp, eventid, recordid):
        config = Config()  # Load configuration using Config class

        # Sanitize log source name to make it safe for use as a filename
        sanitized_log_source = self.sanitize_filename(log_source)
        
        # Directory path for storing client-specific log files
        directory = f"{config.LOG_PATH}/{client_ip}"
        
        # Unique key to represent the client and log source
        key = f"{client_ip}_{sanitized_log_source}"

        # If the directory does not exist, create it
        if not os.path.exists(directory):
            os.makedirs(directory)

        # If there are no open file handles for this key, open new ones for log, index, event ID, and record ID
        if key not in self.files:
            self.files[key] = {
                "log": open(f"{directory}/{key}_log", "a+"),        # Log file
                "index": open(f"{directory}/{key}_index", "a+"),    # Index file
                "eventId": open(f"{directory}/{key}_eventId", "a+"), # Event ID file
                "recordId": open(f"{directory}/{key}_recordId", "a+") # Record ID file
            }

        # Retrieve open file handles
        log_file = self.files[key]["log"]
        index_file = self.files[key]["index"]
        eventId_file = self.files[key]["eventId"]
        recordId_file = self.files[key]["recordId"]
        
        # Get the current file position (start position) for the log file
        startposition = log_file.tell()

        # Write the log message to the log file and flush to ensure it's written immediately
        log_file.write(message + '\n')
        log_file.flush()

        # Get the file position after writing the log message (end position)
        position = log_file.tell()

        # Write an entry to the index file with timestamp and position info
        index_entry = json.dumps({"t": timestamp, "p": position})
        index_file.write(index_entry + '\n')
        index_file.flush()

        # Write event ID entry to the event ID file, along with the start position
        eventId_entry = json.dumps({"i": eventid, "p": startposition})
        eventId_file.write(eventId_entry + '\n')
        eventId_file.flush()

        # Write record ID entry to the record ID file, along with the start position
        recordId_entry = json.dumps({"i": recordid, "p": startposition})
        recordId_file.write(recordId_entry + '\n')
        recordId_file.flush()

    # Method to close all open file handles gracefully
    def close_files(self):
        for key in self.files:
            self.files[key]["log"].close()
            self.files[key]["index"].close()
            self.files[key]["eventId"].close()
            self.files[key]["recordId"].close()

# Class to handle Redis connection and process log queue
class RedisWriter:
    config = Config()  # Load configuration

    # Initialize RedisWriter by connecting to Redis and initializing a FileHandler
    def __init__(self, redis_host=f'{config.REDIS_HOST}', redis_port=config.REDIS_PORT, redis_password=f'{config.REDIS_PASSWORD}'):
        # Connect to the Redis server using the given configuration
        self.redis_client = redis.StrictRedis(
            host=redis_host, 
            port=redis_port, 
            db=0,  # Default Redis database (db 0)
            password=redis_password
        )
        # Initialize the file handler for managing log files
        self.file_handler = FileHandler()

    # Method to continuously process the Redis log queue
    def process_queue(self):
        while True:
            # Block until a log entry is available in the 'log_queue' or timeout occurs
            log_entry = self.redis_client.brpop('log_queue', timeout=5)
            
            # If a log entry is retrieved, process it
            if log_entry:
                _, log_data = log_entry  # Extract log data (ignore key)
                try:
                    # Decode the log data from bytes to a string, and parse it as JSON
                    log_json = json.loads(log_data.decode('utf-8'))

                    # Write the log data to the appropriate files
                    self.file_handler.write_log(
                        log_json['log_source'], 
                        log_json['client_ip'],
                        log_json['message'], 
                        log_json['timestamp'], 
                        log_json['eventid'],
                        log_json['recordid']
                    )
                except json.JSONDecodeError:
                    # Handle case where the log data is not valid JSON
                    print(f"Failed to decode log data: {log_data}")

    # Method to gracefully shut down the service by closing file handles
    def shutdown(self):
        self.file_handler.close_files()

# Start the Redis writer service
redis_writer = RedisWriter()

try:
    # Start processing the Redis log queue
    redis_writer.process_queue()
except KeyboardInterrupt:
    # On keyboard interrupt (Ctrl+C), shutdown the service
    redis_writer.shutdown()
    print("Writer service shut down.")
