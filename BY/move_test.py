import time
from multi_robomaster import multi_robot
from robomaster import led, blaster


ROBOTS_NUM = 3
DISTANCE_BY_SITE = 0.3


def reset_task(robot_group):
    """初始自由模式 & 关掉所有灯效"""
    robot_group.led.set_led(led.COMP_ALL, 255, 1, 1, led.EFFECT_OFF)
    robot_group.set_group_robots_mode(multi_robot.FREE_MODE)
    robot_group.led.set_led(led.COMP_ALL, 1, 255, 1, led.EFFECT_FLASH)
    # 目前只有步兵车，可以这样用
    robot_group.gimbal.moveto(0, 0, 180, 180).wait_for_completed()
    robot_group.led.set_led(led.COMP_ALL, 255, 1, 1, led.EFFECT_OFF)


def ep_arm_initial_pos(robot_group):
    """ep_arm 初始云台位置"""
    robot_group.gimbal.moveto(0, 0, 180, 180).wait_for_completed()
    robot_group.gimbal.moveto(-20, 0, 100, 100).wait_for_completed()


def ep_gimbal_initial_pos(robot_group):
    """ep_gimbal 初始云台位置"""
    robot_group.gimbal.moveto(0, 0, 180, 180).wait_for_completed()
    robot_group.gimbal.moveto(-20, 0, 100, 100).wait_for_completed()


def light_order(robot_group):
    """组内小车灯依次亮起,云台依次抬起"""
    media_sound_solmization_1a = 0x110
    music_note = media_sound_solmization_1a
    count = 0
    for robot_id in robot_group._robots_id_in_group_list:
        count += 1
        robot_obj = robot_group.get_robot(robot_id)
        # robot_obj.play_sound(music_note).wait_for_completed(0.5)
        # 音符的编码顺序为 1A -> 1ASharp -> 1B -> 1BSharp... ，因此每次要移动两个编码才能到下一个音符
        music_note += 2
        robot_obj.blaster.fire(fire_type='water', times=1)
        if count & 0x01:
            robot_obj.led.set_led(led.COMP_ALL, 255, 1, 1, led.EFFECT_ON)
            robot_obj.gimbal.moveto(0, 0, 180, 180).wait_for_completed()
        else:
            robot_obj.led.set_led(led.COMP_ALL, 75, 255, 255, led.EFFECT_ON)
            robot_obj.gimbal.moveto(0, 0, 180, 180).wait_for_completed()
        time.sleep(0.5)


def move_forward(robot_group):
    """全体前进"""
    robot_group.chassis.move(0.5, 0, 0, 1).wait_for_completed()


def rotate_right(robot_group):
    """底盘右转"""
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    time.sleep(0.5)
    robot_group.chassis.move(0, 0, -90, 0, 180).wait_for_completed()


def rotate_left(robot_group):
    """底盘左转"""
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    time.sleep(0.5)
    robot_group.chassis.move(0, 0, 90, 0, 180).wait_for_completed()


def rotate_dance(robot_group):
    """底盘solo舞蹈"""
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    robot_group.chassis.move(0.2, 0, 0, 1).wait_for_completed()
    robot_group.chassis.move(0, 0, 45, 0, 180).wait_for_completed()
    robot_group.chassis.move(0, 0, -90, 0, 180).wait_for_completed()
    robot_group.chassis.move(0, 0, 45, 0, 180).wait_for_completed()
    robot_group.chassis.move(0, 0, 360, 0, 180).wait_for_completed()


def move_backward(robot_group):
    """底盘后移"""
    robot_group.chassis.move(-DISTANCE_BY_SITE, 0, 0, 1, 0).wait_for_completed()


def led_red_blink(robot_group):
    """红灯闪烁"""
    robot_group.led.set_led(led.COMP_ALL, 255, 1, 1, led.EFFECT_FLASH)


def led_grey_blink(robot_group):
    """grey闪烁"""
    robot_group.led.set_led(led.COMP_ALL, 75, 255, 255, led.EFFECT_FLASH)


def led_red_solid(robot_group):
    """红灯常亮"""
    robot_group.led.set_led(led.COMP_ALL, 255, 1, 1, led.EFFECT_ON)


def led_grey_solid(robot_group):
    """grey常亮"""
    robot_group.led.set_led(led.COMP_ALL, 75, 255, 255, led.EFFECT_ON)


def move_left(robot_group):
    """底盘左移"""
    robot_group.chassis.move(0, 0.6, 0, 2, 0).wait_for_completed()


def move_right(robot_group):
    """底盘右移"""
    robot_group.chassis.move(0, -0.6, 0, 2, 0).wait_for_completed()


def gimbal_down(robot_group):
    """云台下垂"""
    robot_group.gimbal.moveto(-20, 0, 180, 180).wait_for_completed()


def gimbal_recenter(robot_group):
    """云台回中"""
    robot_group.gimbal.moveto(0, 0, 180, 180).wait_for_completed()


def rotate_circle_right(robot_group):
    """顺时针转圈"""
    robot_group.chassis.move(0, 0, 360, 0, 360).wait_for_completed()


