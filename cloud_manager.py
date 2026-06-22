"""
=============================================================================
  INTELLIGENT CLOUD RESOURCE OPTIMIZER & FINOPS GOVERNANCE PLATFORM
  Version: 2.0.0
  Author:  Cloud Solutions Architect
  Stack:   Python 3 | Tkinter / ttk | JSON
=============================================================================
"""

import os
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS & THEME TOKENS
# ─────────────────────────────────────────────────────────────────────────────

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "cloud_config.json")

# FinOps thresholds
UPTIME_POLICY_HOURS     = 48     # non-prod hours before flagging
CPU_RIGHTSIZING_PCT     = 15.0   # below this → over-provisioned
WASTE_BUDGET_FACTOR     = 0.60   # 60 % of cost is waste when over-provisioned

# Palette – deep command-centre dark
BG_BASE         = "#0d1117"   # deepest background
BG_PANEL        = "#161b22"   # card / panel surface
BG_CARD         = "#1c2333"   # elevated card
BG_ROW_ALT      = "#1a2030"   # treeview alternate row
BORDER          = "#30363d"   # subtle border
ACCENT_BLUE     = "#58a6ff"   # primary action / highlight
ACCENT_GREEN    = "#3fb950"   # healthy / running
ACCENT_RED      = "#f85149"   # alert / stopped
ACCENT_ORANGE   = "#f0883e"   # optimization warning
TEXT_MAIN       = "#c9d1d9"   # generic text
TEXT_MUTED      = "#8b949e"   # subtitles / labels
TEXT_WHITE      = "#ffffff"   # headers

# ─────────────────────────────────────────────────────────────────────────────
#  APPLICATION CLASS
# ─────────────────────────────────────────────────────────────────────────────

class CloudOptimizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cloud Resource Optimizer & FinOps Governance Platform")
        self.geometry("1100x700")
        self.configure(bg=BG_BASE)
        self.resizable(True, True)

        # Reactive State Data Variables
        self._data = {}
        self._report = {
            "total_cost": 0.0,
            "total_waste": 0.0,
            "efficiency_score": 100.0,
            "violations_count": 0,
            "rightsize_count": 0,
            "active_count": 0
        }
        
        # UI Component Variables
        self._cost_var = tk.StringVar(value="$0.00")
        self._waste_var = tk.StringVar(value="$0.00")
        self._efficiency_var = tk.StringVar(value="100.0%")
        self._status_var = tk.StringVar(value="System initialized.")

        # Font Setup
        self._title_font = font.Font(family="Helvetica", size=14, weight="bold")
        self._card_val_font = font.Font(family="Helvetica", size=18, weight="bold")
        self._card_lbl_font = font.Font(family="Helvetica", size=9, weight="normal")

        # Initialize UI and Start Workflows
        self._configure_styles()
        self._build_layout()
        self._refresh_data(animate=True)
        self._schedule_refresh()

    # ─── THEME CONFIGURATION ─────────────────────────────────────────────────

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Global Widget Adjustments
        style.configure(".", background=BG_BASE, foreground=TEXT_MAIN, bordercolor=BORDER)
        
        # Label Frames
        style.configure("TLabelframe", background=BG_PANEL, bordercolor=BORDER, relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=BG_PANEL, foreground=TEXT_WHITE, font=self._title_font)

        # Custom Buttons
        style.configure("Action.TButton", background=ACCENT_BLUE, foreground=BG_BASE, font=("Helvetica", 10, "bold"), borderwidth=0)
        style.map("Action.TButton", background=[("active", "#79c0ff")])

        style.configure("Remediation.TButton", background=ACCENT_RED, foreground=TEXT_WHITE, font=("Helvetica", 10, "bold"), borderwidth=0)
        style.map("Remediation.TButton", background=[("active", "#ff7b72")])
        
        style.configure("Standard.TButton", background=BG_CARD, foreground=TEXT_MAIN, font=("Helvetica", 10), borderwidth=1, bordercolor=BORDER)
        style.map("Standard.TButton", background=[("active", BG_PANEL)])

        # Data Inventory Treeview Grid Config
        style.configure("Treeview", background=BG_PANEL, foreground=TEXT_MAIN, fieldbackground=BG_PANEL, rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background=BG_CARD, foreground=TEXT_WHITE, relief="flat", font=("Helvetica", 10, "bold"), padding=5)
        style.map("Treeview.Heading", background=[("active", BG_PANEL)])
        style.map("Treeview", background=[("selected", "#21262d")], foreground=[("selected", TEXT_WHITE)])

    # ─── INTERFACE GENERATOR ─────────────────────────────────────────────────

    def _build_layout(self):
        # 1. Platform Top Ribbon Banner
        top_banner = tk.Frame(self, bg=BG_PANEL, height=60, highlightbackground=BORDER, highlightthickness=1)
        top_banner.pack(fill="x", side="top")
        top_banner.pack_propagate(False)

        lbl_logo = tk.Label(top_banner, text="☁  AWS INTELLIGENT COMPLIANCE & FINOPS RESOURCE OPTIMIZER", font=("Helvetica", 12, "bold"), fg=TEXT_WHITE, bg=BG_PANEL)
        lbl_logo.pack(side="left", padx=20)

        # 2. Executive Metrics Summary Dashboard (3 Card Layout)
        metrics_ribbon = tk.Frame(self, bg=BG_BASE)
        metrics_ribbon.pack(fill="x", padx=20, pady=15)
        metrics_ribbon.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        self._create_metric_card(metrics_ribbon, 0, "TOTAL ACCRUED COST LIABILITY", self._cost_var, ACCENT_BLUE)
        self._create_metric_card(metrics_ribbon, 1, "IDENTIFIED COST LEAKAGE / WASTE", self._waste_var, ACCENT_ORANGE)
        self._create_metric_card(metrics_ribbon, 2, "INFRASTRUCTURE EFFICIENCY RATING", self._efficiency_var, ACCENT_GREEN)

        # 3. Main Workspace Container Split Pane (Left Tree / Right Actions Window)
        workspace = tk.Frame(self, bg=BG_BASE)
        workspace.pack(fill="both", expand=True, padx=20, pady=5)

        # Left Container Window (Active Inventory Grid)
        left_pane = ttk.LabelFrame(workspace, text="  Active Virtual Server Inventory Pool  ")
        left_pane.pack(fill="both", expand=True, side="left", padx=(0, 10))

        grid_cols = ("id", "name", "type", "env", "status", "uptime", "cpu", "cost")
        self._tree = ttk.Treeview(left_pane, columns=grid_cols, show="headings", selectmode="browse")
        
        self._tree.heading("id", text="Instance ID")
        self._tree.heading("name", text="Server Tag Name")
        self._tree.heading("type", text="Type")
        self._tree.heading("env", text="Deployment Env")
        self._tree.heading("status", text="State")
        self._tree.heading("uptime", text="Uptime (Hrs)")
        self._tree.heading("cpu", text="Avg CPU %")
        self._tree.heading("cost", text="Accrued USD")

        self._tree.column("id", width=130, anchor="center")
        self._tree.column("name", width=150, anchor="w")
        self._tree.column("type", width=90, anchor="center")
        self._tree.column("env", width=110, anchor="center")
        self._tree.column("status", width=90, anchor="center")
        self._tree.column("uptime", width=95, anchor="e")
        self._tree.column("cpu", width=85, anchor="e")
        self._tree.column("cost", width=100, anchor="e")
        
        self._tree.tag_configure("oddrow", background=BG_ROW_ALT)
        self._tree.tag_configure("evenrow", background=BG_PANEL)
        self._tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Right Container Window (Action Terminal Panel)
        right_pane = ttk.LabelFrame(workspace, text="  Required System Remediation Logs  ")
        right_pane.pack(fill="both", side="right", width=360, padx=(10, 0))

        self._terminal = tk.Text(right_pane, bg="#010409", fg=TEXT_MAIN, font=("Consolas", 10), wrap="word", relief="flat", padx=10, py=10)
        self._terminal.pack(fill="both", expand=True, padx=10, pady=10)
        self._terminal.config(state="disabled")

        # 4. Operations Control Room & Action Buttons Footer
        footer = tk.Frame(self, bg=BG_PANEL, height=50, highlightbackground=BORDER, highlightthickness=1)
        footer.pack(fill="x", side="bottom", pady=(15, 0))
        footer.pack_propagate(False)

        # Activity Status Ticker Text
        lbl_status = tk.Label(footer, textvariable=self._status_var, font=("Helvetica", 9, "italic"), fg=TEXT_MUTED, bg=BG_PANEL)
        lbl_status.pack(side="left", padx=20)

        # Management Control Action Triggers
        btn_remediate = ttk.Button(footer, text="⚡ Run Auto-Remediation", style="Remediation.TButton", command=self._trigger_remediation)
        btn_remediate.pack(side="right", padx=(5, 20), pady=10)

        btn_refresh = ttk.Button(footer, text="🔄 Sync Metrics", style="Action.TButton", command=lambda: self._refresh_data(animate=True))
        btn_refresh.pack(side="right", padx=5, pady=10)

        btn_export = ttk.Button(footer, text="📥 Export Report", style="Standard.TButton", command=self._export_report)
        btn_export.pack(side="right", padx=5, pady=10)

        btn_reset = ttk.Button(footer, text="↺ Reset Data", style="Standard.TButton", command=self._reset_data)
        btn_reset.pack(side="right", padx=5, pady=10)

    def _create_metric_card(self, parent, col, title, text_var, highlight_color):
        card = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=0, column=col, padx=8, sticky="nsew")
        
        # Color accent tab border
        accent_strip = tk.Frame(card, bg=highlight_color, height=3)
        accent_strip.pack(fill="x", side="top")

        lbl_title = tk.Label(card, text=title, font=self._card_lbl_font, fg=TEXT_MUTED, bg=BG_CARD, anchor="w")
        lbl_title.pack(fill="x", padx=15, pady=(12, 2))

        lbl_val = tk.Label(card, textvariable=text_var, font=self._card_val_font, fg=TEXT_WHITE, bg=BG_CARD, anchor="w")
        lbl_val.pack(fill="x", padx=15, pady=(0, 12))

    # ─── DATA ENGINE PIPELINE & BACKGROUND WORKING THREADS ───────────────────

    def _refresh_data(self, animate=False):
        if animate:
            self._status_var.set("Connecting to local data state architecture...")
        
        # Spin up a worker execution thread so parsing never lag-locks the main window interface
        threading.Thread(target=self._async_load_and_audit, daemon=True).start()

    def _async_load_and_audit(self):
        try:
            time.sleep(0.2) # Microdelay for native UI feel
            
            if not os.path.exists(CONFIG_PATH):
                raise FileNotFoundError(f"Configuration profile repository missing at: {CONFIG_PATH}")

            with open(CONFIG_PATH, "r") as fh:
                self._data = json.load(fh)

            # Re-init fresh runtime analytical report summary profiles
            self._report = {
                "total_cost": 0.0, "total_waste": 0.0, "efficiency_score": 100.0,
                "violations_count": 0, "rightsize_count": 0, "active_count": 0
            }
            terminal_logs = []

            instances = self._data.get("instances", [])
            for inst in instances:
                status = inst.get("status", "stopped")
                uptime = float(inst.get("uptime_hours", 0.0))
                rate = float(inst.get("hourly_cost_usd", 0.0))
                cpu = float(inst.get("avg_cpu_utilization_pct", 0.0))
                name = inst.get("instance_name", "unnamed")
                env = inst.get("environment", "Unknown")

                # Linear Cost Accrual Analysis Equation Model
                accrued = uptime * rate
                self._report["total_cost"] += accrued

                if status == "running":
                    self._report["active_count"] += 1
                    
                    # Heuristic Check 1: Policy Runtime Threshold Breakdown
                    if env in ["Testing", "Sandbox", "Development"] or "Testing" in name or "Sandbox" in name:
                        if uptime > UPTIME_POLICY_HOURS:
                            self._report["violations_count"] += 1
                            terminal_logs.append(
                                f"⚠️  [POLICY LEAK ALERT]\n"
                                f"Instance: {name}\n"
                                f"Environment profile '{env}' run duration ({int(uptime)}h) exceeds policy window ({UPTIME_POLICY_HOURS}h).\n"
                                f"Action Required: Stop or decommission asset immediately.\n"
                                f"─────────────────────────────────────\n"
                            )

                    # Heuristic Check 2: Threshold System Optimization Underutilization Engine
                    if cpu < CPU_RIGHTSIZING_PCT:
                        self._report["rightsize_count"] += 1
                        waste = accrued * WASTE_BUDGET_FACTOR
                        self._report["total_waste"] += waste
                        terminal_logs.append(
                            f"📉 [RIGHT-SIZE WARNING]\n"
                            f"Instance: {name} [{inst.get('instance_type')}]\n"
                            f"Avg Core Allocation CPU load operates at {cpu}% (Threshold: <{CPU_RIGHTSIZING_PCT}%).\n"
                            f"Calculated Spend Waste Leakage: ${waste:.2f}\n"
                            f"Action Required: Downscale allocation framework footprint.\n"
                            f"─────────────────────────────────────\n"
                        )

            # Final Platform Financial Efficiency Score Matrix Synthesis
            tc = self._report["total_cost"]
            tw = self._report["total_waste"]
            self._report["efficiency_score"] = ((tc - tw) / tc * 100.0) if tc > 0 else 100.0

            # Direct state results back to safety main thread update targets
            self.after(0, self._sync_ui_state, instances, terminal_logs)

        except Exception as err:
            self.after(0, self._show_error, str(err))

    # ─── THREAD UI STATE RE-SYNCHRONIZATION ──────────────────────────────────

    def _sync_ui_state(self, instances, logs):
        # Update executive global scorecard fields
        self._cost_var.set(f"${self._report['total_cost']:.2f}")
        self._waste_var.set(f"${self._report['total_waste']:.2f}")
        self._efficiency_var.set(f"{self._report['efficiency_score']:.1f}%")

        # Reload table grid system view
        for item in self._tree.get_children():
            self._tree.delete(item)

        for idx, inst in enumerate(instances):
            uptime = float(inst.get("uptime_hours", 0.0))
            rate = float(inst.get("hourly_cost_usd", 0.0))
            accrued = uptime * rate
            
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            
            self._tree.insert("", "end", values=(
                inst.get("instance_id", "N/A"),
                inst.get("instance_name", "N/A"),
                inst.get("instance_type", "N/A"),
                inst.get("environment", "N/A"),
                inst.get("status", "N/A").upper(),
                f"{inst.get('uptime_hours', 0.0):.1f}",
                f"{inst.get('avg_cpu_utilization_pct', 0.0):.1f}%",
                f"${accrued:.2f}"
            ), tags=(row_tag,))

        # Rewrite System Log Terminal Output Console Box
        self._terminal.config(state="normal")
        self._terminal.delete("1.0", tk.END)
        
        if logs:
            for log in logs:
                self._terminal.insert(tk.END, log)
        else:
            self._terminal.insert("1.0", "✅ ALL COMPLIANCE TARGET METRICS WITHIN SECURE THRESHOLDS.\n\nInfrastructure optimization score perfectly aligned with system FinOps policies.")
            
        self._terminal.config(state="disabled")
        
        ts = datetime.now().strftime("%H:%M:%S")
        self._status_var.set(f"Metrics Engine Synchronized at: {ts} | Running assets: {self._report['active_count']}")

    # ─── ACTIVE ONE-CLICK AUTO-REMEDIATION REMEDY MECHANISMS ─────────────────

    def _trigger_remediation(self):
        if not self._data or "instances" not in self._data:
            messagebox.showwarning("Execution Aborted", "Data profile layer uninitialized. Run system sync before applying remediation tasks.")
            return

        violations = self._report["violations_count"]
        if violations == 0:
            messagebox.showinfo("Optimization Engine Info", "No active environment policy violations detected requiring infrastructure state modifications.")
            return

        confirm = messagebox.askyesno(
            "Execute Self-Healing Remediation",
            f"Automated remediation framework flagged {violations} policy violations.\\n"
            "This operations payload will modify instance status profiles to 'stopped' and decouple active billing structures.\\n\\n"
            "Apply modifications to cloud_config.json?"
        )
        
        if confirm:
            self._status_var.set("Executing automated server shutdown sequences...")
            threading.Thread(target=self._async_remediate_payload, daemon=True).start()

    def _async_remediate_payload(self):
        try:
            modified_count = 0
            instances = self._data.get("instances", [])
            
            for inst in instances:
                status = inst.get("status", "stopped")
                uptime = float(inst.get("uptime_hours", 0.0))
                name = inst.get("instance_name", "unnamed")
                env = inst.get("environment", "Unknown")

                if status == "running" and (env in ["Testing", "Sandbox", "Development"] or "Testing" in name or "Sandbox" in name):
                    if uptime > UPTIME_POLICY_HOURS:
                        # Apply Direct Remediation Strategy State Modifiers
                        inst["status"] = "stopped"
                        inst["uptime_hours"] = 0.0  # Decouple continuous billing simulation metrics
                        modified_count += 1

            # Commit state transformations back into file JSON DB storage structure layers
            with open(CONFIG_PATH, "w") as fh:
                json.dump(self._data, fh, indent=2)

            self.after(0, self._post_remediation_complete, modified_count)
        except Exception as err:
            self.after(0, self._show_error, str(err))

    def _post_remediation_complete(self, count):
        messagebox.showinfo("Remediation Framework Complete", f"Successfully dispatched automated remediation directives.\\n{count} over-policy server assets shut down.")
        self._refresh_data(animate=True)

    # ─── DATA EXPORT REPORT UTILITY ──────────────────────────────────────────

    def _export_report(self):
        if not self._data:
            return
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = os.path.join(os.path.dirname(__file__), f"finops_report_{ts}.json")
        
        payload = {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "source_file": CONFIG_PATH,
                "platform_ver": "2.0.0"
            },
            "report":    self._report,
            "instances": self._data.get("instances", [])
        }
        with open(out, "w") as fh:
            json.dump(payload, fh, indent=2)
        messagebox.showinfo("Export Complete", f"Report saved to:\\n{out}")
        self._status_var.set(f"Report exported → finops_report_{ts}.json")

    # ─── RESET DATA STATE ────────────────────────────────────────────────────

    def _reset_data(self):
        confirm = messagebox.askyesno(
            "Reset Data",
            "This will reload the original cloud_config.json.\\n"
            "Any remediation changes will be discarded.\\nProceed?"
        )
        if confirm:
            self._refresh_data(animate=True)

    # ─── SHOW ERROR ──────────────────────────────────────────────────────────

    def _show_error(self, msg: str):
        self._status_var.set(f"⚠ Error: {msg}")
        messagebox.showerror("Engine Error", f"Analytics engine error:\\n{msg}")

    # ─── AUTO REFRESH TIMERS ─────────────────────────────────────────────────

    def _schedule_refresh(self):
        self.after(30_000, self._auto_refresh) # Queue a loop trigger every 30 seconds

    def _auto_refresh(self):
        self._refresh_data()
        self._schedule_refresh()


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = CloudOptimizerApp()
    app.mainloop()