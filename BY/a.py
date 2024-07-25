import time
from multi_robomaster import multi_robot

##### 로봇 종류별 움직임 확인했음 #####

'''################ 몸통 ################'''    #6개 

# 앞으로 전진   W
def move_forward(robot_group):
    robot_group.chassis.move(0.5, 0, 0, 1).wait_for_completed()

# 뒤로 후진    S
def move_backward(robot_group):
    robot_group.chassis.move(-0.3, 0, 0, 1).wait_for_completed()

# 왼쪽으로 이동   A
def move_left(robot_group):
    robot_group.chassis.move(0, -0.6, 0, 2).wait_for_completed()

# 오른쪽으로 이동   D
def move_right(robot_group):
    robot_group.chassis.move(0, 0.6, 0, 2).wait_for_completed()

# 오른쪽으로 90도 회전   E
def rotate_right(robot_group):      
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    time.sleep(0.5)
    robot_group.chassis.move(0, 0, -90, 0, 180).wait_for_completed()

# 왼쪽으로 90도 회전     Q
def rotate_left(robot_group):    
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    time.sleep(0.5)
    robot_group.chassis.move(0, 0, 90, 0, 180).wait_for_completed()

'''################ 짐벌(총) ################'''   #5개   -> 아직 없음

# 아래   
def gimbal_down(robot_group):
    robot_group.gimbal.moveto(-20, 0, 180, 180).wait_for_completed()

# 위
def gimbal_up(robot_group):
    robot_group.gimbal.moveto(20, 0, 180, 180).wait_for_completed()

# 가운데 정렬
def gimbal_recenter(robot_group):
    robot_group.gimbal.moveto(0, 0, 180, 180).wait_for_completed()

# 왼쪽 위로
def gimbal_left_up(robot_group):
    robot_group.gimbal.moveto(30, -90, 100, 100).wait_for_completed()

# 오른쪽 위로
def gimbal_right_up(robot_group):
    robot_group.gimbal.moveto(30, 90, 100, 100).wait_for_completed()

'''################ 집게 ################'''           #7개

# 앞 U 
def arm_forward(robot_group):   
    robot_group.robotic_arm.move(x=90, y=0).wait_for_completed()

# 뒤 J
def arm_backward(robot_group):
    robot_group.robotic_arm.move(x=-90, y=0).wait_for_completed()

# 위 Y
def arm_up(robot_group):
    robot_group.robotic_arm.move(x=0, y=50).wait_for_completed()

# 아래  H
def arm_down(robot_group):
    robot_group.robotic_arm.move(x=0, y=-50).wait_for_completed()
    
# 정렬     
def arm_recenter(robot_group):
    robot_group.robotic_arm.moveto(x=0, y=0).wait_for_completed()
    robot_group.gripper.close(power=50)
    time.sleep(1)
    robot_group.gripper.pause()

# 그리퍼 열기   O
def gripper_open(robot_group):
    robot_group.gripper.open(power=50)
    time.sleep(1)
    robot_group.gripper.pause()

# 그리퍼 닫기  L
def gripper_close(robot_group):
    robot_group.gripper.close(power=50)
    time.sleep(1)
    robot_group.gripper.pause()



''' 메인 코드 '''

if __name__ == '__main__':
    robots_sn_list_gimbal = ['3JKCK6U0030A6U', '3JKCK980030EKR']
    robots_sn_list_gripper = ['3JKCK2S00305WL']   

    multi_robots = multi_robot.MultiEP()
    multi_robots.initialize()

    connected_robots_gimbal = []
    connected_robots_gripper = []

    # 연결 상태 확인 및 그룹 설정
    for idx, sn in enumerate(robots_sn_list_gimbal):
        try:
            if multi_robots.number_id_by_sn([idx, sn]):
                connected_robots_gimbal.append((idx, sn))
        except:
            print(f"Robot with SN {sn} is not connected.")

    for idx, sn in enumerate(robots_sn_list_gripper, start=len(robots_sn_list_gimbal)):
        try:
            if multi_robots.number_id_by_sn([idx, sn]):
                connected_robots_gripper.append((idx, sn))
        except:
            print(f"Robot with SN {sn} is not connected.")

    if not connected_robots_gimbal and not connected_robots_gripper:
        print("No robots are connected.")
        multi_robots.close()
        exit(1)

    print("The number of connected gimbal robots is: {0}".format(len(connected_robots_gimbal)))
    print("The number of connected gripper robots is: {0}".format(len(connected_robots_gripper)))

    gimbal_ids = [idx for idx, sn in connected_robots_gimbal]
    gripper_ids = [idx for idx, sn in connected_robots_gripper]

    robot_group_gimbal = multi_robots.build_group(gimbal_ids)  # gimbal 로봇 그룹
    robot_group_gripper = multi_robots.build_group(gripper_ids)  # gripper 로봇 그룹

    '''# 움직임 설정 (모든 로봇에 적용)
    multi_robots.run([robot_group_gimbal, move_forward], [robot_group_gripper, move_forward])
    multi_robots.run([robot_group_gimbal, move_backward], [robot_group_gripper, move_backward])
    multi_robots.run([robot_group_gimbal, move_left], [robot_group_gripper, move_left])
    multi_robots.run([robot_group_gimbal, move_right], [robot_group_gripper, move_right])
    multi_robots.run([robot_group_gimbal, rotate_right], [robot_group_gripper, rotate_right])
    multi_robots.run([robot_group_gimbal, rotate_left], [robot_group_gripper, rotate_left])

    # gimbal 로봇에만 적용
    multi_robots.run([robot_group_gimbal, gimbal_down])
    multi_robots.run([robot_group_gimbal, gimbal_up])
    multi_robots.run([robot_group_gimbal, gimbal_recenter])
    multi_robots.run([robot_group_gimbal, gimbal_left_up])
    multi_robots.run([robot_group_gimbal, gimbal_right_up])

    # gripper 로봇에만 적용
    multi_robots.run([robot_group_gripper, arm_forward])
    multi_robots.run([robot_group_gripper, arm_backward])
    multi_robots.run([robot_group_gripper, arm_up])
    multi_robots.run([robot_group_gripper, arm_down])
    multi_robots.run([robot_group_gripper, gripper_open])
    multi_robots.run([robot_group_gripper, gripper_close])'''

    multi_robots.run([robot_group_gripper, arm_recenter])

    print("END")
    multi_robots.close()
