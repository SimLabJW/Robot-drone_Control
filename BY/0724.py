import time
from multi_robomaster import multi_robot


'''#### 몸통 ####'''

# 앞으로 전진   w
def move_forward(robot_group):
    robot_group.chassis.move(0.5, 0, 0, 1).wait_for_completed()

# 뒤로 후진    s
def move_backward(robot_group):
    robot_group.chassis.move(-0.3, 0, 0, 1, 0).wait_for_completed()
    
# 왼쪽으로 이동   a
def move_left(robot_group):
    robot_group.chassis.move(0, -0.6, 0, 2, 0).wait_for_completed()

# 오른쪽으로 이동   d
def move_right(robot_group):
    robot_group.chassis.move(0, 0.6, 0, 2, 0).wait_for_completed()

# 오른쪽으로 90도 회전
def rotate_right(robot_group):      
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    time.sleep(0.5)
    robot_group.chassis.move(0, 0, -90, 0, 180).wait_for_completed()

# 왼쪽으로 90도 회전
def rotate_left(robot_group):    
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    time.sleep(0.5)
    robot_group.chassis.move(0, 0, 90, 0, 180).wait_for_completed()


'''#### 짐벌(총) ####'''

def gimbal_down(robot_group):
    robot_group.gimbal.moveto(-20, 0, 180, 180).wait_for_completed()

def gimbal_up(robot_group):
    robot_group.gimbal.moveto(20, 0, 180, 180).wait_for_completed()

# 가운데 정렬
def gimbal_recenter(robot_group):
    robot_group.gimbal.moveto(0, 0, 180, 180).wait_for_completed()   
    
def gimbal_left_up(robot_group):    
    #robot_group.set_group_robots_mode(multi_robot.FREE_MODE)  몸통도 같이 이동
    robot_group.gimbal.moveto(30, -90, 100, 100).wait_for_completed()

def gimbal_right_up(robot_group):
    #robot_group.set_group_robots_mode(multi_robot.FREE_MODE)  몸통도 같이 이동
    robot_group.gimbal.moveto(30, 90, 100, 100).wait_for_completed()


def ep_arm_initial_pos(robot_group):
    robot_group.gimbal.moveto(0, 0, 180, 180).wait_for_completed()
    robot_group.gimbal.moveto(-20, 0, 100, 100).wait_for_completed()


'''#### 집게() ####'''

def arm_forward(robot_group):
    robot_group.robotic_arm.move(x=40, y=0).wait_for_completed()

def arm_backward(robot_group):
    robot_group.robotic_arm.move(x=-40, y=0).wait_for_completed()

def arm_up(robot_group):  
    robot_group.robotic_arm.move(x=0, y=50).wait_for_completed()
        
def arm_down(robot_group):  
    robot_group.robotic_arm.move(x=0, y=-50).wait_for_completed()

def gripper_open(robot_group):
    robot_group.gripper.open(power=50)
    time.sleep(1)
    robot_group.gripper.pause()

def gripper_close(robot_group):
    robot_group.gripper.close(power=50)
    time.sleep(1)
    robot_group.gripper.pause()




'''  메인 코드  '''


if __name__ == '__main__':
    robots_sn_list = ['3JKCK2S00305WL', '3JKCK980030EKR', '3JKCK6U0030A6U'] 
    
    multi_robots = multi_robot.MultiEP()
    multi_robots.initialize()
    
    connected_robots = []
    
    for idx, sn in enumerate(robots_sn_list):
        try:
            # Assign number to the robot to check connection
            if multi_robots.number_id_by_sn([idx, sn]):
                connected_robots.append((idx, sn))
        except:
            # If the assignment fails, it means the robot is not connected
            print(f"Robot with SN {sn} is not connected.")

    if not connected_robots:
        print("No robots are connected.")
        multi_robots.close()
        exit(1)

    print("The number of connected robots is: {0}".format(len(connected_robots)))

    connected_ids = [idx for idx, sn in connected_robots]
    
    robot_group = multi_robots.build_group(connected_ids)  # 전체 연결된 로봇 그룹

    # 움직임 설정
    multi_robots.run([robot_group, arm_up])
    multi_robots.run([robot_group, arm_up])
    multi_robots.run([robot_group, arm_down])
    multi_robots.run([robot_group, arm_down])
    multi_robots.run([robot_group, arm_down]) 
    multi_robots.run([robot_group, arm_backward])
    
    print("END")
    multi_robots.close()
