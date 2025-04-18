#!/usr/bin/env python3
# encoding:utf-8
import sys
import time
from kinematics.arm_move_ik import *
from common.ros_robot_controller_sdk import Board
import common.yaml_handle as yaml_handle

board = Board()
deviation_data = yaml_handle.get_yaml_data(yaml_handle.Deviation_file_path)

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
    
# 实例化逆运动学库(Instantiate the inverse kinematics library)
AK = ArmIK()
AK.board = Board()

def grasp():
    board.pwm_servo_set_position(0.3, [[1, 2000]]) 
    # AK.setPitchRangeMoving((0, 6, 18), 0,-90, 90, 1500) 
    # AK.setPitchRangeMoving((0, 9, 10), 0,-90, 90, 1500) 
    # time.sleep(1) 
    AK.setPitchRangeMoving((0, 10.8, -5), -90, -180, 90, 1500) 
    time.sleep(2)
    board.pwm_servo_set_position(0.3, [[1, 1500]]) 
    time.sleep(0.5)
    # AK.setPitchRangeMoving((0, 6, 18), 0,-90, 90, 1500) 
    AK.setPitchRangeMoving((0, 9, 10), 0,-90, 90, 1500) 
    time.sleep(1.5) 

def headUp():
    AK.setPitchRangeMoving((0, 6, 18), 0,-90, 90, 1500)

def headDown():
    AK.setPitchRangeMoving((0, 9, 10), 0,-90, 90, 1500)

def headDownDown():
    AK.setPitchRangeMoving((0, 12, 4), 0,-90, 90, 1500)

if __name__ == "__main__":
    AK.setPitchRangeMoving((0, 12, 4), 0,-90, 90, 1500)
    