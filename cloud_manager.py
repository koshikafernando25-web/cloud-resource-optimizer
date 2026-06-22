import json
import os
import time

# SETTING: Change to True if you want the script to automatically SHUT DOWN wasteful test servers!
AUTO_REMEDIATE = True

def load_cloud_environment():
    if not os.path.exists("cloud_config.json"):
        print("❌ CRITICAL ERROR: cloud_config.json configuration profile missing!")
        return None
    with open("cloud_config.json", "r") as file:
        return json.load(file)

def save_cloud_environment(data):
    """Saves the modified infrastructure state back to the JSON file."""
    with open("cloud_config.json", "w") as file:
        json.dump(data, file, indent=2)
    print("💾 [SYSTEM INFO] cloud_config.json updated successfully with new states.")

def run_cloud_audit():
    cloud_data = load_cloud_environment()
    if not cloud_data:
        return

    print("==================================================================")
    print(f"☁️  AWS INTELLIGENT RESOURCE OPTIMIZER V2")
    print(f"⏰ Execution Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================================")
    print(f"Provider  : {cloud_data['cloud_provider']}")
    print(f"Region    : {cloud_data['target_region']}")
    print("------------------------------------------------------------------")
    
    servers = cloud_data["virtual_servers"]
    active_compute_units = 0
    total_accrued_cost = 0.0
    estimated_waste_usd = 0.0
    recommendations = []
    file_needs_update = False
    
    for server in servers:
        status_symbol = "🟢" if server["status"] == "running" else "⚪"
        print(f"{status_symbol} Instance: {server['name']} [{server['id']}]")
        
        # Calculate accrued cost safely
        hourly_rate = server.get("hourly_cost_usd", 0.0)
        uptime = server.get("uptime_hours", 0)
        accrued_cost = uptime * hourly_rate
        total_accrued_cost += accrued_cost
        
        if server["status"] == "running":
            active_compute_units += 1
            cpu = server.get("avg_cpu_utilization_pct", 100.0)
            print(f"   └─ Type: {server['type']} | CPU Avg: {cpu}% | Cost Accrued: ${accrued_cost:.2f}")
            
            # Policy Violation: Non-prod sandbox left running extensively
            if "Sandbox" in server["name"] or "Testing" in server["name"]:
                print(f"   ⚠️  [ALERT] Non-prod instance running extensively ({uptime} hrs).")
                
                if AUTO_REMEDIATE and uptime > 48:
                    print(f"   🛠️  [REMEDIATION] Automatically STOPPING server to prevent billing leaks!")
                    server["status"] = "stopped"
                    server["uptime_hours"] = 0  # Stop further billing accrual simulation
                    file_needs_update = True
                    continue # Skip right-sizing check since we are shutting it down
            
            # Efficiency Rule: Low CPU utilization check
            if cpu < 15.0:
                estimated_waste = accrued_cost * 0.60
                estimated_waste_usd += estimated_waste
                print(f"   📉 [RIGHT-SIZE WARNING] Underutilized resource! Avg CPU is under 15%.")
                
                if "large" in server["type"]:
                    action = f"Downsize {server['name']} from {server['type']} to t3.medium (Saves ~60%)"
                else:
                    action = f"Downsize {server['name']} to t3.micro"
                recommendations.append(action)
        else:
            print(f"   └─ Type: {server['type']} | State: STOPPED (No active compute billing)")
        print("-" * 66)
                
    # Calculate Efficiency Score
    if total_accrued_cost > 0:
        efficiency_score = (1 - (estimated_waste_usd / total_accrued_cost)) * 100
    else:
        efficiency_score = 100.0

    print("==================================================================")
    print("📊 FINOPS & OPTIMIZATION REPORT")
    print(f"Total Cloud Compute Cost Accrued : ${total_accrued_cost:.2f}")
    print(f"Identified Cost Leakage / Waste  : ${estimated_waste_usd:.2f}")
    print(f"Infrastructure Efficiency Score  : {efficiency_score:.1f}%")
    print("==================================================================")
    
    if recommendations:
        print("\n📋 SUGGESTED ACTION ITEMS:")
        for idx, rec in enumerate(recommendations, 1):
            print(f"  {idx}. {rec}")
        print("==================================================================")

    # Save changes if any servers were auto-stopped
    if file_needs_update:
        print("\n")
        save_cloud_environment(cloud_data)

if __name__ == "__main__":
    run_cloud_audit()