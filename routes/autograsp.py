import common.mecanum as mecanum

import logging
from flask import Blueprint, request, jsonify
import logging
import  math
from kinematics.arm_move_ik import *
from common.ros_robot_controller_sdk import Board
import common.yaml_handle as yaml_handle


connect_bp = Blueprint('autograsp', __name__)
logger = logging.getLogger(__name__)

board = Board()
deviation_data = yaml_handle.get_yaml_data(yaml_handle.Deviation_file_path)
chassis = mecanum.MecanumChassis()

AK = ArmIK()
AK.board = Board()

@connect_bp.route('/autoGrasp', methods=['POST'])
def auto_move():
    try:
        data = request.get_json()
        logger.info(f"收到控制数据: {data}")
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        x = data.get('x', 0.0)
        y = data.get('y', 0.0)
        z = data.get('z', 0.0)
        distance = data.get('distance', 0.0)
        angle = data.get('angle', 0)
        action = data.get('action', True)
        logger.info(f"控制命令 - x: {x}, y: {y}, z: {z}, diatance: {distance}, angle: {angle_deg}, action:{action}")

        move_and_rotate(distance, angle, x, y, z)

        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"控制处理出错: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 移动 x 厘米
def move_forward(x: float):
    # 假设线速度为50，小车前进的时间为距离 / 速度
    # 需要根据实际情况调整时间（根据小车实际速度和性能）
    velocity = 50  # 线速度（可以根据需要调整）
    time = x / velocity  # 移动时间 = 距离 / 速度
    
    # 设置线速度为50，方向角为0（前进方向），偏航角速度为0（不旋转）
    chassis.set_velocity(velocity, 0, 0)  # 设置前进
    time.sleep(time)  # 让小车前进所需时间
    
    # 停止前进
    chassis.set_velocity(0, 0, 0)

# 顺时针旋转 y 度
def rotate(y: float):
    # 偏航角速度控制顺时针旋转
    angular_velocity = 1  # 偏航角速度，数值可以根据需要调整
    time_to_rotate = y / angular_velocity  # 旋转时间 = 角度 / 角速度
    
    # 设置线速度为0（停止前进），方向角为0（不改变方向），偏航角速度为正（顺时针）
    chassis.set_velocity(0, 0, angular_velocity)  # 顺时针旋转
    time.sleep(time_to_rotate)  # 让小车旋转所需时间
    
    # 停止旋转
    chassis.set_velocity(0, 0, 0)

def grasp(x, y, z):
    board.pwm_servo_set_position(0.3, [[1, 2000]]) 
    # AK.setPitchRangeMoving((0, 6, 18), 0,-90, 90, 1500) 
    # AK.setPitchRangeMoving((0, 9, 10), 0,-90, 90, 1500) 
    # time.sleep(1) 
    AK.setPitchRangeMoving((x, y, z), -90, -180, 90, 1500) 
    time.sleep(2)
    board.pwm_servo_set_position(0.3, [[1, 1500]]) 
    time.sleep(0.5)
    # AK.setPitchRangeMoving((0, 6, 18), 0,-90, 90, 1500) 
    AK.setPitchRangeMoving((0, 9, 10), 0,-90, 90, 1500) 
    time.sleep(1.5) 

# 移动 x 厘米并旋转 y 度
def move_and_rotate_and_grasp(distance: float, angle: int, x: float, y:float, z:float):
    move_forward(distance)  # 前进 x 厘米
    rotate(angle)  # 顺时针旋转 y 度
    grasp(x, y, z)

