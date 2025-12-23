import requests
import socket

def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def probe_http(url):
    try:
        print(f"Probing {url}...")
        resp = requests.get(url, timeout=5)
        print(f"Status: {resp.status_code}")
        print(f"Content: {resp.text[:200]}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

print("--- GOLOGIN DIAGNOSTIC ---")

# 1. Check if port is open via Socket
port_open = check_port('127.0.0.1', 36912)
print(f"Port 36912 (127.0.0.1) open: {port_open}")

if port_open:
    # 2. Probe commonly used endpoints
    probe_http('http://127.0.0.1:36912')
    probe_http('http://127.0.0.1:36912/browser/start')
    probe_http('http://127.0.0.1:36912/api/v1/profile/start')
else:
    print("Port 36912 seems closed via socket connect.")

print("\n--------------------------")
