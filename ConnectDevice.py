import asyncio
from robomaster import robot, camera, conn
from RobotController import *  

class ConnectDevice:
    def __init__(self) -> None:

        self.ep_robot = robot.Robot()
        self.ip_to_sn = {
        "192.168.50.31": "3JKCK2S00305WL",
        "192.168.50.221": "3JKCK6U0030A6U",
        "192.168.50.39": "3JKCK980030EKR"
        }
        self.ip_list = conn.scan_robot_ip_list(timeout=5)

    async def SearchDevcie(self):
        if self.ip_list:
            selected_ips = self.select_robot_ips(self.ip_list)
            robots = [{"name": f"robot_{self.ip_to_sn[ip][-4:]}", "sn": self.ip_to_sn[ip]} for ip in selected_ips if ip in ip_to_sn]
            
            if robots:
                print(f"Selected robots: {robots}")
                esc_event = asyncio.Event()
                tasks = [self.control_robot(robot_info, esc_event) for robot_info in robots]
                tasks.append(self.esc_listener(esc_event))
                await asyncio.gather(*tasks)
            else:
                print("No valid robots selected.")
        else:
            print("No robots found.")

    def select_robot_ips(ip_list):
        for index, ip in enumerate(ip_list):
            print(f"{index + 1}: {ip}")

        return [ip_list[i] for i in ip_list if 0 <= i < len(ip_list)]

    async def control_robot(self, robot_info, esc_event):
        # 로봇을 초기화 및 제어 루프를 실행
        try:
            ep_robot_camera = await self.initialize_robot(robot_info["sn"])
            comm = self.initialize_communication("192.168.50.75", 11014)
            controller = RobotController(ep_robot_camera, robot_info["name"], comm)
            self.setup_callbacks(ep_robot_camera, controller)
            await asyncio.sleep(0.5)
            await controller.capture_data(esc_event, interval=0.1)
        except Exception as e:
            print(f"Error initializing robot {robot_info['name']}: {e}")

    

    def initialize_communication(address, port):
        # 서버와의 통신을 초기화
        return Communication(address, port)

    def setup_callbacks(ep_robot, controller):
        # 로봇의 센서와 아머 이벤트 콜백을 설정
        ep_robot.armor.set_hit_sensitivity(comp="all", sensitivity=100)
        ep_robot.armor.sub_hit_event(controller.hit_callback)
        ep_robot.sensor.sub_distance(freq=20, callback=controller.tof_callback)

    def main(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.SearchDevcie())
        except KeyboardInterrupt:
            print("Ctrl+C pressed. Exiting...")
        finally:
            loop.close()

