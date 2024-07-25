import socket
import threading
import time
import signal
import os
from pynput import keyboard
from RobotController import *

class TCPServer:
    def __init__(self, host='0.0.0.0', ports=[11013]):
        self.robotcontroller = RobotController()
        self.message = None
        self.sensor_message = None

        self.host = host
        self.ports = ports
        self.servers = []
        self.stop_event = threading.Event()
        self.remote_flag = False
        self.image_conn = None  # To hold the connection for image transfer
        self.image_conn_lock = threading.Lock()

        self.ep_robot = self.robotcontroller.initialize_robot("3JKCK980030EKR")
        self.robotcamera = self.robotcontroller.Device_Camera(self.ep_robot)
        self.robotcontroller.Device_Sensor(self.ep_robot)

        for port in self.ports:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.host, port))
            server.listen(5)
            self.servers.append(server)
            print(f"Server is running on port {port}...")


    def send_periodically(self, conn, message, stop_event):
        while not stop_event.is_set():
            if self.remote_flag:
                self.sensor_message = self.robotcontroller.get_latest_distance()
                message = json.dumps(self.sensor_message).encode()
            else:
                self.message = self.robotcontroller.Research_Device()
                message = json.dumps(self.message).encode()

            conn.sendall(message)
            time.sleep(1)  # 1초마다 메시지 전송

    def send_image(self, robotcamera):
        with self.image_conn_lock:
            if self.image_conn:
                # 이미지를 로봇 컨트롤러로부터 가져옴
                image_data = robotcamera.read_cv2_image(strategy="newest")
                img = cv2.resize(image_data, (480, 300))  # 해상도를 조정
                encoded_image = self.convert_image_to_bytes(img)

                try:
                    self.image_conn.sendall(encoded_image)

                except Exception as e:
                    print(f"Failed to send image: {e}")
                    self.image_conn = None

    def handle_client(self, conn, addr, port):
        print(f"Client connected on port {port}: {addr}")
        stop_event = threading.Event()
        send_thread = None

        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.decode()

                if port == 11013:
                    print(f"Received from {addr} on port {port}: {data}")
                    if data == 'Simulation':
                        self.remote_flag = False
                        if send_thread and send_thread.is_alive():
                            stop_event.set()
                            send_thread.join()
                        stop_event.clear()
                        self.message = self.robotcontroller.Research_Device()
                        if not self.message or self.message == "No robots found.":
                            self.message = b"No robots found."
                        else:
                            self.message = json.dumps(self.message).encode()
                        send_thread = threading.Thread(target=self.send_periodically, args=(conn, self.message, stop_event))
                        send_thread.start()
                    elif data == 'Remote':
                        self.remote_flag = True
                        
                        if send_thread and send_thread.is_alive():
                            stop_event.set()
                            send_thread.join()
                        stop_event.clear()
                        self.sensor_message = self.robotcontroller.get_latest_distance()
        
                        if not self.sensor_message :
                            self.sensor_message = b"No robots found."
                        else:
                            self.sensor_message = json.dumps(self.sensor_message).encode()
                        send_thread = threading.Thread(target=self.send_periodically, args=(conn,self.sensor_message, stop_event))
                        send_thread.start()

                elif port == 11014:
                    print(f"Received from {addr} on port {port}: {data}")
                    with threading.Lock():
                        self.image_conn = conn

                    command_thread = threading.Thread(target=self.handle_commands, args=(conn,))
                    command_thread.start()

                    while True:
                        try:
                            if not self.remote_flag:
                               self.image_conn.sendall(b'ping')
                               time.sleep(1)
                            else:
                                self.send_image(self.robotcamera)

                        except Exception as e:
                            print(f"Exception keeping 11014 alive: {e}")
                            with threading.Lock():
                                self.image_conn = None
                            break
        except Exception as e:
            print(f"Exception in client handler on port {port}: {e}")
        finally:
            if send_thread and send_thread.is_alive():
                stop_event.set()
                send_thread.join()
            if port == 11014:
                with threading.Lock():
                    self.image_conn = None
            conn.close()
            print(f"Client disconnected on port {port}: {addr}")

    def convert_image_to_bytes(self, image_data):
        success, encoded_image = cv2.imencode('.jpg', image_data)
        if success:
            return encoded_image.tobytes()
        else:
            return None
        
    def handle_commands(self, conn):
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.decode()
                if self.remote_flag and data in ['W', 'S', 'A', 'D']:
                    self.robomaster_move(data)
        except Exception as e:
            print(f"Exception in command handler: {e}")

    def robomaster_move(self, cmd):
        self.robotcontroller.Move(cmd)
        print(f"robomaster unity cmd : {cmd}")

    def start_server(self):
        signal.signal(signal.SIGINT, self.shutdown)
        threads = []
        try:
            for i, server in enumerate(self.servers):
                thread = threading.Thread(target=self.accept_connections, args=(server, self.ports[i]))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

        except Exception as e:
            print(f"Server error: {e}")
        finally:
            print("Server is shutting down.")
            for server in self.servers:
                server.close()
            os._exit(1)

    def accept_connections(self, server, port):
        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr, port)).start()

    def shutdown(self, signum, frame):
        print("Shutting down server...")
        self.stop_event.set()
        for server in self.servers:
            server.close()
        os._exit(0)

if __name__ == "__main__":
    ports = [11013, 11014]  # 필요한 포트를 추가
    tcp_server = TCPServer(ports=ports)
    tcp_server.start_server()
