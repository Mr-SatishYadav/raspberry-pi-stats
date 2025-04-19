from flask import Flask, render_template
from flask_socketio import SocketIO
import psutil

app = Flask(__name__)
socketio = SocketIO(app)

def get_stats():
    temperatures = psutil.sensors_temperatures().get('cpu_thermal', [])
    cpu_temp = temperatures[0].current if temperatures else 'N/A'
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "temperature": f"{cpu_temp:.2f}" if isinstance(cpu_temp, (int, float)) else cpu_temp
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