import base64
import cv2
from datetime import datetime
import random
import json
import time

from multi_robomaster import multi_robot
from robomaster import robot, camera, conn
import sys

class RobotController():
    def __init__(self): 
        self.distance = 0  # 초기 거리 값
        self.ep_robot = None
        
        self.ip_to_sn = {
        "192.168.50.31": "3JKCK2S00305WL",  # 집게 로봇
        "192.168.50.221": "3JKCK6U0030A6U", # 5층 로봇
        "192.168.50.39": "3JKCK980030EKR"   # 6층 로봇
        }
        
    def Research_Device(self):
        self.ip_list = conn.scan_robot_ip_list(timeout=1)
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


    def Device_Camera(self, ep_robot):
        ep_camera = ep_robot.camera
        ep_camera.start_video_stream(display=False)
        return ep_camera

    def initialize_robot(self, sn):
        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type="sta", sn=sn)
        self.ep_chassis = self.ep_robot.chassis

        return self.ep_robot

    def Device_Sensor(self, ep_robot):
        ep_robot.sensor.sub_distance(freq=4, callback=self.tof_callback)
        
    
    def get_latest_distance(self):
        return [{"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], "distance": self.distance}]
    
    ##################################################

    def tof_callback(self, sub_info):
        # ToF 센서로부터 거리를 업데이트
        self.distance = sub_info[0]

    def hit_callback(self, sub_info):
        # 로봇이 충격을 받을 때 호출
        # armor_id, hit_type = sub_info
        timestamp = self.time()
        
        # hit_info = [armor_id, hit_type]
        
  
        # self.ep_robot.led.set_led(comp="all", r=random.randint(0, 255), g=random.randint(0, 255), b=random.randint(0, 255))  

        return [{"timestamp":timestamp, "distance":self.distance}] #hit_info

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

    ###############################################################################################
    # 로봇 1개
    def control_one():
        
        return    
    
    
    
    # 다중 로봇 
    def control_multi():
    
        # 집게, 5층, 6층
        robots_sn_list = ['3JKCK2S00305WL', '3JKCK6U0030A6U', '3JKCK980030EKR']
        
        multi_robots = multi_robot.MultiEP()
        multi_robots.initialize()
        
        number = multi_robots.number_id_by_sn([0, robots_sn_list[0]], [1, robots_sn_list[1]], [2, robots_sn_list[2]])
        
        print("The number of robot is: {0}".format(number))
        robot_group_all = multi_robots.build_group([0, 1, 2])
        
        robot_group_ep_arm = multi_robots.build_group([0])       # 집게
        robot_group_ep_gimbal = multi_robots.build_group([1, 2])    # 총
        
        return
    

    
    def Move(self, key):
        
        try:
            # Define body movement based on key
            body_movement = {
                'W': (0.3, 0, 0),
                'S': (-0.3, 0, 0),
                'A': (0, -0.3, 0),
                'D': (0, 0.3, 0),
                'Q': (0, 0, 45),
                'E': (0, 0, -45)
            }
            x, y, z = body_movement[key]
            self.ep_chassis.move(x=x, y=y, z=z, xy_speed=0.7, z_speed=45).wait_for_completed()
        except KeyError:
            print(f"Invalid key: '{key}'. Terminating program.")
            sys.exit(1)  # 프로그램을 에러 코드와 함께 종료
