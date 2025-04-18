from flask import Blueprint, request, jsonify
import common.mecanum as mecanum
from routes.roboticarm import grasp, headDown, headUp, headDownDown
import logging

chassis = mecanum.MecanumChassis()

button_bp = Blueprint('button', __name__)
logger = logging.getLogger(__name__)

@button_bp.route("/button", methods=["POST"])
def handle_button():
    try:
        data = request.get_json()
        logger.info(f"收到按钮命令: {data}")
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        button_id = data.get('button_id')
        action = data.get('button_action', True)

        logger.info(f"按钮 - ID: {button_id}, 动作: {action}")

        # === 匹配前端的按钮 ID 并处理对应逻辑 ===
        if button_id == "button_model1":
            logger.info("切换模型1")
            headUp()

        elif button_id == "button_model2":
            logger.info("切换模型2")
            headDown()

        elif button_id == "button_model3":
            logger.info("切换模型3")
            headDownDown()

        elif button_id == "button_left":
            logger.info("左转")
            chassis.set_velocity(0,90,-0.3)

        elif button_id == "button_right":
            logger.info("右转")
            chassis.set_velocity(0,90,0.3)

        elif button_id == "button_grasp":
            logger.info("执行抓取操作")
            grasp()

        elif button_id == "detect":
            logger.info(f"{'开启' if action else '关闭'}识别")


        elif button_id == "auto_grasp":
            logger.info(f"{'开启' if action else '关闭'}自动识别抓取")


        else:
            logger.warning(f"未知按钮 ID: {button_id}")
            return jsonify({'status': 'error', 'message': 'Unknown button ID'}), 400

        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"按钮处理出错: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
