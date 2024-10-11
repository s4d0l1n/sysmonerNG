import grpc
import json
from concurrent import futures

import pandas as pd
import logservice_pb2
import logservice_pb2_grpc
from logbook import Logbook  # Assuming you have the Logbook class
from logLister import LogLister  # Assuming you have the LogLister class

# LogbookService class implementing the log retrieval functionality
class LogbookService(logservice_pb2_grpc.LogbookServiceServicer):

    # gRPC method to get logs by date range with optional filters
    def GetLogsByDateRange(self, request, context):
        # Extract parameters from the gRPC request
        from_date = request.from_date
        to_date = request.to_date
        filter_key = request.filter_key
        filter_values = list(request.filter_values)  # Convert repeated field into a Python list
        
        # Create a Logbook instance using the provided parameters
        logbook = Logbook(request.client_ip, request.log_name, from_date, to_date)
        
        try:
            # Iterate over logs returned by the Logbook's loadLog method
            for log_entry in logbook.loadLog(filter_key=filter_key if filter_key else None, filter_values=filter_values if filter_values else None):
                # Create a LogEntry message for each log entry
                log_response = logservice_pb2.LogEntry(
                    log_source=log_entry.get("LogSource", ""),
                    event_id=log_entry.get("EventId", 0),
                    time_created=log_entry.get("TimeCreated", ""),
                    record_id=log_entry.get("RecordId", 0),
                    machine_name=log_entry.get("MachineName", ""),
                    event_data=json.dumps(log_entry.get("EventData", {}))  # Serialize EventData into JSON string
                )
                # Yield the LogEntriesResponse containing the log response
                yield logservice_pb2.LogEntriesResponse(entries=[log_response])
        except Exception as e:
            # Handle exceptions and return an INTERNAL gRPC error with details
            context.set_details(f"An error occurred: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)

    # gRPC method to get logs by index (event or record ID)
    def GetLogsByIndex(self, request, context):
        # Extract filter key (eventId or recordId) and values from the gRPC request
        filter_key = request.filter_key
        filter_values = list(request.filter_values)  # Convert repeated field into a Python list
        
        # Create a Logbook instance using the provided parameters
        logbook = Logbook(request.client_ip, request.log_name)
        
        try:
            # Iterate over logs returned by the Logbook's loadLogByIds method
            for log_entry in logbook.loadLogByIds(index_type=filter_key, filter_field=filter_values):
                # Create a LogEntry message for each log entry
                log_response = logservice_pb2.LogEntry(
                    log_source=log_entry.get("LogSource", ""),
                    event_id=log_entry.get("EventId", 0),
                    time_created=log_entry.get("TimeCreated", ""),
                    record_id=log_entry.get("RecordId", 0),
                    machine_name=log_entry.get("MachineName", ""),
                    event_data=json.dumps(log_entry.get("EventData", {}))  # Serialize EventData into JSON string
                )
                # Yield the LogEntriesResponse containing the log response
                yield logservice_pb2.LogEntriesResponse(entries=[log_response])
        except Exception as e:
            # Handle exceptions and return an INTERNAL gRPC error with details
            context.set_details(f"An error occurred: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)

# LogListService class implementing the log listing functionality
class LogListService(logservice_pb2_grpc.LogListServiceServicer):

    # gRPC method to list all logs for a specific host
    def GetLogListByHost(self, request, context):
        logged_host = request.logged_host  # Extract the host parameter from the gRPC request
        
        # Create a LogLister instance to list logs for the specified host
        logLister = LogLister(logged_host)
        try:
            # Return the list of logs for the host in the LogListResponse
            return logservice_pb2.LogListResponse(entries=logLister.listAllLogs(logged_host=logged_host))
        except Exception as e:
            # Handle exceptions and return an INTERNAL gRPC error with details
            context.set_details(f"An error occurred: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
    
    # gRPC method to list all logged hosts
    def GetLogHostList(self, request, context):
        # Create a LogLister instance to list all logged hosts
        logHostLister = LogLister(logged_host="")
        try:
            # Return the list of logged hosts in the LogHostListResponse
            return logservice_pb2.LogHostListResponse(entries=logHostLister.getLoggedHosts())
        except Exception as e:
            # Handle exceptions and return an INTERNAL gRPC error with details
            context.set_details(f"An error occurred: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)

# Function to serve the gRPC server
def serve():
    # Create a gRPC server with a thread pool for handling requests
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register the LogbookService with the gRPC server
    logservice_pb2_grpc.add_LogbookServiceServicer_to_server(LogbookService(), server)
    
    # Register the LogListService with the gRPC server
    logservice_pb2_grpc.add_LogListServiceServicer_to_server(LogListService(), server)
    
    # Bind the server to port 50051 for incoming connections
    server.add_insecure_port('[::]:50051')
    
    # Start the gRPC server
    server.start()
    
    # Keep the server running indefinitely
    server.wait_for_termination()

# Main entry point to start the server
if __name__ == "__main__":
    serve()
