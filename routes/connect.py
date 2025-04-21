from flask import Blueprint, request, jsonify
import logging

connect_bp = Blueprint('connect', __name__)
logger = logging.getLogger(__name__)

@connect_bp.route('/ping', methods=['GET'])
def ping():
    """健康检查端点"""
    return jsonify({'status': 'success', 'message': 'pong'}), 200
