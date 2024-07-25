import time
from multi_robomaster import multi_robot


# 앞으로 전진
def move_forward(robot_group):
    robot_group.chassis.move(0.5, 0, 0, 1).wait_for_completed()

def rotate_right(robot_group):
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    time.sleep(0.5)
    robot_group.chassis.move(0, 0, -90, 0, 180).wait_for_completed()


def rotate_left(robot_group):
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    time.sleep(0.5)
    robot_group.chassis.move(0, 0, 90, 0, 180).wait_for_completed()


if __name__ == '__main__':
    
    robots_sn_list = ['3JKCK2S00305WL', '3JKCK980030EKR', '3JKCK6U0030A6U'] 
        
    multi_robots = multi_robot.MultiEP()
    multi_robots.initialize()
    number = multi_robots.number_id_by_sn([0, robots_sn_list[0]], [1, robots_sn_list[1]], [2, robots_sn_list[2]] )
    
    print("The number of robot is: {0}".format(number))

    robot_group = multi_robots.build_group([0, 1, 2]) # 전체 
    robot_group1 = multi_robots.build_group([0])   # 집게
    robot_group2 = multi_robots.build_group([1, 2])   # 총
    
    #multi_robots.run([robot_group, group_task])
    #multi_robots.run([robot_group1, group_task1])
    
    # 움직임 설정
    multi_robots.run([robot_group, move_forward])
    multi_robots.run([robot_group, rotate_right])
    multi_robots.run([robot_group, rotate_left])
    
    
    
    
    
    
    
    print("END")
    multi_robots.close()