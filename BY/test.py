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
        self.host = host
        self.ports = ports
        self.servers = []
        self.stop_event = threading.Event()
        self.image_conn = None  # To hold the connection for image transfer

        for port in self.ports:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.host, port))
            server.listen(5)
            self.servers.append(server)
            print(f"Server is running on port {port}...")

    def send_periodically(self, conn, message, stop_event):
        while not stop_event.is_set():
            conn.sendall(message)
            time.sleep(1)  # 1초마다 메시지 전송

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
                print(f"Received from {addr} on port {port}: {data}")

                if port == 11013:
                    if data == 'Simulation':
                        if send_thread and send_thread.is_alive():
                            stop_event.set()
                            send_thread.join()
                        stop_event.clear()
                        self.message = self.robotcontroller.Research_Device()
                        if not self.message or self.message == "No robots found.":
                            self.message = b"No robots found."
                        else:
                            self.message = self.message.encode()
                        send_thread = threading.Thread(target=self.send_periodically, args=(conn, self.message, stop_event))
                        send_thread.start()
                    elif data == 'Remote':
                        if send_thread and send_thread.is_alive():
                            stop_event.set()
                            send_thread.join()
                        stop_event.clear()
                        send_thread = threading.Thread(target=self.send_periodically, args=(conn, b'bbbb', stop_event))
                        send_thread.start()

                        # Send image to the client connected to port 11014
                        if self.image_conn:
                            robotcamera = self.robotcontroller.Device_Camera  # 이미지를 로봇 컨트롤러로부터 가져옴
                            image_data = robotcamera.read_cv2_image(strategy="newest")

                            img = cv2.resize(image_data, (480, 300))  # 해상도를 조정
                            encoded_image = self.convert_image_to_bytes(img)

                            self.image_conn.sendall(encoded_image)
                        else:
                            print("No client connected on port 11014 to send the image.")
                    else:
                        conn.sendall(b'Unknown command')
                elif port == 11014:
                    self.image_conn = conn

        except Exception as e:
            print(f"Exception in client handler on port {port}: {e}")
        finally:
            if send_thread and send_thread.is_alive():
                stop_event.set()
                send_thread.join()
            conn.close()
            print(f"Client disconnected on port {port}: {addr}")

    def convert_image_to_bytes(self, image_data):
        # 이미지를 PNG 형식으로 메모리 버퍼에 인코딩
        success, encoded_image = cv2.imencode('.png', image_data)
        if success:
            # 성공적으로 인코딩된 경우, 바이트 데이터를 반환
            return encoded_image.tobytes()
        else:
            # 인코딩 실패 시, None 반환
            return None

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
