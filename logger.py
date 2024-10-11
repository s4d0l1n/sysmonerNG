import os
import re
import redis
import json
import time
from config import Config

class FileHandler:
    def __init__(self):
        self.files = {}

    def sanitize_filename(self, name):
        return re.sub(r'[^\w\-]', '_', name)

    def write_log(self, log_source, client_ip, message, timestamp, eventid, recordid, machinename):
        config = Config()
        
        
 

        sanitized_log_source = self.sanitize_filename(log_source)
        directory = f"{config.LOG_PATH}/{client_ip}"
        key = f"{client_ip}_{sanitized_log_source}"

        if not os.path.exists(directory):
            os.makedirs(directory)

        if key not in self.files:
            self.files[key] = {
                "log": open(f"{directory}/{key}_log", "a+"),
                "index": open(f"{directory}/{key}_index", "a+"),
                "eventId" : open(f"{directory}/{key}_eventId", "a+"),
                "recordId" : open(f"{directory}/{key}_recordId", "a+"),
                "machineName" : open(f"{directory}/{key}_machineName", "a+")
            }

        log_file = self.files[key]["log"]
        index_file = self.files[key]["index"]
        eventId_file = self.files[key]["eventId"]
        recordId_file = self.files[key]["recordId"]
        machineName_file = self.files[key]["machineName"]
        startposition = log_file.tell()
        # Write to log file
        log_file.write(message + '\n')
        log_file.flush()

        
        position = log_file.tell()
        # Write to index file
        index_entry = json.dumps({"ts": timestamp, "pt": position})
        index_file.write(index_entry + '\n')
        index_file.flush()

        # Write to eventId index file
        
        eventId_entry = json.dumps({"eId": eventid, "pt": startposition})
        eventId_file.write(eventId_entry + '\n')
        eventId_file.flush()

        # Write to recordId index file
        
        recordId_entry = json.dumps({"rId": recordid, "pt": startposition})
        recordId_file.write(recordId_entry + '\n')
        recordId_file.flush()

        # Write to machineName index file just incase machine name changes for that ip
        
        machineName_entry = json.dumps({"rId": machinename, "pt": startposition})
        machineName_file.write(machineName_entry + '\n')
        machineName_file.flush()

    def close_files(self):
        for key in self.files:
            self.files[key]["log"].close()
            self.files[key]["index"].close()
            self.files[key]["eventId"].close()
            self.files[key]["recordId"].close()
            self.files[key]["machineName"].close()


class RedisWriter:
    config = Config()

    def __init__(self, redis_host=f'{config.REDIS_HOST}', redis_port=config.REDIS_PORT, redis_password=f'{config.REDIS_PASSWORD}'):
        # Connect to Redis
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0, password=redis_password)
        self.file_handler = FileHandler()

    def process_queue(self):
        while True:
            # Fetch a log entry from Redis queue (blocking pop)
            log_entry = self.redis_client.brpop('log_queue', timeout=5)
            if log_entry:
                _, log_data = log_entry
                try:
                    # Decode the log data and process it
                    log_json = json.loads(log_data.decode('utf-8'))
                    self.file_handler.write_log(log_json['log_source'], log_json['client_ip'],
                                                log_json['message'], log_json['timestamp'], log_json['eventid'],
                                                log_json['recordid'], log_json['machineName'])
                except json.JSONDecodeError:
                    print(f"Failed to decode log data: {log_data}")

    def shutdown(self):
        self.file_handler.close_files()

# Start the Redis writer service
redis_writer = RedisWriter()
try:
    redis_writer.process_queue()
except KeyboardInterrupt:
    redis_writer.shutdown()
    print("Writer service shut down.")
