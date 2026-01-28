# Enterprise GPS Tracking System 

<div align="center">

![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx Proxy Manager](https://img.shields.io/badge/Nginx_Proxy_Manager-F15833?style=for-the-badge&logo=nginxproxymanager&logoColor=white)
![Cloudflare](https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=Cloudflare&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=for-the-badge&logo=mariadb&logoColor=white)
![Beszel](https://img.shields.io/badge/Beszel-Monitoring-7B68EE?style=for-the-badge)

<p align="center">
  <strong>A high-availability GPS tracking infrastructure designed for scalability, security, and data integrity.</strong>
</p>

</div>

---

## 📖 Project Overview

This project implements a robust **GPS Tracking System** tailored for the Royal Irrigation Department (RID) project. It leverages **Containerization technology** to ensure portability and ease of management. The system is designed to handle high-frequency data from IoT devices (Teltonika FMC920), ensuring real-time tracking, historical data retention, and automated disaster recovery.

### 🌟 Key Features
* **Microservices Architecture:** Fully containerized using Docker & Docker Compose.
* **High Performance:** Optimized for handling 200+ devices with 30s update intervals.
* **Security First:** SSL/TLS termination via Nginx Proxy Manager and Cloudflare integration.
* **Automated Backups:** Daily cron-based SQL dumps with retention policies.
* **Historical Replay:** Dedicated "Time Travel" environment for restoring and viewing past data without affecting production.
* **Load Testing:** Verified stability under simulated high-load scenarios.

---

## 🏗 System Architecture

The infrastructure consists of several interconnected services running within a Docker network, managed by a reverse proxy gateway.

![Architecture Diagram](Architecture-Design.png)

### 📸 System Screenshots

| **Core Platform (Traccar)** | **Monitoring (Beszel)** |
| :---: | :---: |
| ![Traccar](Traccar.png) | ![Beszel](Beszel.png) |
| **Manage & Track Devices** | **Server Resource Monitoring** |

| **Database Management (DBeaver)** |
| :---: |
| ![DBeaver](dbeaver.png) |
| **Direct Database Access** |

### 🛠 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Gateway** | Nginx Proxy Manager | Handles Reverse Proxy, SSL (Let's Encrypt), and Domain mapping. |
| **Core App** | Traccar | Open-source GPS tracking platform (Java-based). |
| **Database** | MariaDB 10.6 | Optimized relational database for time-series geospatial data. |
| **Management** | DBeaver (Cloud) | Web-based database management tool. |
| **Monitoring** | Beszel | Lightweight server resource monitoring (CPU/RAM/Disk). |
| **Backup** | Fradelg | Automated MySQL cron backup solution. |

---

## 📂 Project Structure

The project is organized into modular directories for easy maintenance:

```text
/root/gps-traccar/                  # Production Environment
├── docker-compose.yml              # Main orchestrator
├── nginx/                          # Gateway Configuration
├── traccar/                        # Application Config (XML) & Logs
├── mariadb/                        # Database Volume & Config
├── dbeaver/                        # DB Management Tool
├── beszel/                         # Monitoring System
└── fradelg/                        # Automated Backup System

/root/gps-traccar-restore/          # Staging/Restore Environment
├── docker-compose.yml              # Isolated Environment Config
├── traccar/                        # Separate Config for Restore
└── mariadb/                        # Separate DB for Restore
```

## 🚀 Deployment Guide

### Prerequisites
* Ubuntu Server 22.04 LTS or newer
* Docker Engine & Docker Compose installed
* Domain name managed by Cloudflare (Recommended)

### 1. Installation
Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/your-username/gps-tracking-system.git
cd gps-tracking-system/gps-traccar
```

### 2. Configuration
Ensure all `docker-compose.yml` files inside subdirectories are configured correctly.
> **Security Note:** Change default passwords in `docker-compose.yml` and `traccar.xml` before deploying to production.

Example `docker-compose.yml` (Main):
```yaml
services:
  nginx:
    extends:
      file: ./nginx/docker-compose-nginx.yml
      service: nginx
  traccar:
    extends:
      file: ./traccar/docker-compose-traccar.yml
      service: traccar
  mariadb:
    extends:
      file: ./mariadb/docker-compose-mariadb.yml
      service: mariadb
  # ... other services
networks:
  proxy_network:
    driver: bridge
```

### 3. Start Services
```bash
docker compose up -d
```
Check the status of all containers:
```bash
docker compose ps
```

---

## 🛡️ Backup & Restoration Strategy

### Automated Backup
The system uses `fradelg/mysql-cron-backup` to perform daily backups.
* **Schedule:** Every midnight (`0 0 * * *`)
* **Retention:** 365 days
* **Format:** Compressed `.sql.gz`

### Historical Data Restoration (Staging Environment)
To view historical data without impacting the live database, we use a separate **Restore Environment** running on port `8100`.

**Workflow:**
1. Start the restore environment:
   ```bash
   cd ~/gps-traccar-restore
   docker compose up -d
   ```
2. Inject the specific backup file:
   ```bash
   zcat ~/gps-traccar/mysqlbackups/202601240000.traccar.sql.gz | docker exec -i mariadb-restore mysql -u root -p traccar
   ```
3. Access the data via `https://restore.yourdomain.com`.

---

## 🧪 Load Testing & Performance

We simulated **200 concurrent devices** sending data every 30 seconds to verify system stability.


<summary><strong> Server Specifications </strong></summary>

| Item | Specification |
| :--- | :--- |
| **Operating System (OS)** | Ubuntu Server 22.04 LTS (64-bit) |
| **Processor (CPU)** | 2 vCPU (Intel Xeon Skylake, 2 Cores / 2 Threads) |
| **Memory (RAM)** | 8 GB |

<details>
<summary><strong>📄 Click to view Python Simulation Script</strong></summary>

```python
# Simplified snippet of the load test script
import socket, struct, time, threading, random

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5027
DEVICE_COUNT = 200

def sim(i):
    imei = f"860000000000{i:03d}"
    # ... connection logic ...
    while True:
        # Simulate movement and send packet
        s.sendall(build_avl_packet(...))
        time.sleep(30)

if __name__ == "__main__":
    for i in range(1, DEVICE_COUNT + 1):
        threading.Thread(target=sim, args=(i,), daemon=True).start()
```
</details>

### Test Results (Production Config)
| Metric | Result (30s Interval) | Status |
| :--- | :--- | :--- |
| **Avg CPU Usage** | 6.53% | ✅ Excellent |
| **Memory Usage** | 2.3 GB / 4 GB | ✅ Stable |
| **Disk I/O (Write)** | 147 KB/s | ✅ Low Latency |
| **Packet Loss** | 0% | ✅ Reliable |

---

## 📡 IoT Device Configuration (Teltonika FMC920)

The system is optimized for **Teltonika FMC920** devices. Below are the critical configuration parameters.

<details>
<summary><strong>⚙️ Click to view Device Configuration Details</strong></summary>

### System Settings
| Parameter | Value | Reason |
| :--- | :--- | :--- |
| **Data Protocol** | Codec 8 Extended | Supports high I/O IDs. |
| **Ignition Source** | Power Voltage | Virtual ignition detection (13.2V = ON). |
| **Sleep Mode** | Online Deep Sleep | Saves battery while maintaining connection. |

### GPRS Settings
| Parameter | Value |
| :--- | :--- |
| **Server IP** | `Your-Public-IP` |
| **Port** | `5027` (TCP) |
| **Open Link Timeout** | `300s` |

### Data Acquisition (On Moving)
* **Min Period:** 30s
* **Min Distance:** 50m
* **Min Angle:** 30° (Smooth cornering)
* **Min Speed:** 10 km/h

</details>

---

<div align="center">
  <sub>Developed by Kanokphon Fufon | Last Updated: Jan 2026</sub>
</div>
