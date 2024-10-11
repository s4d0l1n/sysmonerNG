import socket
import threading
import json
import redis
from config import Config

class ConnectionHandler:
    config = Config()

    def __init__(self, port, redis_host=f'{config.REDIS_HOST}', redis_port=config.REDIS_PORT, redis_password=f'{config.REDIS_PASSWORD}'):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', port))
        self.server_socket.listen(5)
        self.active_threads = []

        # Set up Redis connection
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0 ,password=redis_password)

    def handle_client(self, client_socket, client_address):
        received_line = b''
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                received_line += data
                if b'\n' in received_line:
                    line, received_line = received_line.split(b'\n', 1)
                    if line.strip():
                        try:
                            json_entry = json.loads(line.decode('utf-8'))
                            # Push the JSON entry to Redis queue (list)
                            self.redis_client.lpush('log_queue', json.dumps({
                                'log_source': json_entry['LogSource'],
                                'client_ip': client_address[0],
                                'message': line.decode('utf-8'),
                                'timestamp': json_entry['TimeCreated'],
                                'eventid': json_entry['EventId'],
                                'recordid': json_entry['RecordId'],
                                'machineName': json_entry['MachineName']
                            }))
                        except json.JSONDecodeError:
                            print(f"Failed to decode JSON from {client_address}: {line}")
        finally:
            client_socket.close()

    def start_server(self):
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
                print(f"{client_address} connected")
                self.active_threads.append(client_thread)

                # Cleanup finished threads
                self.active_threads = [t for t in self.active_threads if t.is_alive()]
        except KeyboardInterrupt:
            print("Server is shutting down...")
            for thread in self.active_threads:
                thread.join()
        finally:
            self.server_socket.close()
            print("Server has shutdown.")

# Start the listener server
server = ConnectionHandler(7070)
server.start_server()
