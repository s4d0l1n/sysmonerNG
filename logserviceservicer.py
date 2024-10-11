import grpc
import json
from concurrent import futures

import pandas as pd
import logservice_pb2
import logservice_pb2_grpc
from logbook import Logbook  # Assuming you have the Logbook class
from logLister import LogLister

class LogbookService(logservice_pb2_grpc.LogbookServiceServicer):
    # def __init__(self, log_name):
    #     self.log_name = log_name

    def GetLogsByDateRange(self, request, context):
        # Parse the dates
        from_date = request.from_date
        to_date = request.to_date
        
        # Instantiate the Logbook class with the log name and date range
        logbook = Logbook(request.log_name, from_date, to_date)
        
        # Stream log entries back to the client
        try:
            for log_entry in logbook.loadLog():
                log_response = logservice_pb2.LogEntry(
                    log_source=log_entry.get("LogSource", ""),
                    event_id=log_entry.get("EventId", 0),
                    time_created=log_entry.get("TimeCreated", ""),
                    record_id=log_entry.get("RecordId", 0),
                    machine_name=log_entry.get("MachineName", ""),
                    event_data=json.dumps(log_entry.get("EventData", {}))
                )
                yield logservice_pb2.LogEntriesResponse(entries=[log_response])
        except Exception as e:
            context.set_details(f"An error occurred: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)

class LogListService(logservice_pb2_grpc.LogListServiceServicer):


    def GetLogListByHost(self, request, context):
        logged_host = request.logged_host
        
        logLister = LogLister(logged_host)
        try:

            return logservice_pb2.LogListResponse(entries=logLister.listAllLogs(logged_host=logged_host))
        except Exception as e:
            context.set_details(f"An error occurred: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
    
    def GetLogHostList(self, request, context):
        logHostLister = LogLister(logged_host="")
        try:
            return logservice_pb2.LogHostListResponse(entries=logHostLister.getLoggedHosts())
        except Exception as e:
            context.set_details(f"An error occurred: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logservice_pb2_grpc.add_LogbookServiceServicer_to_server(LogbookService(), server)
    logservice_pb2_grpc.add_LogListServiceServicer_to_server(LogListService(), server)
    
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
