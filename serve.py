import socket
import json
from threading import Thread
from RobotController import RobotController

class Server:
    def __init__(self, address="0.0.0.0", port=11014):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((address, port))
        self.socket.listen(5)
        print("Waiting for client connections...")

    def unity_socket(self):
        # Unity와의 연결 설정
        self.socket_unity = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_unity.bind(("0.0.0.0", 11013)) # Unity Port 11013
        self.socket_unity.listen(5)
        print("Waiting for unity connections...")
        
        

    def handle_unity_connection(self):
        # Unity 연결 처리
        while True:
            self.conn_u, self.addr_u = self.socket_unity.accept()
            print(f"Connected to {self.addr_u}")
            try:
                recv_data = self.conn_u.recv(4096).decode("utf-8")
                if not recv_data:
                    continue
                else:
                    if recv_data == "Unity Start":
                        print(recv_data)
                        device_connect = self.robotcontroller.Research_Device()
                        print(f"aa + {device_connect[0]['name']}")
                        print(f"bb + {device_connect[1]['name']}")

                        json_data = json.dumps(device_connect)
                        self.conn_u.send(json_data.encode('utf-8'))

                    elif recv_data == "Remote":
                        continue
            except ConnectionResetError:
                print("Connection lost. Waiting for reconnection...")
                self.conn_u, self.addr_u = self.socket_unity.accept()
                print(f"Reconnected to {self.addr_u}")
            except Exception as e:
                print(f"An error occurred: {e}")

    def start(self):
        # 서버 시작
        self.unity_thread = Thread(target=self.handle_unity_connection)
        self.unity_thread.start()

    def close(self):
        # 서버 종료
        self.socket_unity.close()

if __name__ == '__main__':
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()





    # def device_socket(self):
    #     # for unity
    #     self.socket_device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.socket_device.bind(("0.0.0.0", 11014)) # Unity Port 11013
    #     self.socket_device.listen(5)
    #     self.conn_d, self.addr_d = self.socket_device.accept()
    #     print(f"Connected to {self.addr_d}")
    #     print("Waiting for device connections...")




    # def handle_client(self, conn, addr):
    #     buffer = ""
    #     data_list = []
    #     try:
    #         while True:
    #             data = conn.recv(4096).decode('utf-8')
    #             if not data:
    #                 print(f"Connection closed by {addr}")
    #                 break
    #             buffer += data
    #             while '\n' in buffer:
    #                 packet, buffer = buffer.split('\n', 1)
    #                 print(f"Received packet: {packet}")
    #                 data_list.append(json.loads(packet))
    #     except ConnectionResetError:
    #         print(f"Connection reset by {addr}")
    #     except Exception as e:
    #         print(f"Error handling client {addr}: {e}")
    #     finally:
    #         conn.close()



    # def start(self): # Unity Open Recv 
        
    #     while True:
    #         conn, addr = self.socket.accept()
    #         print(f"Connected to {addr}")
    #         client_thread = Thread(target=self.handle_client, args=(conn, addr))
    #         client_thread.start()

# def save_data(self, data_list):
#         try:
#             id = data_list[0]["id"]
#             start_timestamp = data_list[0]["time"].replace(":", "-").replace(" ", "_")
#             end_timestamp = data_list[-1]["time"].replace(":", "-").replace(" ", "_")

#             # Save image data and replace it with the filename in the JSON data
#             for packet in data_list:
#                 if packet["imageData"]:
#                     image_bytes = base64.b64decode(packet["imageData"])
#                     safe_timestamp = packet["time"].replace(":", "-").replace(" ", "_")
#                     image_filename = f"{id}_{safe_timestamp}.jpg"
#                     with open(image_filename, 'wb') as image_file:
#                         image_file.write(image_bytes)
#                     print(f"Image saved as {image_filename}")
#                     packet["imageData"] = image_filename

#             # Save all other data to a single JSON file
#             json_filename = f"{id}_{start_timestamp}_to_{end_timestamp}.json"
#             with open(json_filename, 'w') as json_file:
#                 json.dump(data_list, json_file, indent=4)
#             print(f"Data saved as {json_filename}")

#         except Exception as e:
#             print(f"Error saving data: {e}")
