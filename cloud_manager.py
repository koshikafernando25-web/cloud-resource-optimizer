import json
import os
import time

def load_cloud_environment():
    """Loads and returns the simulated cloud infrastructure configuration."""
    if not os.path.exists("cloud_config.json"):
        print("❌ CRITICAL ERROR: cloud_config.json configuration profile missing!")
        return None
    with open("cloud_config.json", "r") as file:
        return json.load(file)

def run_cloud_audit():
    """Parses cloud infrastructure and flags architectural/billing anomalies."""
    cloud_data = load_cloud_environment()
    if not cloud_data:
        return

    print("==================================================================")
    print(f"☁️  AWS COMPLIANCE & RESOURCE AUDIT ENGINE")
    print(f"⏰ Execution Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================================")
    print(f"Provider  : {cloud_data['cloud_provider']}")
    print(f"Region    : {cloud_data['target_region']}")
    print(f"Auth Token: {cloud_data['auth_status']} [SECURE]")
    print("------------------------------------------------------------------")
    
    servers = cloud_data["virtual_servers"]
    active_compute_units = 0
    billing_leak_alerts = 0
    
    for server in servers:
        status_symbol = "🟢" if server["status"] == "running" else "⚪"
        print(f"{status_symbol} Instance: {server['name']} [{server['id']}]")
        print(f"   └─ Type: {server['type']} | State: {server['status'].upper()}")
        
        # DevOps Optimization Logic: Look for idle/wasteful testing resources
        if server["status"] == "running":
            active_compute_units += 1
            if "Sandbox" in server["name"] or "Testing" in server["name"]:
                print(f"   ⚠️  [BILLING LEAK ALERT] Non-production server running extensively! ({server['uptime_hours']} hrs)")
                billing_leak_alerts += 1
                
    print("==================================================================")
    print("📊 CLOUD METRICS SUMMARY")
    print(f"Total Configured Instances : {len(servers)}")
    print(f"Active Running Instances   : {active_compute_units}")
    print(f"Cost Optimizations Flagged : {billing_leak_alerts} Action(s) Required")
    print("==================================================================")

if __name__ == "__main__":
    run_cloud_audit()