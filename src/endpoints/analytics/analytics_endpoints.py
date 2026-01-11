from flask import Blueprint, jsonify
from datetime import datetime
import random

analytics_bp = Blueprint('analytics', __name__)

# Mock Data for Analytics
def get_mock_paths_data():
    return [
        {"path_id": "path_A1", "latency_ms": random.randint(20, 100), "packet_loss_percent": random.uniform(0, 1)},
        {"path_id": "path_A2", "latency_ms": random.randint(25, 120), "packet_loss_percent": random.uniform(0, 2)},
        {"path_id": "path_S1", "latency_ms": random.randint(15, 80), "packet_loss_percent": 0.0},
    ]

def get_mock_threats_data():
    return [
        {"timestamp": datetime.utcnow().isoformat(), "source_ip": "192.168.1.105", "event": "Failed Auth Attempt", "severity": "Medium"},
        {"timestamp": datetime.utcnow().isoformat(), "source_ip": "10.0.0.45", "event": "Integrity Check Fail", "severity": "High"},
    ]

@analytics_bp.route('/api/v1/analytics/paths', methods=['GET'])
def get_paths():
    """
    View real-time latency and packet loss per transmission path.
    """
    return jsonify({
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "data": get_mock_paths_data()
    }), 200

@analytics_bp.route('/api/v1/analytics/threats', methods=['GET'])
def get_threats():
    """
    Retrieve logs of failed reassembly attempts (potential attacks).
    """
    return jsonify({
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "logs": get_mock_threats_data()
    }), 200
