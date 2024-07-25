import threading
import time
from RobotController import RobotController

robotcontroller = RobotController()
ep_robot = robotcontroller.initialize_robot("3JKCK980030EKR")

# Device_Sensor를 한 번만 호출하여 콜백을 설정
robotcontroller.Device_Sensor(ep_robot)

# 최신 센서 데이터를 주기적으로 출력
def print_latest_distance():
    while True:
        latest_distance = robotcontroller.get_latest_distance()
        print(f"Latest distance: {latest_distance}")
        time.sleep(1)

# 센서 데이터 출력 스레드 시작
print_thread = threading.Thread(target=print_latest_distance)
print_thread.start()
