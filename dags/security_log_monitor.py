from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import requests
import os

# Load API Key 
ABUSE_IPDB_API_KEY = os.getenv("ABUSE_IPDB_API_KEY", "")
THRESHOLD_SCORE = 75  # Flag IPs with a risk score above this

if not ABUSE_IPDB_API_KEY:
    raise ValueError("AbuseIPDB API Key is missing. Set ABUSE_IPDB_API_KEY in environment variables.")

# Define default args
default_args = {
    'owner': 'security_team',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Function to fetch live malicious IPs
def get_live_malicious_ips():
    headers = {"Key": ABUSE_IPDB_API_KEY, "Accept": "application/json"}
    try:
        response = requests.get(
            "https://api.abuseipdb.com/api/v2/blacklist",
            headers=headers,
            params={"limit": 50}  # Get top 50 bad IPs
        )
        response.raise_for_status()
        data = response.json()
        ips = [entry["ipAddress"] for entry in data.get("data", [])]
        print(f"Found {len(ips)} malicious IPs")
        return ips
    except requests.RequestException as e:
        print(f"Error fetching IPs: {e}")
        return []

#fetch threat intelligence for each IP
def fetch_abuseipdb_data():
    headers = {"Key": ABUSE_IPDB_API_KEY, "Accept": "application/json"}
    check_ips = get_live_malicious_ips()
    results = []
    
    for ip in check_ips:
        try:
            response = requests.get(
                "https://api.abuseipdb.com/api/v2/check",
                headers=headers,
                params={"ipAddress": ip, "maxAgeInDays": 90}
            )
            response.raise_for_status()
            data = response.json()
            results.append({
                "ip": ip,
                "abuse_score": data["data"].get("abuseConfidenceScore", 0),
                "is_malicious": data["data"].get("abuseConfidenceScore", 0) > THRESHOLD_SCORE,
                "total_reports": data["data"].get("totalReports", 0)
            })
        except requests.RequestException as e:
            print(f"Error fetching data for {ip}: {e}")
    
    logs_path = "/opt/airflow/logs/abuseipdb_results.json"
    with open(logs_path, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Threat intelligence results saved to {logs_path}")

# Function to analyze threat data
def analyze_threat_data():
    logs_path = "/opt/airflow/logs/abuseipdb_results.json"
    
    if not os.path.exists(logs_path):
        print("No data file found, skipping analysis.")
        return
    
    with open(logs_path, 'r') as f:
        data = json.load(f)
    
    flagged_ips = [entry for entry in data if entry.get("is_malicious")]
    
    if flagged_ips:
        print("ALERT: Malicious IPs detected")
        for ip_info in flagged_ips:
            print(f"{ip_info['ip']} - Abuse Score: {ip_info['abuse_score']}, Reports: {ip_info['total_reports']}")
    else:
        print("NO high-risk IPs detected.")

# Define Airflow DAG
with DAG(
    'security_abuseipdb_monitor',
    default_args=default_args,
    schedule_interval=timedelta(hours=1),  # Runs every hour
    catchup=False,
) as dag:
    
    task_fetch_data = PythonOperator(
        task_id='fetch_abuseipdb_data',
        python_callable=fetch_abuseipdb_data
    )
    
    task_analyze_data = PythonOperator(
        task_id='analyze_threat_data',
        python_callable=analyze_threat_data
    )
    
    task_fetch_data >> task_analyze_data