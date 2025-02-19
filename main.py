from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

ip_log = {}
ip_log_file = "ip_log.json"
counter_file = "counter.txt"
webhook_file = "resources/discord/webhook"

PROXYCHECK_API_URL = "http://proxycheck.io/v2/{ip}?key={api_key}&vpn=1&asn=1"
API_KEY = "sillers!"

def is_proxy(ip):
    try:
        url = PROXYCHECK_API_URL.format(ip=ip, api_key=API_KEY)
        response = requests.get(url)
        data = response.json()

        if ip in data and data[ip].get("proxy") == "yes":
            print(f"Blocked proxy IP: {ip} (Type: {data[ip].get('type')})")
            return True
    except Exception as e:
        print(f"Error checking proxy status: {e}")
    return False


if not os.path.exists(ip_log_file):
    with open(ip_log_file, "w") as f:
        json.dump({}, f)

if not os.path.exists(counter_file):
    with open(counter_file, "w") as f:
        f.write("0")

def load_ip_log():
    with open(ip_log_file, "r") as f:
        return json.load(f)

def save_ip_log(ip_log):
    with open(ip_log_file, "w") as f:
        json.dump(ip_log, f)

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

    ip_log = load_ip_log()
    if client_ip in ip_log:
        return "Blocked", 403

    if is_proxy(client_ip):
        return jsonify({"error": "Proxy access denied"}), 403  # thank you to "itookashitintheurinal" on discord. ill be adding cloudflare too

    ip_log[client_ip] = True
    save_ip_log(ip_log)


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
    app.run(host="127.0.0.1", port=5000)
