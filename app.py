# app.py
import logging
import os
from flask import Flask
from flask_cors import CORS
from routes.control import control_bp
from routes.button import button_bp
from routes.video import video_bp
from routes.connect import connect_bp
from camera.stream import CameraStream
from routes.autograsp import autograsp_bp
from routes.avoidance import avoidacne_bp


logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
app = Flask(__name__)
CORS(app)

camera = CameraStream()

app.register_blueprint(control_bp)
app.register_blueprint(button_bp)
app.register_blueprint(video_bp)
app.register_blueprint(connect_bp)
app.register_blueprint(autograsp_bp)
app.register_blueprint(avoidacne_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3160, debug=True ,use_reloader=False)
