import socket
import json
import base64
from datetime import datetime
from threading import Thread

class Server:
    def __init__(self, address="0.0.0.0", port=11014):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((address, port))
        self.socket.listen(5)
        print("Waiting for client connections...")

    def start(self):
        while True:
            conn, addr = self.socket.accept()
            print(f"Connected to {addr}")
            client_thread = Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

    def handle_client(self, conn, addr):
        buffer = ""
        data_list = []
        try:
            while True:
                data = conn.recv(4096).decode('utf-8')
                if not data:
                    print(f"Connection closed by {addr}")
                    break
                buffer += data
                while '\n' in buffer:
                    packet, buffer = buffer.split('\n', 1)
                    print(f"Received packet: {packet}")
                    data_list.append(json.loads(packet))
        except ConnectionResetError:
            print(f"Connection reset by {addr}")
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            if data_list:
                self.save_data(data_list)
            conn.close()

    def save_data(self, data_list):
        try:
            id = data_list[0]["id"]
            start_timestamp = data_list[0]["time"].replace(":", "-").replace(" ", "_")
            end_timestamp = data_list[-1]["time"].replace(":", "-").replace(" ", "_")

            # Save image data and replace it with the filename in the JSON data
            for packet in data_list:
                if packet["imageData"]:
                    image_bytes = base64.b64decode(packet["imageData"])
                    safe_timestamp = packet["time"].replace(":", "-").replace(" ", "_")
                    image_filename = f"{id}_{safe_timestamp}.jpg"
                    with open(image_filename, 'wb') as image_file:
                        image_file.write(image_bytes)
                    print(f"Image saved as {image_filename}")
                    packet["imageData"] = image_filename

            # Save all other data to a single JSON file
            json_filename = f"{id}_{start_timestamp}_to_{end_timestamp}.json"
            with open(json_filename, 'w') as json_file:
                json.dump(data_list, json_file, indent=4)
            print(f"Data saved as {json_filename}")

        except Exception as e:
            print(f"Error saving data: {e}")

    def close(self):
        self.socket.close()

if __name__ == '__main__':
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()
