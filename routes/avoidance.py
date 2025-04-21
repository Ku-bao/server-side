#!/usr/bin/python3
#coding=utf8
import sys
sys.path.append('/home/pi/MasterPi')
import cv2
import time
import signal
import Camera
import numpy as np
import pandas as pd
import common.sonar as Sonar
import common.mecanum as mecanum
from kinematics.transform import *
from kinematics.arm_move_ik import *
from common.ros_robot_controller_sdk import Board
from flask import Blueprint, request, jsonify
import logging

avoidacne_bp = Blueprint('avoidance', __name__)
logger = logging.getLogger(__name__)

AK = ArmIK()
board = Board()
car = mecanum.MecanumChassis()

HWSONAR = None
Threshold = 30.0
TextColor = (0, 255, 255)
TextSize = 12

speed = 40
__isRunning = False
__until = 0


# 夹持器夹取时闭合的角度(the closing angle of the gripper while grasping an object)
servo1 = 1500

# 初始位置(initial position)
def initMove():
    car.set_velocity(0,0,0)
    board.pwm_servo_set_position(0.3, [[1, servo1]])
    # AK.setPitchRangeMoving((0, 6, 18), 0,-90, 90,1500)

# 变量重置(reset variables)
def reset():
    global __isRunning
    global Threshold
    global speed
    global stopMotor
    global turn
    global forward
    global old_speed
    
    speed = 40
    old_speed = 0
    Threshold = 30.0
    turn = True
    forward = True
    stopMotor = True
    __isRunning = False
    
# app初始化调用(call the initialization of the app)
def init():
    print("Avoidance Init")
    initMove()
    reset()
    
__isRunning = False
# app开始玩法调用(the app starts the game calling)
def start():
    global __isRunning
    global stopMotor
    global forward
    global turn
    
    turn = True
    forward = True
    stopMotor = True
    __isRunning = True
    print("Avoidance Start")

# app停止玩法调用(the app stops the game calling)
def stop():
    global __isRunning
    __isRunning = False
    car.set_velocity(0,0,0)
    print("Avoidance Stop")

# app退出玩法调用(the app exits the game calling)
def exit():
    global __isRunning
    __isRunning = False
    car.set_velocity(0,0,0)
    HWSONAR.setPixelColor(0, (0, 0, 0))
    HWSONAR.setPixelColor(1, (0, 0, 0))
    print("Avoidance Exit")

# 设置避障速度(set the speed of obstacle avoidance)
def setSpeed(args):
    global speed
    speed = int(args[0])
    return (True, ())
 
# 设置避障阈值(set the threshold of obstacle avoidance)
def setThreshold(args):
    global Threshold
    Threshold = args[0]
    return (True, (Threshold,))

# 获取当前避障阈值(obtain current threshold of obstacle avoidance)
def getThreshold(args):
    global Threshold
    return (True, (Threshold,))


turn = True
forward = True
old_speed = 0
stopMotor = True
distance_data = []

def run():
    global turn
    global speed
    global __until
    global __isRunning
    global HWSONAR
    global Threshold
    global distance_data
    global stopMotor
    global forward
    global old_speed
    
    dist = HWSONAR.getDistance() / 10.0

    distance_data.append(dist)
    data = pd.DataFrame(distance_data)
    data_ = data.copy()
    u = data_.mean()  # 计算均值(calculate the mean)
    std = data_.std()  # 计算标准差(calculate the standard deviation）

    data_c = data[np.abs(data - u) <= std]
    distance = data_c.mean()[0]

    if len(distance_data) == 5:
        distance_data.remove(distance_data[0])

    if __isRunning:   
        if speed != old_speed:   # 同样的速度值只设置一次 (set the same speed value only once)
            old_speed = speed
            car.set_velocity(speed,90,0)
            
        if distance <= Threshold:   # 检测是否达到距离阈值(detect whether the distance threshold has been reached)
            if turn:
                turn = False
                forward = True
                stopMotor = True
                car.set_velocity(0,90,-0.5)
                time.sleep(0.5)
            
        else:
            if forward:
                turn = True
                forward = False
                stopMotor = True
                car.set_velocity(speed,90,0)
    else:
        if stopMotor:
            stopMotor = False
            car.set_velocity(0,0,0)  # 关闭所有电机(close all motors)
        turn = True
        forward = True
        time.sleep(0.03)
    # return cv2.putText(img, "Dist:%.1fcm"%distance, (30, 480-30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, TextColor, 2)  # 把超声波测距值打印在画面上


#关闭前处理(process before closing)
def Stop(signum, frame):
    global __isRunning
    
    __isRunning = False
    print('关闭中...')
    car.set_velocity(0,0,0)  # 关闭所有电机(close all motors)


@avoidacne_bp.route('/avoidance', methods=['POST'])
def avoidance_handle():
    global HWSONAR
    init()
    start()
    HWSONAR = Sonar.Sonar()
    signal.signal(signal.SIGINT, Stop)
    # #cap = cv2.VideoCapture('http://127.0.0.1:8080?action=stream')
    # cap = cv2.VideoCapture(0)
    while __isRunning:
        run()  

@avoidacne_bp.route('/stopAvoidance', methods=['POST'])
def avoidance_stop_handle():
    exit()