import logging
import json
import pprint
import pandas as pd
from typing import Generator
from config import Config
from typing import Optional, List

# Class to represent a logbook for a particular client and log source
class Logbook:
    # Initialize the Logbook with client IP, log name, and optional filters for date range, event IDs, and record IDs
    def __init__(self, client_ip, log_name, minDate=pd.Timestamp.now(tz='utc') - pd.Timedelta(days=90000), maxDate=pd.Timestamp.now(tz='utc'), eventids: Optional[List[int]] = None, recordids: Optional[List[int]] = None):
        self.client_ip = client_ip  # IP address of the client (log source)
        self.log_name = log_name    # Name of the log file
        # Convert minDate and maxDate to pandas timestamps (ensures correct date formats with timezones)
        self.minDate = pd.to_datetime(minDate, utc=True)
        self.maxDate = pd.to_datetime(maxDate, utc=True)
        self.eventids = eventids    # List of event IDs to filter logs (optional)
        self.recordids = recordids  # List of record IDs to filter logs (optional)

    # Method to load logs based on event or record IDs
    # index_type specifies whether to use 'eventId' or 'recordId', and filter_field contains the values to filter on
    def loadLogByIds(self, index_type: str, filter_field: list) -> Generator[dict, None, None]:
        config = Config()  # Load configuration for paths
        # Build paths for index and log files
        index_file = f'{config.LOG_PATH}/{self.client_ip}/{self.client_ip}_{self.log_name}_{index_type}'
        log_file = f'{config.LOG_PATH}/{self.client_ip}/{self.client_ip}_{self.log_name}_log'
        
        try:
            # Open and read the index file, then normalize it into a pandas DataFrame
            with open(index_file, 'r') as indexFile:
                indexes = [json.loads(line) for line in indexFile]  # Read each line as JSON
                dfIndex = pd.json_normalize(indexes)  # Convert list of dicts to a pandas DataFrame

                # Filter DataFrame based on the provided list of event/record IDs
                filterdf = dfIndex[dfIndex['i'].isin(filter_field)]
                
                # If there are matching entries, proceed to read the corresponding log lines
                if not filterdf.empty:
                    pointers = filterdf['p'].tolist()  # Get the positions of matching logs in the log file

                    # Open the log file and retrieve the log entries by seeking to the correct position
                    with open(log_file, 'rb') as logFile:
                        for pointer in pointers:
                            logFile.seek(pointer)  # Move the file pointer to the position
                            line = logFile.readline()  # Read the log entry
                            if line:
                                log_entry = json.loads(line.decode('utf-8'))  # Decode the line from bytes to JSON
                                yield log_entry  # Yield each log entry as it's read
        except FileNotFoundError:
            # Log an error if the index or log file is not found
            logging.error(f'File {index_file} or {log_file} not found.')
        except Exception as e:
            # Log any unexpected errors during execution
            logging.error(f'An unexpected error occurred: {e}')

    # Method to load logs by event IDs using the general loadLogByIds method
    def loadLogByEventIds(self) -> Generator[dict, None, None]:
        return self.loadLogByIds('eventId', self.eventids)

    # Method to load logs by record IDs using the general loadLogByIds method
    def loadLogByRecordIds(self) -> Generator[dict, None, None]:
        return self.loadLogByIds('recordId', self.recordids)
   
    # Method to load logs based on date range and optional filter criteria (event ID, record ID, etc.)
    def loadLog(self, filter_key: str = None, filter_values: list = None) -> Generator[dict, None, None]:
        config = Config()  # Load configuration for paths
        
        # Build paths for index and log files
        index_file = f'{config.LOG_PATH}/{self.client_ip}/{self.client_ip}_{self.log_name}_index'
        log_file = f'{config.LOG_PATH}/{self.client_ip}/{self.client_ip}_{self.log_name}_log'

        try:
            # Open and read the index file, then normalize it into a pandas DataFrame
            with open(index_file, 'r') as indexFile:
                indexes = [json.loads(line) for line in indexFile]  # Read each line as JSON
                dfIndex = pd.json_normalize(indexes)  # Convert list of dicts to a pandas DataFrame
                dfIndex['t'] = pd.to_datetime(dfIndex['t'], utc=True)  # Ensure the timestamp column is in the correct format

            # Filter the logs based on the specified date range (minDate and maxDate)
            filterdf = dfIndex[(dfIndex['t'] >= self.minDate) & (dfIndex['t'] <= self.maxDate)]

            # If there are matching entries, proceed to read the corresponding log lines
            if not filterdf.empty:
                minPointer = filterdf['p'].min()  # Find the minimum log position (start reading from here)
                maxPointer = filterdf['p'].max()  # Find the maximum log position (stop reading here)

                # Open the log file and read the entries between minPointer and maxPointer
                with open(log_file, 'rb') as logFile:
                    logFile.seek(minPointer)  # Move the file pointer to the start position
                    while logFile.tell() < maxPointer:  # Continue until the pointer reaches the end position
                        line = logFile.readline()  # Read the log entry
                        if line:
                            log_entry = json.loads(line.decode('utf-8'))  # Decode the line from bytes to JSON
                            
                            # If a filter is provided (e.g., filtering by event or record ID), apply the filter
                            if filter_key and filter_values: 
                                if log_entry[f'{filter_key}'] in filter_values:
                                    yield log_entry  # Yield only matching log entries
                            else:
                                yield log_entry  # Yield each log entry if no filter is applied
        except FileNotFoundError:
            # Log an error if the index or log file is not found
            logging.error(f'File {index_file} or {log_file} not found.')
        except Exception as e:
            # Log any unexpected errors during execution
            logging.error(f'An unexpected error occurred: {e}')

# The following block is commented out. It demonstrates how to use the Logbook class for testing purposes.
# if __name__ == "__main__":
#     # Example: Load logs by event ID for a specific client and log name
#     # mylog = Logbook(client_ip="192.168.0.84", log_name="Microsoft-Windows-Sysmon_Operational", eventids=[1,22])
#     # for c in mylog.loadLogByEventIds():
#     #     print(c)

#     # Example: Load logs by record ID within a specified date range for a specific client and log name
#     mylog = Logbook(client_ip="192.168.0.84", log_name="Microsoft-Windows-Sysmon_Operational", minDate="2024-10-11T11:50:14.7104784-07:00")
#     for c in mylog.loadLog(filter_key="RecordId", filter_values=[181250]):
#         print(c)
