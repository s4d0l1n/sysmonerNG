import socket
import threading
import json
import redis
from config import Config

# Class to handle server connections and manage incoming data
class ConnectionHandler:
    # Load configuration using a Config class (assumed to handle Redis settings)
    config = Config()

    # Constructor to initialize server and Redis connection
    def __init__(self, port, redis_host=f'{config.REDIS_HOST}', redis_port=config.REDIS_PORT, redis_password=f'{config.REDIS_PASSWORD}'):
        # Create a TCP/IP socket for the server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the server to all network interfaces (0.0.0.0) and the provided port
        self.server_socket.bind(('0.0.0.0', port))
        
        # Set up the socket to listen for incoming connections (up to 5 in the queue)
        self.server_socket.listen(5)
        
        # List to keep track of active threads (handling client connections)
        self.active_threads = []

        # Set up a Redis client connection using the provided configuration
        self.redis_client = redis.StrictRedis(
            host=redis_host, 
            port=redis_port, 
            db=0,  # Default database 0
            password=redis_password
        )

    # Method to handle communication with a connected client
    def handle_client(self, client_socket, client_address):
        received_line = b''  # Buffer to accumulate data from client
        try:
            while True:
                # Receive data from the client, 1024 bytes at a time
                data = client_socket.recv(1024)
                
                # Break if no more data is received (client disconnected)
                if not data:
                    break
                
                # Append the received data to the buffer
                received_line += data
                
                # Check if a complete line (ending with '\n') has been received
                if b'\n' in received_line:
                    # Split the buffer at the newline character
                    line, received_line = received_line.split(b'\n', 1)
                    
                    # Proceed only if the line is not empty
                    if line.strip():
                        try:
                            # Decode the line from bytes to a string and parse it as JSON
                            json_entry = json.loads(line.decode('utf-8'))
                            
                            # Prepare a structured JSON entry and push it to a Redis list
                            self.redis_client.lpush('log_queue', json.dumps({
                                'log_source': json_entry['LogSource'],  # Log source from the JSON data
                                'client_ip': client_address[0],        # Client's IP address
                                'message': line.decode('utf-8'),       # Original message received
                                'timestamp': json_entry['TimeCreated'], # Log timestamp
                                'eventid': json_entry['EventId'],       # Event ID
                                'recordid': json_entry['RecordId'],     # Record ID
                                'machineName': json_entry['MachineName'] # Machine name from the JSON data
                            }))
                        except json.JSONDecodeError:
                            # Print error if the received line is not valid JSON
                            print(f"Failed to decode JSON from {client_address}: {line}")
        finally:
            # Close the client socket after finishing communication
            client_socket.close()

    # Method to start the server and handle incoming connections
    def start_server(self):
        try:
            while True:
                # Accept a new client connection
                client_socket, client_address = self.server_socket.accept()
                
                # Create a new thread to handle the client connection
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
                
                # Print information about the connected client
                print(f"{client_address} connected")
                
                # Add the thread to the list of active threads
                self.active_threads.append(client_thread)

                # Clean up finished threads (remove inactive threads from the list)
                self.active_threads = [t for t in self.active_threads if t.is_alive()]
        except KeyboardInterrupt:
            # Handle server shutdown gracefully on keyboard interrupt (Ctrl+C)
            print("Server is shutting down...")
            
            # Wait for all active threads to finish before shutting down
            for thread in self.active_threads:
                thread.join()
        finally:
            # Close the server socket
            self.server_socket.close()
            print("Server has shutdown.")

# Start the listener server on port 7070
server = ConnectionHandler(7070)
server.start_server()
