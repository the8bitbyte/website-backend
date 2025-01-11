from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ip_log = {}
counter_file = "counter.txt"
webhook_file = "resources/discord/webhook"

if not os.path.exists(counter_file):
    with open(counter_file, "w") as f:
        f.write("0")

def read_counter():
    with open(counter_file, "r") as f:
        return int(f.read())

def update_counter(value):
    with open(counter_file, "w") as f:
        f.write(str(value))

def read_webhook():
    if not os.path.exists(webhook_file):
        print("yap")
    with open(webhook_file, "r") as f:
        return f.read().strip()

def send(counter):
    webhook_url = read_webhook()
    message = {
        "content": f"New visitor. current counter value: {counter}"
    }
    try:
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
        print("webhook sent")
    except requests.exceptions.RequestException as e:
        print(f"error sending webhook: {e}")
@app.route("/", methods=["POST"])
def log_ip():
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    if client_ip in ip_log:
        return "Blocked", 403

    ip_log[client_ip] = True
    counter = read_counter()
    counter += 1
    update_counter(counter)

    send(counter)

    print(f"Logged IP: {client_ip}, Counter: {counter}")
    return "Logged", 200

@app.route("/counter", methods=["GET"])
def get_counter():
    counter = read_counter()
    return jsonify({"current_counter": counter})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
