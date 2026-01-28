import socket
import struct
import time
import threading
import random
import math

# ================= CONFIGURATION =================
SERVER_IP = '122.155.175.199'
SERVER_PORT = 5027
DEVICE_COUNT = 200
SEND_INTERVAL = 29  # ⏱️ Edit to 30s as per requirement
# =================================================

# Zones
HUBS_NORTH = [(18.7883, 98.9853), (19.9105, 99.8406), (18.7832, 100.7926), (16.8211, 100.2659)]
HUBS_CENTRAL = [(13.7563, 100.5018), (13.3611, 100.9847), (14.3532, 100.5684), (12.6114, 102.1039)]
HUBS_SOUTH = [(7.8804, 98.3923), (9.1389, 99.3226), (7.0058, 100.4681), (8.0863, 98.9063)]

def get_hub_by_index(index):
    if 1 <= index <= 70: return random.choice(HUBS_NORTH), HUBS_NORTH
    elif 71 <= index <= 140: return random.choice(HUBS_CENTRAL), HUBS_CENTRAL
    else: return random.choice(HUBS_SOUTH), HUBS_SOUTH

def crc16_arc(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if (crc & 1): crc = (crc >> 1) ^ 0xA001
            else: crc >>= 1
    return crc

def build_avl_packet(lat, lon, speed, course, odometer):
    timestamp = int(time.time() * 1000)
    lat_int, lon_int = int(lat * 10000000), int(lon * 10000000)

    avl_data = struct.pack('>BB', 0x08, 0x01) + struct.pack('>Q B', timestamp, 0)
    avl_data += struct.pack('>i i h h B h', lon_int, lat_int, 0, int(course), 10, int(speed))

    io_payload = struct.pack('>B B', 0, 4) + \
                struct.pack('>B B B', 1, 239, 1) + \
                struct.pack('>B B h B h', 2, 66, 12500, 67, 12500) + \
                struct.pack('>B B I', 1, 16, int(odometer)) + \
                struct.pack('>B', 0)

    full = avl_data + io_payload
    pkt = struct.pack('>L L', 0, len(full)) + full + struct.pack('>B', 0x01)
    return pkt + struct.pack('>L', crc16_arc(pkt[8:]))

def move_vehicle(lat, lon, course, speed, hubs):
    speed = max(60, min(140, speed + random.uniform(-5, 5)))
    course = (course + random.uniform(-10, 10)) % 360
    dist = speed * (SEND_INTERVAL / 3600)
    n_lat = lat + (dist / 111) * math.cos(math.radians(course))
    n_lon = lon + (dist / 111) * math.sin(math.radians(course))

    if not ((5.6 < n_lat < 20.5) and (97.3 < n_lon < 105.6)):
        h = random.choice(hubs)
        return h[0], h[1], random.uniform(0, 360), speed, 0
    return n_lat, n_lon, course, speed, dist * 1000

def sim(i):
    imei = f"860000000000{i:03d}"
    hub, my_hubs = get_hub_by_index(i)
    lat, lon = hub[0], hub[1]
    course, speed, odo = 0, 100, 50000

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # ⚡ Fix: Reduce Timeout to 5s (from 60)
                # To avoid long waiting if Server doesn't respond
                s.settimeout(1)
                s.connect((SERVER_IP, SERVER_PORT))

                s.sendall(struct.pack('>H', len(imei)) + imei.encode())
                if s.recv(1024) != b'\x01':
                    time.sleep(2)
                    continue

                while True:
                    lat, lon, course, speed, dist = move_vehicle(lat, lon, course, speed, my_hubs)
                    odo += dist
                    s.sendall(build_avl_packet(lat, lon, speed, course, odo))

                    # If Server responds, this executes fast
                    # If not, waits 5s (settimeout) then loops
                    if not s.recv(1024): break

                    time.sleep(SEND_INTERVAL)

        except Exception:
            time.sleep(2)

if __name__ == "__main__":
    for i in range(1, DEVICE_COUNT + 1):
        threading.Thread(target=sim, args=(i,), daemon=True).start()
        time.sleep(0.02)
