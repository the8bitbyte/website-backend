from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

with open(resources/discord/webhook_url, "r") as file:
    WEBHOOK_URL = file.read().strip()

IP_DATA_FILE = "ip_data.txt"
COUNTER_FILE = "counter.txt"

if os.path.exists(IP_DATA_FILE):
    with open(IP_DATA_FILE, "r") as f:
        ip_data = set(f.read().splitlines())
else:
    ip_data = set()

if os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "r") as f:
        counter = int(f.read().strip())
else:
    counter = 0

def save_data():
    """Save IP data and counter to files."""
    with open(IP_DATA_FILE, "w") as f:
        f.write("\n".join(ip_data))
    with open(COUNTER_FILE, "w") as f:
        f.write(str(counter))

@app.route("/", methods=["POST", "GET"])
def handle_request():
    global counter
    client_ip = request.remote_addr

    if client_ip in ip_data:
        return jsonify({"message": "Request blocked", "reason": "IP already sent a request"}), 403

    ip_data.add(client_ip)
    counter += 1
    save_data()

    webhook_message = {
        "content": f"New visitor at tainted-purity.rip. Total unique requests: {counter}."
    }
    try:
        requests.post(WEBHOOK_URL, json=webhook_message)
    except Exception as e:
        return jsonify({"message": "Failed to send webhook", "error": str(e)}), 500

    return jsonify({"message": "Request successful", "unique_requests": counter})

@app.route("/counter", methods=["GET"])
def get_counter():
    """Allow clients to request the current counter value."""
    return jsonify({"current_counter": counter})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
