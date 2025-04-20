from flask import Blueprint, Response, jsonify, request
from camera.stream import CameraStream
import logging
import time
import threading
video_bp = Blueprint('video', __name__)
logger = logging.getLogger(__name__)
camera = CameraStream()

active_clients = 0
client_lock = threading.Lock()

@video_bp.route("/video")
def video_feed():
    global active_clients
    try:
        camera.start(False)
        client_ip = request.remote_addr
        with client_lock:
            active_clients += 1
        print(f"[/video] 收到来自 {client_ip} 的请求，当前连接数: {active_clients}")

        def generate():
            global active_clients  
            try:
                for frame in camera.frames():  # 不做YOLO检测
                    yield frame
            except GeneratorExit:
                print(f"[/video] 客户端 {client_ip} 断开连接")
            finally:
                with client_lock:
                    active_clients -= 1
                print(f"[/video] 当前剩余连接数: {active_clients}")

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logger.exception("视频开启失败")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@video_bp.route("/detection_video")
def detection_video_feed():
    global active_clients
    try:
        camera.start(True)
        client_ip = request.remote_addr
        with client_lock:
            active_clients += 1
        print(f"[/detection_video] 收到来自 {client_ip} 的请求，当前连接数: {active_clients}")

        def generate():
            global active_clients  
            try:
                for frame in camera.frames():  
                    yield frame
            except GeneratorExit:
                print(f"[/detection_video] 客户端 {client_ip} 断开连接")
            finally:
                with client_lock:
                    active_clients -= 1
                print(f"[/detection_video] 当前剩余连接数: {active_clients}")

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logger.exception("视频开启失败")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@video_bp.route("/stopVideo")
def stop_video():
    try:
        camera.stop()
        logger.info("摄像头已停止")
        return jsonify({'status': 'success', 'message': 'Video stopped'})
    except Exception as e:
        logger.error(f"视频停止失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
