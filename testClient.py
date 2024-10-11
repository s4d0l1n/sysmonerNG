import pprint
import grpc
import logservice_pb2
import logservice_pb2_grpc

def get_logs_by_date_range(log_name, from_date, to_date):
    # Create a channel and a stub (client)
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = logservice_pb2_grpc.LogbookServiceStub(channel)

        # Create a request with log_name, from_date, and to_date
        request = logservice_pb2.LogDateRangeRequest(
            log_name=log_name,
            from_date=from_date,
            to_date=to_date
        )

        # Call the GetLogsByDateRange method
        try:
            for response in stub.GetLogsByDateRange(request):
                pprint.pprint(response.entries)
                for entry in response.entries:
                    print(f"Log Source: {entry.log_source}")
                    print(f"Event ID: {entry.event_id}")
                    print(f"Time Created: {entry.time_created}")
                    print(f"Record ID: {entry.record_id}")
                    print(f"Machine Name: {entry.machine_name}")
                    print(f"Event Data: {entry.event_data}")
                    print("-------------")
        except grpc.RpcError as e:
            print(f"Error occurred: {e.details()}")

def get_log_list_by_host(logged_host):
    # Create a channel and a stub (client)
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = logservice_pb2_grpc.LogListServiceStub(channel)

        # Create a request with logged_host
        request = logservice_pb2.LogListRequest(logged_host=logged_host)

        # Call the GetLogListByHost method
        try:
            response = stub.GetLogListByHost(request)
            print(f"Log List for host {logged_host}:")
            for entry in response.entries:
                print(f"Log Name: {entry}")
        except grpc.RpcError as e:
            print(f"Error occurred: {e.details()}")

def get_log_hosts():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = logservice_pb2_grpc.LogListServiceStub(channel)

        request = logservice_pb2.LogHostListRequest()

        try:
            response = stub.GetLogHostList(request)
            for entry in response.entries:
                print(f"host: {entry}")
        except grpc.RpcError as e:
            print(f"Error occured: {e.details()}")

if __name__ == "__main__":
    # Test fetching logs by date range
    print("Fetching logs by date range...")
    get_logs_by_date_range(log_name="192.168.1.120_Microsoft-Windows-Sysmon_Operational", from_date="2024-02-01T00:00:00Z", to_date="2024-11-08T23:59:59Z")

    # Test fetching log names by host
    print("\nFetching log list by host...")
    get_log_list_by_host(logged_host="192.168.1.120")

  # Test fetching log names by host
    print("\nFetching log hosts...")
    get_log_hosts()



# # log_name="192.168.0.84_Microsoft-Windows-Sysmon_Operational",
# #             from_date="2024-02-01T00:00:00Z",  # Update to your desired date range
#             to_date="2024-11-08T23:59:59Z"