from flask import Flask, render_template
from flask_socketio import SocketIO
import psutil
import subprocess
import time

app = Flask(__name__)
socketio = SocketIO(app)

prev_net = {"bytes_sent": 0, "bytes_recv": 0, "timestamp": time.time()}

def get_drive_temp_and_usage(drive=None):
    # Only works on Linux (Raspberry Pi OS Lite)
    import os
    temp = "N/A"
    usage = "N/A"
    # Try to get drive temperature using smartctl (if available)
    if drive is not None and os.name == "posix":
        try:
            result = subprocess.run(
                ["smartctl", "-A", drive],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            for line in result.stdout.splitlines():
                if (
                    "Airflow_Temperature_Cel" in line or
                    "Temperature_Internal" in line or
                    "Drive Temperature" in line
                ):
                    parts = line.split()
                    for part in reversed(parts):
                        if part.isdigit():
                            temp = part
                            break
                    break
        except Exception:
            temp = "N/A"
    return temp

def get_network_speeds():
    global prev_net
    counters = psutil.net_io_counters()
    now = time.time()
    elapsed = now - prev_net["timestamp"] if prev_net["timestamp"] else 1
    upload_speed = (counters.bytes_sent - prev_net["bytes_sent"]) / elapsed
    download_speed = (counters.bytes_recv - prev_net["bytes_recv"]) / elapsed
    prev_net = {
        "bytes_sent": counters.bytes_sent,
        "bytes_recv": counters.bytes_recv,
        "timestamp": now
    }
    return upload_speed, download_speed

def get_stats():
    temperatures = psutil.sensors_temperatures().get('cpu_thermal', [])
    cpu_temp = temperatures[0].current if temperatures else 'N/A'
    # Try to find a non-system drive (not C:) for Windows
    drive_letter = "/dev/sda"
    drive_temp = get_drive_temp_and_usage(drive_letter)
    upload_speed, download_speed = get_network_speeds()
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "temperature": f"{cpu_temp:.2f}" if isinstance(cpu_temp, (int, float)) else cpu_temp,
        "drive_temperature": drive_temp,
        "upload_speed": f"{upload_speed/1024:.2f} KB/s" if upload_speed < 1048576 else f"{upload_speed/1048576:.2f} MB/s",
        "download_speed": f"{download_speed/1024:.2f} KB/s" if download_speed < 1048576 else f"{download_speed/1048576:.2f} MB/s"
    }

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@socketio.on("request_stats")
def send_stats():
    stats = get_stats()
    socketio.emit("update_stats", stats)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)