def rotate_circle_left(robot_group):
    """逆时针转圈"""
    robot_group.chassis.move(0, 0, -360, 0, 360).wait_for_completed()


def rotate_right_dance(robot_group):
    """右转"""
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    robot_group.chassis.move(0, 0, -90, 0, 180).wait_for_completed()
    robot_group.gimbal.moveto(-20, 0, 100, 100).wait_for_completed()


def rotate_left_dance(robot_group):
    """左转"""
    robot_group.set_group_robots_mode(multi_robot.CHASSIS_LEAD_MODE)
    robot_group.chassis.move(0, 0, 90, 0, 180).wait_for_completed()
    robot_group.gimbal.moveto(-20, 0, 100, 100).wait_for_completed()


def gimbal_left_up(robot_group):
    """云台左转，并抬起"""
    robot_group.set_group_robots_mode(multi_robot.FREE_MODE)
    robot_group.gimbal.moveto(30, 90, 100, 100).wait_for_completed()


def gimbal_right_up(robot_group):
    """云台右转,并抬起"""
    robot_group.set_group_robots_mode(multi_robot.FREE_MODE)
    robot_group.gimbal.moveto(30, -90, 100, 100).wait_for_completed()


def ending_formation(robot_group):
    """结束队形"""
    robot_group.blaster.fire(blaster.WATER_FIRE, 3)
    time.sleep(2)
    robot_group.gimbal.moveto(20, 0, 100, 100).wait_for_completed()
    # 连续执行三次点头动作
    for count in range(3):
        robot_group.gimbal.move(-20, 0, 150, 150).wait_for_completed()
        robot_group.gimbal.move(20, 0, 150, 150).wait_for_completed()
    # 低头，熄灯，落幕
    robot_group.gimbal.moveto(-20, 0, 100, 100).wait_for_completed()
    robot_group.led.set_led(led.COMP_ALL, 255, 1, 1, led.EFFECT_OFF)


def nod_action(robot_group):
    """云台做点头动作"""
    # sound_action = robot_group.play_sound(define.SOUND_ID_ATTACK, 3)
    robot_group.gimbal.moveto(-20, 0, 100, 100).wait_for_completed()
    robot_group.gimbal.moveto(0, 0, 100, 100).wait_for_completed()


if __name__ == '__main__':
    robots_sn_list = ['3JKCK2S00305WL', '3JKCK980030EKR']   #3JKCK980030EKR   3JKCK6U0030A6U
 
    multi_robots = multi_robot.MultiEP()
    multi_robots.initialize()
    number = multi_robots.number_id_by_sn([0, robots_sn_list[0]], [1, robots_sn_list[1]])
    
    print("The number of robot is: {0}".format(number))
    
    
    robot_group_all = multi_robots.build_group([0, 1])
        
    robot_group_ep_arm = multi_robots.build_group([0])       # 집게
    robot_group_ep_gimbal = multi_robots.build_group([1])    # 총

    
    
    
    
    # 初始摆放，云台向左，云台向右，依次摆放
    multi_robots.run([robot_group_all, reset_task])
    multi_robots.run([robot_group_ep_gimbal, ep_gimbal_initial_pos], [robot_group_ep_arm, ep_arm_initial_pos])
    # 依次点亮灯，抬起云台
    multi_robots.run([robot_group_all, light_order])
    # 两组向两面散开
    multi_robots.run([robot_group_all, move_forward])
    # 面向观众
    multi_robots.run([robot_group_ep_gimbal, rotate_left], [robot_group_ep_arm, rotate_right])
    # 两边对齐
    multi_robots.run([robot_group_ep_gimbal, move_backward])
    # 灯效闪烁
    multi_robots.run([robot_group_ep_gimbal, led_red_blink], [robot_group_ep_arm, led_grey_blink])
    # 两边转头面向对方
    multi_robots.run([robot_group_ep_gimbal, rotate_left], [robot_group_ep_arm, rotate_right])
    
    # 点头
    multi_robots.run([robot_group_ep_arm, nod_action])
    
    # 步兵点头
    multi_robots.run([robot_group_ep_gimbal, nod_action])
    # 面向观众
    multi_robots.run([robot_group_ep_gimbal, rotate_right], [robot_group_ep_arm, rotate_left])
    # 灯效
    multi_robots.run([robot_group_ep_gimbal, led_red_solid], [robot_group_ep_arm, led_grey_solid])
    # 两边左右旋转
    multi_robots.run([robot_group_ep_gimbal, rotate_right], [robot_group_ep_arm, rotate_left])
    multi_robots.run([robot_group_ep_gimbal, rotate_left], [robot_group_ep_arm, rotate_right])
    multi_robots.run([robot_group_ep_gimbal, rotate_circle_right], [robot_group_ep_arm, rotate_circle_left])
    multi_robots.run([robot_group_ep_gimbal, rotate_circle_left], [robot_group_ep_arm, rotate_circle_right])
    # 结束队形,对天空放礼炮->
    multi_robots.run([robot_group_ep_gimbal, gimbal_right_up], [robot_group_ep_arm, gimbal_left_up])
    multi_robots.run([robot_group_all, ending_formation])

    print("Game over")