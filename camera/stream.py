import cv2
import threading
import time
import subprocess
import os
class CameraStream:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print("[CameraStream] 创建实例")
                    cls._instance = super(CameraStream, cls).__new__(cls)
                    cls._instance.__init_once()
        return cls._instance

    def __init_once(self):
        print("[CameraStream] 初始化摄像头")
        print("[CameraStream] 检查摄像头是否被占用...")
        res = subprocess.getoutput("lsof /dev/video0")
        print(res or "没有其他进程占用 /dev/video0")

        self.capture = None
        self.running = False
        self.lock = threading.Lock()
        self.read_thread = None
        self.latest_frame = None
        self.start()

    def _reader(self):
        print("[CameraStream] 读取线程已启动")
        failure_count = 0
        while self.running and self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if not ret:
                failure_count += 1
                print(f"[CameraStream] 读取失败 {failure_count} 次")
                if failure_count > 10:
                    print("[CameraStream] 连续失败超过限制，自动重启")
                    self.restart()
                    break
                time.sleep(0.01)
                continue

            failure_count = 0
            _, buffer = cv2.imencode('.jpg', frame)
            self.latest_frame = buffer.tobytes()

        print("[CameraStream] 读取线程结束")

    def start(self):
        with self.lock:
            if not self.running:
                print("[CameraStream] 启动摄像头")
                self.capture = cv2.VideoCapture(0)
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
                if not self.capture.isOpened():
                    print("[CameraStream] 摄像头打开失败")
                self.running = True
                self.read_thread = threading.Thread(target=self._reader, daemon=True)
                self.read_thread.start()

    def stop(self):
        with self.lock:
            print("[CameraStream] 停止摄像头")
            self.running = False
            if self.capture:
                self.capture.release()
                self.capture = None

    def restart(self):
        self.stop()
        time.sleep(0.5)
        self.start()

    def frames(self):
        print("[CameraStream] 开始传输帧")
        while self.running:
            if self.latest_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + self.latest_frame + b'\r\n')
            else:
                time.sleep(0.05)
        print("[CameraStream] 停止传输帧")
