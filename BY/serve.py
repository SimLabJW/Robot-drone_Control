import socket
import threading
import time
from RobotController import *

class TCPServer:
    def __init__(self, host='127.0.0.1', port=11013):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.client_socket = None
        self.address = None
        self.keep_sending = True
        self.data = "default_data"
        self.deviceDetailState = "Device Connection"
        self.robotcontroller = RobotController()
        
    def start_server(self):
        print(f'Server started at {self.host}:{self.port}')
        self.client_socket, self.address = self.server_socket.accept()
        print(f'Connection from {self.address}')
        threading.Thread(target=self.send_data).start()
        self.receive_commands()

    def send_data(self):
        
        while self.keep_sending:
            if self.client_socket:
                try:
                    if (self.data == "Simulation"):
                        connection = self.robotcontroller.Research_Device()
    
                        self.deviceDetailState = json.dumps(connection)

                        self.client_socket.sendall(self.deviceDetailState.encode())
                        time.sleep(1)

                    elif self.data == "Remote":
                        self.deviceDetailState = "Device Detial State"
                        self.client_socket.sendall(self.deviceDetailState.encode())
                        time.sleep(1)

                    # else:
                    #     self.client_socket.sendall(self.data.encode())
                    #     time.sleep(1)
                    
                except socket.error as e:
                    print(f'Socket error: {e}')
                    self.keep_sending = False
            else:
                break

    def receive_commands(self):
        while self.keep_sending:
            try:
                command = self.client_socket.recv(1024).decode()
                if command:
                    print(f'Received command: {command}')
                        
                    self.handle_command(command)
            except socket.error as e:
                print(f'Socket error: {e}')
                self.keep_sending = False

    def handle_command(self, command):
        if command == 'STOP':
            self.keep_sending = False
            self.client_socket.close()
        else:
            self.data = command

    def close_server(self):
        if self.client_socket:
            self.client_socket.close()
        self.server_socket.close()

if __name__ == '__main__':
    server = TCPServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print('Server is shutting down.')
        server.close_server()
