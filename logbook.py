import logging
import json
import pprint
import pandas as pd
from typing import Generator
from config import Config
from typing import Optional, List

class Logbook:
    def __init__(self, client_ip, log_name, minDate=pd.Timestamp.now(tz='utc') - pd.Timedelta(days=90000), maxDate=pd.Timestamp.now(tz='utc'), eventid: Optional[List[int]]=None, recordid: Optional[List[int]]=None, machineName: Optional[List[int]]=None):
        self.client_ip = client_ip
        self.log_name = log_name
        # Convert minDate and maxDate to timestamps
        self.minDate = pd.to_datetime(minDate, utc=True)
        self.maxDate = pd.to_datetime(maxDate, utc=True)
        self.eventid = eventid
        self.recordid = recordid
        self.machineName = machineName

    def loadLogByEventIds(self) -> Generator[dict, None, None]:
        config = Config()
        index_file = f'{config.LOG_PATH}/{self.client_ip}/{self.client_ip}_{self.log_name}_eventId'
        log_file = f'{config.LOG_PATH}/{self.client_ip}/{self.client_ip}_{self.log_name}_log'
        try:
            # Read the index file and normalize it
            with open(index_file, 'r') as indexFile:
                indexes = [json.loads(line) for line in indexFile]
                dfIndex = pd.json_normalize(indexes)
               

                # Filter the entries based on date range
                filterdf = dfIndex[dfIndex['eId'].isin(self.eventid)]
                
                if not filterdf.empty:
                    # minPointer = filterdf['pt'].min()
                    # maxPointer = filterdf['pt'].max()
                    pointers = filterdf['pt'].tolist()
                    
                    # Open the log file and read log entries within the pointer range
                    with open(log_file, 'rb') as logFile:
                        for pointer in pointers:
                            
                            logFile.seek(pointer)
                            # while logFile.tell() < pointer:
                            line = logFile.readline()
                            # print(line)
                            if line:
                                log_entry = json.loads(line.decode('utf-8'))
                                # Yield each log entry instead of appending to a list
                                yield log_entry
        except FileNotFoundError:
            logging.error(f'File {index_file} or {log_file} not found.')
        except Exception as e:
            logging.error(f'An unexpected error occurred: {e}')
        

    def loadLog(self) -> Generator[dict, None, None]:
        config = Config()
        

        index_file = f'{config.LOG_PATH}/{self.client_ip}/{self.client_ip}_{self.log_name}_index'
        log_file = f'{config.LOG_PATH}/{self.client_ip}/{self.client_ip}_{self.log_name}_log'
        try:
            # Read the index file and normalize it
            with open(index_file, 'r') as indexFile:
                indexes = [json.loads(line) for line in indexFile]
                dfIndex = pd.json_normalize(indexes)
                dfIndex['ts'] = pd.to_datetime(dfIndex['ts'], utc=True)

                # Filter the entries based on date range
                filterdf = dfIndex[(dfIndex['ts'] >= self.minDate) & (dfIndex['ts'] <= self.maxDate)]
                
                if not filterdf.empty:
                    minPointer = filterdf['pt'].min()
                    maxPointer = filterdf['pt'].max()

                    # Open the log file and read log entries within the pointer range
                    with open(log_file, 'rb') as logFile:
                        logFile.seek(minPointer)
                        while logFile.tell() < maxPointer:
                            line = logFile.readline()
                            if line:
                                log_entry = json.loads(line.decode('utf-8'))
                                # Yield each log entry instead of appending to a list
                                yield log_entry
        except FileNotFoundError:
            logging.error(f'File {index_file} or {log_file} not found.')
        except Exception as e:
            logging.error(f'An unexpected error occurred: {e}')
        
    
if __name__ == "__main__":
    mylog = Logbook(client_ip="192.168.1.120",log_name="Microsoft-Windows-Sysmon_Operational",eventid=[1])
    for c in mylog.loadLogByEventIds():
        # None
        print(c)