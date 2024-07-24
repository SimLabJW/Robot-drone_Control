import asyncio
import random
import cv2
from robomaster import robot, camera, conn
import socket
import json
import base64
from datetime import datetime
import keyboard

#이게 맞는건지 모르겠음,,,

class Communication:
    def __init__(self, address, port):
        # 서버와의 소켓 통신을 초기화
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))
        print(f"Connected to server at {address}:{port}")

    def send(self, id, timestamp, image_data, distance, hit_info=None):
        # 데이터를 서버로 전송
        hit_info = hit_info if hit_info else [None, None]
        packet = {
            "id": id,
            "time": timestamp,
            "imageData": image_data,
            "distance": distance,
            "hitInfo": hit_info
        }
        json_data = json.dumps(packet) + '\n'
        try:
            self.socket.sendall(json_data.encode('utf-8'))
        except Exception as e:
            print(f"Error sending data: {e}")

    def close(self):
        # 소켓을 닫음
        self.socket.close()

    @staticmethod
    def time():
        # 현재 시간을 문자열 형식으로 반환
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class RobotController:
    def __init__(self, ep_robot, robot_name, comm):
        # 로봇 제어기 초기화
        self.ep_robot = ep_robot
        self.robot_name = robot_name
        self.comm = comm
        self.distance = 0  # 초기 거리 값

    async def capture_data(self, esc_event, interval=0.1):
        # 주기적으로 데이터를 캡처하고 서버로 전송
        try:
            while not esc_event.is_set():
                timestamp = Communication.time()
                img = self.ep_robot.camera.read_cv2_image(strategy="newest")
                image_data = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode('utf-8') if img is not None else None
                self.comm.send(self.robot_name, timestamp, image_data, self.distance)
                print(f"{self.robot_name} sent data at {timestamp} with distance: {self.distance}")
                await asyncio.sleep(interval)
            
            print(f"{self.robot_name} Exit, Bye!")
            await self.shutdown()
        except Exception as e:
            print(f"Error in capture_data loop: {e}")
            await self.shutdown()

    async def shutdown(self):
        # 로봇과의 연결을 종료
        self.ep_robot.camera.stop_video_stream()
        self.ep_robot.close()
        self.comm.close()

    def tof_callback(self, sub_info):
        # ToF 센서로부터 거리를 업데이트
        self.distance = sub_info[0]

    def hit_callback(self, sub_info):
        # 로봇이 충격을 받을 때 호출
        armor_id, hit_type = sub_info
        timestamp = Communication.time()
        img = self.ep_robot.camera.read_cv2_image(strategy="newest")
        image_data = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode('utf-8') if img is not None else None
        hit_info = [armor_id, hit_type]
        
        # 충격시 로봇 색 변환
        print(f"{self.robot_name} Physical hit event: armor_id={armor_id}, hit_type={hit_type}")
        self.ep_robot.led.set_led(comp="all", r=random.randint(0, 255), g=random.randint(0, 255), b=random.randint(0, 255))  
        self.comm.send(self.robot_name, timestamp, image_data, self.distance, hit_info)

async def control_robot(robot_info, esc_event):
    # 로봇을 초기화 및 제어 루프를 실행
    try:
        ep_robot = await initialize_robot(robot_info["sn"])
        comm = initialize_communication("192.168.50.75", 11014)
        controller = RobotController(ep_robot, robot_info["name"], comm)
        setup_callbacks(ep_robot, controller)
        await asyncio.sleep(0.5)
        await controller.capture_data(esc_event, interval=0.1)
    except Exception as e:
        print(f"Error initializing robot {robot_info['name']}: {e}")

async def initialize_robot(sn):
    # 로봇을 초기화 및 비디오 스트림을 시작
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta", sn=sn)
    ep_robot.camera.start_video_stream(display=False, resolution=camera.STREAM_360P)
    return ep_robot

def initialize_communication(address, port):
    # 서버와의 통신을 초기화
    return Communication(address, port)

def setup_callbacks(ep_robot, controller):
    # 로봇의 센서와 아머 이벤트 콜백을 설정
    ep_robot.armor.set_hit_sensitivity(comp="all", sensitivity=100)
    ep_robot.armor.sub_hit_event(controller.hit_callback)
    ep_robot.sensor.sub_distance(freq=20, callback=controller.tof_callback)

async def main():
    # 메인 함수
    # 로봇을 스캔 및 제어 루프를 실행 
    ip_to_sn = {
        "192.168.50.31": "3JKCK2S00305WL",
        "192.168.50.221": "3JKCK6U0030A6U",
        "192.168.50.39": "3JKCK980030EKR"
    }

    ip_list = conn.scan_robot_ip_list(timeout=5)
    
    if ip_list:
        selected_ips = select_robot_ips(ip_list)
        robots = [{"name": f"robot_{ip_to_sn[ip][-4:]}", "sn": ip_to_sn[ip]} for ip in selected_ips if ip in ip_to_sn]
        
        if robots:
            print(f"Selected robots: {robots}")
            esc_event = asyncio.Event()
            tasks = [control_robot(robot_info, esc_event) for robot_info in robots]
            tasks.append(esc_listener(esc_event))
            await asyncio.gather(*tasks)
        else:
            print("No valid robots selected.")
    else:
        print("No robots found.")

def select_robot_ips(ip_list):
    # 사용자로부터 로봇 IP를 선택받음 / 시리얼넘버로 뽑을 수 있는지,,
    print("Available robots:")
    for index, ip in enumerate(ip_list):
        print(f"{index + 1}: {ip}")
    
    selected_indices = input("Select robots by numbers (comma separated): ")
    selected_indices = [int(i.strip()) - 1 for i in selected_indices.split(',') if i.strip().isdigit()]
    return [ip_list[i] for i in selected_indices if 0 <= i < len(ip_list)]

async def esc_listener(esc_event):
    # ESC 키를 눌렀는지 감지 및 종료 이벤트를 설정
    while not esc_event.is_set():
        if keyboard.is_pressed('esc'):
            esc_event.set()
            print("ESC key pressed. Stopping all robots.")
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    # 메인 프로그램 실행
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Ctrl+C pressed. Exiting...")
    finally:
        loop.close()


