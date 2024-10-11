# SysmonerNG

**SysmonerNG** is a lightweight tool designed for the collection and processing of Windows event logs. This tool is optimized for managing large log files, making it easy to retrieve, store, and process system events for further analysis. It includes features for scanning log files against Sigma rules and uses a gRPC service for log retrieval and management.

## Features

- **Windows Event Log Collection**: Collects Windows event logs in JSON format.
- **Efficient Storage**: Stores logs in flat files with indexed positions for quick lookups.
- **gRPC Services**: Exposes gRPC endpoints for retrieving log data and managing logs.
- **Sigma Rule Integration**: Scan logs using Sigma rules and tag events.
- **Log Indexing**: Supports timestamp-based indexing for quick access to specific events.
- **Redis Integration**: Utilizes Redis for caching and queuing logs between services.

## File Overview

- **`config.py`**: Configuration file that contains necessary parameters for running the service, such as Redis settings, file paths, and service ports.
- **`listener.py`**: Implements the TCP listener that receives Windows event logs in JSON format and stores them in a flat file, updating an index file with byte offsets for quick access.
- **`logLister.py`**: Provides utilities for listing log entries from the stored log files based on the indexed timestamps.
- **`logbook.py`**: Manages the flat file where log events are written and retrieved. Includes methods for handling the file format and ensuring efficient writes and reads.
- **`logger.py`**: Handles the logging mechanism of the system, ensuring that logs are written with proper metadata for future retrieval.
- **`logservice.proto`**: Defines the gRPC service, including methods for log retrieval and querying.
- **`logservice_pb2.py` and `logservice_pb2_grpc.py`**: Auto-generated Python code from the `.proto` file that handles gRPC communication between client and server.
- **`logserviceservicer.py`**: Implements the gRPC servicer, allowing clients to interact with the event log files, retrieve logs, and submit queries.
- **`testClient.py`**: A test client script that connects to the gRPC service to retrieve and query logs, demonstrating how the gRPC service can be used.

## Installation

To set up **SysmonerNG**, follow the steps below:

### Prerequisites

- Python 3.8+
- `pip` for managing Python packages
- Redis (for caching and queuing)
- Protocol Buffers (`protoc`) for compiling the gRPC `.proto` file
- Docker (Optional: for containerized deployment)

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/SysmonerNG.git
cd SysmonerNG
```
### Step 2: Install required dependencies

```bash
pip install -r requirements.txt
```
### Step 3: Set up Redis (Optional)

Make sure Redis is running on your machine. You can install it locally or use Docker:

```bash
docker run --name redis -d redis
```

### Step 4: Running the gRPC Service

To start the gRPC service:

```bash
python logserviceservicer.py
```

This will start the gRPC service on the specified port (as configured in `config.py`).

### Step 5: Using the Test Client

You can interact with the gRPC service using the `testClient.py` script:

```bash
python testClient.py
```

This will connect to the gRPC server and demonstrate how to retrieve logs, submit queries, and test the overall functionality.

## Usage

Once the service is running, the following functionalities are available:

- **Log Collection**: The service listens for incoming JSON-formatted logs from Windows endpoints over TCP, stores them in flat files, and indexes the logs by timestamp.
- **Log Retrieval**: Logs can be retrieved through the gRPC service, filtered by timestamp or other criteria.
- **Sigma Rule Scanning**: Logs can be scanned against Sigma rules to detect suspicious events. Detected events are tagged and can be retrieved through the gRPC service.
- **Caching and Queuing**: Redis is used to queue logs for processing and cache recent logs for faster access.

## Configuration

You can modify the configuration settings in `config.py` to suit your environment:

- **Redis Settings**: Adjust the Redis host and port to match your setup.
- **Log File Paths**: Configure the path where logs are stored.
- **gRPC Port**: Change the port for the gRPC service if needed.
  
## Future Improvements

- **Docker Support**: Add Docker configuration files for easier containerized deployment.
- **Enhanced Sigma Rule Support**: Implement more robust Sigma rule parsing and searching features.
- **Additional Log Formats**: Add support for other log formats beyond JSON.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
```
 +-------------------+        gRPC Calls         +----------------------+
 |                   | ------------------------> |                      |
 |    gRPC Client    |                           |       gRPC Server    |
 |                   | <------------------------ |                      |
 +-------------------+                            +----------------------+
    |     |     |                                      |           |
    |     |     |                                      |           |
    |     |     |                                      |           |
    |     |     |                                      |           |
    V     V     V                                      V           V
+-----------------------+                         +-------------------------+
|   get_logs_by_date     |  <-------------------> |     LogbookService       |
|   get_logs_by_index    |                        |                          |
|   get_log_list_by_host |                        |  - GetLogsByDateRange    |
|   get_log_hosts        |                        |  - GetLogsByIndex        |
+-----------------------+                         +-------------------------+
                                                         |
                                                         |
                                               +--------------------------+
                                               |                          |
                                               |     Logbook Component    |
                                               |                          |
                                               |  - loadLog               |
                                               |  - loadLogByEventIds     |
                                               |  - loadLogByRecordIds    |
                                               +--------------------------+
                                                         |
                                                         |
                                               +--------------------------+
                                               |   File Storage (Logs)     |
                                               |                           |
                                               |  - Log files by host/log  |
                                               |  - Index files            |
                                               +--------------------------+

                            +------------------------+    
                            |                        |    
                            |    LogListService      |    
                            |                        |    
                            |  - GetLogListByHost    |    
                            |  - GetLogHostList      |    
                            +------------------------+    
                                         |
                                         |
                              +------------------------+
                              |                        |
                              |   LogLister Component  |
                              |                        |
                              |  - listAllLogs         |
                              |  - getLoggedHosts      |
                              +------------------------+
                                         |
                                         |
                              +------------------------+
                              |   config.json          |
                              |   - log_path           |
                              |   - redis_host         |
                              |   - redis_password     |
                              |   - redis_port         |
                              +------------------------+

```
```
+---------------------+        gRPC        +--------------------------+
|                     |  <---------------->|                          |
|     gRPC Client     |                    |      gRPC Server         |
|                     |                    |                          |
+---------------------+                    +--------------------------+
                                               |                  |
                                               |                  |
                                               V                  V
                                      +------------------+    +------------------+
                                      |                  |    |                  |
                                      |  LogbookService  |    |  LogListService  |
                                      |                  |    |                  |
                                      +------------------+    +------------------+
                                               |                  |
                                  +------------+                  +------------+
                                  |                                            |
                            +--------------------+                +--------------------+
                            |                    |                |                    |
                            |      Logbook       |                |    LogLister       |
                            |    (Business Logic)|                |   (Business Logic) |
                            +--------------------+                +--------------------+
                                  |                                          |
                                  |                                          |
                            +--------------------+                +--------------------+
                            |                    |                |                    |
                            |   Redis (Optional) | <------------->|  File Storage (Flat|
                            |   for caching or   |                |   Files: Logs,     |
                            |    event queue     |                |   Indexes)         |
                            +--------------------+                +--------------------+
                                  |
                                  |
                            +--------------------+
                            |   config.json      |
                            |  (Configuration    |
                            |  for paths, Redis  |
                            |  settings, etc.)   |
                            +--------------------+
```
