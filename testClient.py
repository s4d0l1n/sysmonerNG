import pprint
import grpc
import logservice_pb2
import logservice_pb2_grpc

# Function to fetch logs based on a date range and optional filters
def get_logs_by_date_range(client_ip, log_name, from_date, to_date, filter_key: str = None, filter_values: list = None):
    # Create a gRPC channel to connect to the server on localhost at port 50051
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = logservice_pb2_grpc.LogbookServiceStub(channel)  # Create a stub (client) for the LogbookService

        # Create a LogDateRangeRequest object with the necessary fields
        request = logservice_pb2.LogDateRangeRequest(
            client_ip=client_ip,
            log_name=log_name,
            from_date=from_date,
            to_date=to_date,
            filter_key=filter_key,
            filter_values=filter_values
        )

        # Call the GetLogsByDateRange RPC method
        try:
            # Iterate through the response from the server, yielding log entries
            for response in stub.GetLogsByDateRange(request):
                pprint.pprint(response.entries)  # Pretty print the log entries
                for entry in response.entries:   # Loop through each log entry
                    print(f"Log Source: {entry.log_source}")
                    print(f"Event ID: {entry.event_id}")
                    print(f"Time Created: {entry.time_created}")
                    print(f"Record ID: {entry.record_id}")
                    print(f"Machine Name: {entry.machine_name}")
                    print(f"Event Data: {entry.event_data}")
                    print("-------------")
        except grpc.RpcError as e:
            print(f"Error occurred: {e.details()}")

# Function to fetch logs based on event IDs or record IDs
def get_logs_by_index(client_ip, log_name, filter_key: str, filter_values: list):
    # Create a gRPC channel to connect to the server on localhost at port 50051
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = logservice_pb2_grpc.LogbookServiceStub(channel)  # Create a stub (client) for the LogbookService

        # Create a LogByIdRequest object with the necessary fields
        request = logservice_pb2.LogByIdRequest(
            client_ip=client_ip,
            log_name=log_name,
            filter_key=filter_key,
            filter_values=filter_values
        )

        # Call the GetLogsByIndex RPC method
        try:
            # Iterate through the response from the server, yielding log entries
            for response in stub.GetLogsByIndex(request):
                pprint.pprint(response.entries)  # Pretty print the log entries
                for entry in response.entries:   # Loop through each log entry
                    print(f"Log Source: {entry.log_source}")
                    print(f"Event ID: {entry.event_id}")
                    print(f"Time Created: {entry.time_created}")
                    print(f"Record ID: {entry.record_id}")
                    print(f"Machine Name: {entry.machine_name}")
                    print(f"Event Data: {entry.event_data}")
                    print("-------------")
        except grpc.RpcError as e:
            print(f"Error occurred: {e.details()}")

# Function to get a list of logs available for a specific host
def get_log_list_by_host(logged_host):
    # Create a gRPC channel to connect to the server on localhost at port 50051
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = logservice_pb2_grpc.LogListServiceStub(channel)  # Create a stub (client) for the LogListService

        # Create a LogListRequest object with the necessary fields
        request = logservice_pb2.LogListRequest(logged_host=logged_host)

        # Call the GetLogListByHost RPC method
        try:
            # Get the list of logs for the specified host
            response = stub.GetLogListByHost(request)
            print(f"Log List for host {logged_host}:")
            for entry in response.entries:  # Loop through each log name entry
                print(f"Log Name: {entry}")
        except grpc.RpcError as e:
            print(f"Error occurred: {e.details()}")

# Function to get a list of all logged hosts
def get_log_hosts():
    # Create a gRPC channel to connect to the server on localhost at port 50051
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = logservice_pb2_grpc.LogListServiceStub(channel)  # Create a stub (client) for the LogListService

        # Create a LogHostListRequest object with no fields (empty request)
        request = logservice_pb2.LogHostListRequest()

        # Call the GetLogHostList RPC method
        try:
            # Get the list of all hosts
            response = stub.GetLogHostList(request)
            for entry in response.entries:  # Loop through each host entry
                print(f"host: {entry}")
        except grpc.RpcError as e:
            print(f"Error occured: {e.details()}")

# Main function to test the gRPC client methods
if __name__ == "__main__":
    # Example: Fetching log names for a specific host
    print("\nFetching log list by host...")
    get_log_list_by_host(logged_host="192.168.0.84")

    # Example: Fetching the list of logged hosts
    print("\nFetching log hosts...")
    get_log_hosts()

    # Example: Fetching logs by index (eventId or recordId)
    get_logs_by_index(client_ip="192.168.0.84", log_name="Microsoft-Windows-Sysmon_Operational", filter_key="eventId", filter_values=[5])
