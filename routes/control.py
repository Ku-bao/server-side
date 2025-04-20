import common.mecanum as mecanum

import logging
from flask import Blueprint, request, jsonify
import logging
import  math


control_bp = Blueprint('control', __name__)
logger = logging.getLogger(__name__)

@control_bp.route("/control", methods=["POST"])
def handle_control():
    try:
        data = request.get_json()
        logger.info(f"收到控制数据: {data}")
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        x = data.get('x', 0.0)
        y = data.get('y', 0.0)
        speed = data.get('speed', 1.0)
        y = - y
        angle_rad = math.atan2(y, x)
        angle_deg = math.degrees(angle_rad)
        if angle_deg <= 0:
            angle_deg = 360 + angle_deg
        if angle_deg == 360:
            angle_deg = 0
        if x == 0 and y == 0:
            chassis.set_velocity(0, 0, 0)
        else:
            chassis.set_velocity(50,angle_rad,0)

        logger.info(f"控制命令 - x: {x}, y: {y}, speed: {speed}, angle: {angle_deg}")

        return jsonify({'status': 'success', 'angle': angle_deg})
    except Exception as e:
        logger.error(f"控制处理出错: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


