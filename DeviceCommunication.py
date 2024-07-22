import socket
import json
from datetime import datetime

class Communication:
    def __init__(self, address, port):
        # 서버와의 소켓 통신을 초기화
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))
        print(f"Connected to server at {address}:{port}")

    def send(self, jsondata):

        try:
            self.socket.sendall(jsondata)
        except Exception as e:
            print(f"Error sending data: {e}")

    def close(self):
        # 소켓을 닫음
        self.socket.close()
