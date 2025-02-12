# Airflow AbuseIPDB Monitor

## Project Overview
This project automates threat intelligence gathering using **Apache Airflow** and **AbuseIPDB API**. The DAG fetches malicious IPs, checks their threat scores, and logs high-risk IPs for security monitoring.

## Features
✅ Automates fetching malicious IPs from **AbuseIPDB**  
✅ Logs threat intelligence results to `/opt/airflow/logs/abuseipdb_results.json`  
✅ Flags **high-risk IPs** based on a configurable threshold  
✅ Runs as an **Airflow DAG** on a scheduled basis  

## Project Structure
```
📁 airflow-abuseipdb-monitor/
├── dags/                   # Airflow DAG files
│   ├── abuseipdb_monitor.py  # Main DAG script
├── logs/                   # Stores threat intelligence results
│   ├── abuseipdb_results.json
├── docker-compose.yaml     # Airflow setup with Docker
├── .gitignore              # Excludes logs & env files from Git
└── README.md               # Project documentation
```

## Setup & Deployment
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/airflow-abuseipdb-monitor.git
cd airflow-abuseipdb-monitor
```

### **2️⃣ Set Your API Key**
Edit `docker-compose.yaml` and add:
```yaml
ABUSE_IPDB_API_KEY: "your_api_key_here"
```

### **3️⃣ Start Airflow**
```bash
docker-compose up -d
```

### **4️⃣ Monitor Results**
```bash
cat /opt/airflow/logs/abuseipdb_results.json
```

##  Use Cases
🔹 Security teams automating **threat intelligence gathering**  
🔹 SOC analysts needing **scheduled malicious IP checks**  
🔹 Cybersecurity projects tracking **emerging threats**  

## License
This project is licensed under the **Apache 2.0 License**.
