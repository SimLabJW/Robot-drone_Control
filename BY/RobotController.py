import base64
import cv2
import datetime
import random
import json

from robomaster import robot, camera, conn

class RobotController():
    def __init__(self):
        self.ep_robot = robot.Robot()

        self.distance = 0  # 초기 거리 값

        self.ep_robot = robot.Robot()
        self.ip_to_sn = {
        "192.168.50.31": "3JKCK2S00305WL",
        "192.168.50.221": "3JKCK6U0030A6U",
        "192.168.50.39": "3JKCK980030EKR"
        }
        
    def Research_Device(self):
        self.ip_list = conn.scan_robot_ip_list(timeout=5)
        if self.ip_list:
            selected_ips = self.select_robot_ips(self.ip_list)
            robots = [{"name": f"robot_{self.ip_to_sn[ip][-4:]}", "sn": self.ip_to_sn[ip]} for ip in selected_ips if ip in self.ip_to_sn]
            
            device_connect = self.Device_Connect(robots)
            return device_connect
        else:
            print("No robots found.")

    def select_robot_ips(self, ip_list):

        return [ip_list[i] for i in range(len(ip_list))]

    def Device_Connect(self, robots):
        if robots:
            return robots
        else:
            return print("No valid robots selected.")

     ################################################       

    def Device_Camera(self, sn):
        
        self.ep_robot.initialize(conn_type="sta", sn=sn)
        self.ep_robot.camera.start_video_stream(display=False, resolution=camera.STREAM_360P)
        return self.ep_robot

    def Device_Sensor(self, controller):
        # 로봇의 센서와 아머 이벤트 콜백을 설정
        self.ep_robot.armor.set_hit_sensitivity(comp="all", sensitivity=100)
        self.ep_robot.armor.sub_hit_event(controller.hit_callback)
        self.ep_robot.sensor.sub_distance(freq=20, callback=controller.tof_callback)

    ##################################################

    async def shutdown(self):
        # 로봇과의 연결을 종료
        self.ep_robot_camera.camera.stop_video_stream()
        self.ep_robot_camera.close()
        self.comm.close()

    @staticmethod
    def time():
        # 현재 시간을 문자열 형식으로 반환
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


    def tof_callback(self, sub_info):
        # ToF 센서로부터 거리를 업데이트
        self.distance = sub_info[0]

    def hit_callback(self, sub_info):
        # 로봇이 충격을 받을 때 호출
        armor_id, hit_type = sub_info
        timestamp = self.time()
        img = self.ep_robot_camera.camera.read_cv2_image(strategy="newest")
        image_data = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode('utf-8') if img is not None else None
        hit_info = [armor_id, hit_type]
        
        # 충격시 로봇 색 변환
        print(f"{self.robot_name} Physical hit event: armor_id={armor_id}, hit_type={hit_type}")
        self.ep_robot.led.set_led(comp="all", r=random.randint(0, 255), g=random.randint(0, 255), b=random.randint(0, 255))  
        self.comm.send(self.robot_name, timestamp, image_data, self.distance, hit_info)



    def json_convert(id, timestamp, image_data, distance, hit_info=None):
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

        return json_data.encode('utf-8')

    @staticmethod
    def time():
        # 현재 시간을 문자열 형식으로 반환
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]