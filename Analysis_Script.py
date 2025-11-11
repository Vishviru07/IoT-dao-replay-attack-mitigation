#!/usr/bin/env python3
"""
RPL DAO Flooding Mitigation Study - Automated Simulation & Visualization
This script executes multiple ns-3 runs and generates analytical plots
to mirror publication-style evaluation results.
"""

import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# -------------------------------------------------------------------
#  Configuration Paths
# -------------------------------------------------------------------
NS3_ROOT = "/home/chirag/acn_gowda/ns-3-dev-ecn"
SCRATCH_DIR = os.path.join(NS3_ROOT, "scratch")
OUTPUT_DIR = os.path.join(NS3_ROOT, "analysis_graphs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.exists(NS3_ROOT):
    print(f"❌ ERROR: NS-3 directory not found at {NS3_ROOT}")
    exit(1)
if not os.path.exists(SCRATCH_DIR):
    print(f"❌ ERROR: Scratch directory missing at {SCRATCH_DIR}")
    exit(1)

# -------------------------------------------------------------------
#  Utility: Execute ns-3 Simulation and Parse CSV Results
# -------------------------------------------------------------------
def execute_ns3(attack, attack_rate=700, limit=25, node_count=25, win=1.2, duration=120):
    """Run an ns-3 instance and extract computed metrics."""
    if attack:
        command = (
            f"./ns3 run 'dioneighbour "
            f"--attack=true --attackerPps={attack_rate} --attackerPkt=120 "
            f"--threshold={limit} --windowSec={win} --nNodes={node_count} "
            f"--area=60 --rateKbps=16 --simTime={duration}'"
        )
    else:
        command = (
            f"./ns3 run 'dioneighbour "
            f"--attack=false --nNodes={node_count} --area=60 "
            f"--rateKbps=16 --simTime={duration}'"
        )

    result = subprocess.run(command, shell=True, cwd=NS3_ROOT, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"   ❌ Simulation failed.")
        return None

    try:
        pdr_df = pd.read_csv(f"{NS3_ROOT}/results/run1_pdr.csv")
        delay_df = pd.read_csv(f"{NS3_ROOT}/results/run1_delay.csv")
        over_df = pd.read_csv(f"{NS3_ROOT}/results/run1_overhead.csv")

        return {
            "pdr": pdr_df["pdr"].iloc[0],
            "tx": pdr_df["tx"].iloc[0],
            "rx": pdr_df["rx"].iloc[0],
            "delay_ms": delay_df["avg_delay_s"].iloc[0] * 1000,
            "ctrl_tx": over_df["control_tx"].iloc[0],
            "ctrl_rx": over_df["control_rx"].iloc[0],
            "ctrl_dropped": over_df["control_dropped"].iloc[0],
        }
    except Exception as e:
        print(f"   ❌ Error reading result files: {e}")
        return None

# -------------------------------------------------------------------
#  Dataset Collection: Baseline Cases
# -------------------------------------------------------------------
def gather_baselines():
    """Simulate core RPL scenarios (no attack, attack-only, mitigation)."""
    print("\n" + "=" * 70)
    print("RUNNING BASELINE SIMULATIONS")
    print("=" * 70)

    records = []

    # Case 1: Plain RPL (no attack)
    print("▶ Running Baseline RPL...")
    out = execute_ns3(attack=False)
    if out:
        out["scenario"] = "RPL"
        records.append(out)
        print(f"   ✓ PDR = {out['pdr']:.3f}")

    # Case 2: Unsecured RPL under attack
    print("▶ Running Insecure RPL (Attack without Mitigation)...")
    out = execute_ns3(attack=True, limit=999999999)
    if out:
        out["scenario"] = "InsecRPL"
        records.append(out)
        print(f"   ✓ PDR = {out['pdr']:.3f}")

    # Case 3: Secure RPL (Attack + Mitigation)
    print("▶ Running Secure RPL (Mitigation Enabled)...")
    out = execute_ns3(attack=True, limit=25)
    if out:
        out["scenario"] = "SecRPL"
        records.append(out)
        print(f"   ✓ PDR = {out['pdr']:.3f}")

    return pd.DataFrame(records)

# -------------------------------------------------------------------
#  Dataset Collection: Attack Rate Variation
# -------------------------------------------------------------------
def gather_attack_variants():
    """Vary flooding intensity to measure performance degradation."""
    print("\n" + "=" * 70)
    print("RUNNING ATTACK RATE EXPERIMENTS")
    print("=" * 70)

    rates = [150, 300, 500, 700, 900, 1100]
    combined = []

    for r in rates:
        print(f"▶ Attacker frequency: {r} packets/s")

        # Insecure setup
        res = execute_ns3(attack=True, attack_rate=r, limit=999999999)
        if res:
            res["scenario"] = "InsecRPL"
            res["attack_pps"] = r
            combined.append(res)

        # Secure setup
        res = execute_ns3(attack=True, attack_rate=r, limit=25)
        if res:
            res["scenario"] = "SecRPL"
            res["attack_pps"] = r
            combined.append(res)

    # Append RPL (no attack) as reference
    ref = execute_ns3(attack=False)
    if ref:
        for r in rates:
            temp = ref.copy()
            temp["scenario"] = "RPL"
            temp["attack_pps"] = r
            combined.append(temp)

    return pd.DataFrame(combined)

# -------------------------------------------------------------------
#  Dataset Collection: Mitigation Threshold Variation
# -------------------------------------------------------------------
def gather_threshold_tests():
    """Assess performance under different DAO packet thresholds."""
    print("\n" + "=" * 70)
    print("RUNNING THRESHOLD EXPERIMENTS")
    print("=" * 70)

    limits = [5, 15, 25, 35, 50, 70]
    collected = []

    for lim in limits:
        print(f"▶ Evaluating Threshold: {lim}")
        out = execute_ns3(attack=True, attack_rate=700, limit=lim)
        if out:
            out["scenario"] = "SecRPL"
            out["threshold"] = lim
            collected.append(out)
            print(f"   ✓ PDR: {out['pdr']:.3f}")

    return pd.DataFrame(collected)

# -------------------------------------------------------------------
#  Graph Generator
# -------------------------------------------------------------------
def make_graphs(baseline_df, rate_df, thresh_df):
    """Produce visualizations resembling IEEE-style paper figures."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "legend.fontsize": 10,
        "figure.titlesize": 14
    })

    color_map = {"RPL": "#1f77b4", "InsecRPL": "#ff7f0e", "SecRPL": "#2ca02c"}
    symbols = {"RPL": "o", "InsecRPL": "s", "SecRPL": "^"}

    # --- Figure 1: DAO Overhead vs Attack Interval ---
    if not rate_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        for label in ["RPL", "InsecRPL", "SecRPL"]:
            subset = rate_df[rate_df["scenario"] == label].sort_values("attack_pps")
            if subset.empty:
                continue
            x = 1.0 / subset["attack_pps"].values
            y = subset["ctrl_rx"].values
            ax.plot(x, y, marker=symbols[label], color=color_map[label],
                    linewidth=2, markersize=7, label=label)
        ax.set_xlabel("Attack Interval (s)", fontweight="bold")
        ax.set_ylabel("DAO Packets Forwarded", fontweight="bold")
        ax.set_title("DAO Control Traffic vs Attack Frequency", fontweight="bold")
        ax.grid(alpha=0.3, linestyle="--")
        ax.legend()
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/dao_overhead.png", dpi=300)
        plt.close()

    # --- Figure 2: PDR vs Attack Frequency ---
    if not rate_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        for label in ["RPL", "InsecRPL", "SecRPL"]:
            subset = rate_df[rate_df["scenario"] == label].sort_values("attack_pps")
            if subset.empty:
                continue
            x = 1.0 / subset["attack_pps"].values
            y = subset["pdr"].values
            ax.plot(x, y, marker=symbols[label], color=color_map[label],
                    linewidth=2, markersize=7, label=label)
        ax.set_xlabel("Attack Interval (s)", fontweight="bold")
        ax.set_ylabel("Packet Delivery Ratio", fontweight="bold")
        ax.set_title("PDR under Increasing Attack Frequency", fontweight="bold")
        ax.set_ylim([0.7, 1.0])
        ax.grid(alpha=0.3, linestyle="--")
        ax.legend()
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/pdr_vs_attack.png", dpi=300)
        plt.close()

    # --- Figure 3: Delay vs Attack Frequency ---
    if not rate_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        for label in ["RPL", "InsecRPL", "SecRPL"]:
            subset = rate_df[rate_df["scenario"] == label].sort_values("attack_pps")
            if subset.empty:
                continue
            x = 1.0 / subset["attack_pps"].values
            y = subset["delay_ms"].values
            ax.plot(x, y, marker=symbols[label], color=color_map[label],
                    linewidth=2, markersize=7, label=label)
        ax.set_xlabel("Attack Interval (s)", fontweight="bold")
        ax.set_ylabel("End-to-End Delay (ms)", fontweight="bold")
        ax.set_title("Average Latency vs DAO Attack Frequency", fontweight="bold")
        ax.grid(alpha=0.3, linestyle="--")
        ax.legend()
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/delay_vs_attack.png", dpi=300)
        plt.close()

    # --- Figure 4: PDR vs DAO Threshold ---
    if not thresh_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        subset = thresh_df.sort_values("threshold")
        ax.plot(subset["threshold"], subset["pdr"], marker="^",
                color=color_map["SecRPL"], linewidth=2, label="SecRPL")
        if not baseline_df.empty:
            ax.axhline(y=baseline_df.loc[baseline_df["scenario"] == "RPL", "pdr"].iloc[0],
                       linestyle="--", color=color_map["RPL"], label="RPL Base")
            ax.axhline(y=baseline_df.loc[baseline_df["scenario"] == "InsecRPL", "pdr"].iloc[0],
                       linestyle="--", color=color_map["InsecRPL"], label="InsecRPL")
        ax.set_xlabel("DAO Threshold Limit", fontweight="bold")
        ax.set_ylabel("Packet Delivery Ratio", fontweight="bold")
        ax.set_title("Impact of DAO Threshold on PDR", fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3, linestyle="--")
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/pdr_vs_threshold.png", dpi=300)
        plt.close()
        
# -------------------------------------------------------------------
#  Comparative Overview Chart (RPL vs InsecRPL vs SecRPL)
# -------------------------------------------------------------------
def make_comparison_chart(baseline_df):
    """Create side-by-side bar comparison of PDR, Delay, and Control Overhead."""
    if baseline_df.empty:
        return

    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "legend.fontsize": 10,
        "figure.titlesize": 14
    })

    colors = {"RPL": "#961fff", "InsecRPL": "#552903", "SecRPL": "#f2ff00"}

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    scenarios = baseline_df["scenario"].values
    pdr_vals = baseline_df["pdr"].values
    delay_vals = baseline_df["delay_ms"].values
    ctrl_vals = baseline_df["ctrl_rx"].values

    # --- PDR ---
    bars1 = ax1.bar(scenarios, pdr_vals,
                    color=[colors[s] for s in scenarios],
                    edgecolor="black", linewidth=1.3)
    ax1.set_ylabel("PDR", fontweight="bold")
    ax1.set_title("Packet Delivery Ratio", fontweight="bold")
    ax1.set_ylim([0, 1.05])
    ax1.grid(axis="y", alpha=0.3)
    for i, b in enumerate(bars1):
        ax1.text(b.get_x() + b.get_width()/2., b.get_height(),
                 f"{pdr_vals[i]:.3f}", ha="center", va="bottom", fontweight="bold")

    # --- Delay ---
    bars2 = ax2.bar(scenarios, delay_vals,
                    color=[colors[s] for s in scenarios],
                    edgecolor="black", linewidth=1.3)
    ax2.set_ylabel("Delay (ms)", fontweight="bold")
    ax2.set_title("End-to-End Delay", fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)
    for i, b in enumerate(bars2):
        ax2.text(b.get_x() + b.get_width()/2., b.get_height(),
                 f"{delay_vals[i]:.1f}", ha="center", va="bottom", fontweight="bold")

    # --- Control Overhead ---
    bars3 = ax3.bar(scenarios, ctrl_vals,
                    color=[colors[s] for s in scenarios],
                    edgecolor="black", linewidth=1.3)
    ax3.set_ylabel("Control Packets", fontweight="bold")
    ax3.set_title("Control Traffic Overhead", fontweight="bold")
    ax3.grid(axis="y", alpha=0.3)
    for i, b in enumerate(bars3):
        ax3.text(b.get_x() + b.get_width()/2., b.get_height(),
                 f"{int(ctrl_vals[i])}", ha="center", va="bottom", fontweight="bold")

    plt.suptitle("Performance Comparison: RPL vs InsecRPL vs SecRPL",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/comparison_overview.png", dpi=300, bbox_inches="tight")
    print("✓ Saved: comparison_overview.png")
    plt.close()


# -------------------------------------------------------------------
#  Summary Printer
# -------------------------------------------------------------------
def summarize_results(baseline_df):
    """Print key metrics and performance improvements."""
    print("\n" + "=" * 80)
    print("EXPERIMENT SUMMARY")
    print("=" * 80)

    if not baseline_df.empty:
        print("\n📊 Baseline Overview:")
        print(baseline_df[["scenario", "pdr", "delay_ms", "ctrl_rx", "ctrl_dropped"]].to_string(index=False))

        if set(["SecRPL", "InsecRPL"]).issubset(baseline_df["scenario"].values):
            insec = baseline_df.loc[baseline_df["scenario"] == "InsecRPL", "pdr"].iloc[0]
            sec = baseline_df.loc[baseline_df["scenario"] == "SecRPL", "pdr"].iloc[0]
            improvement = ((sec - insec) / insec) * 100
            print(f"\n✨ Improvements:")
            print(f"   • PDR gain via mitigation: {improvement:.2f}%")
            print(f"   • Attack degradation: {(1 - insec) * 100:.2f}%")
            blocked = baseline_df.loc[baseline_df["scenario"] == "SecRPL", "ctrl_dropped"].iloc[0]
            print(f"   • DAO packets filtered: {int(blocked)}")

# -------------------------------------------------------------------
#  Main Entrypoint
# -------------------------------------------------------------------
def main():
    print("\n🚀==============================================================🚀")
    print("   AUTOMATED RPL DAO ATTACK SIMULATION & PAPER-GRADE PLOTTING")
    print("🚀==============================================================🚀\n")

    print(f"📁 NS-3 Root: {NS3_ROOT}")
    print(f"📁 Scratch: {SCRATCH_DIR}")
    print(f"📁 Output: {OUTPUT_DIR}")

    code_file = os.path.join(SCRATCH_DIR, "dioneighbour.cc")
    if not os.path.exists(code_file):
        print(f"\n❌ Could not locate simulation file: {code_file}")
        return
    print(f"✅ Simulation code found.\n")

    base_df = gather_baselines()
    rate_df = gather_attack_variants()
    thresh_df = gather_threshold_tests()

    base_df.to_csv(f"{OUTPUT_DIR}/baseline.csv", index=False)
    rate_df.to_csv(f"{OUTPUT_DIR}/attack_rate.csv", index=False)
    thresh_df.to_csv(f"{OUTPUT_DIR}/thresholds.csv", index=False)
    print(f"\n💾 Data stored in {OUTPUT_DIR}/")

    print("\n📊 Creating figures...")
    make_graphs(base_df, rate_df, thresh_df)
    make_comparison_chart(base_df)

    summarize_results(base_df)

    print("\n✅==============================================================✅")
    print("   ANALYSIS FINISHED. Graphs exported to:", OUTPUT_DIR)
    print("✅==============================================================✅\n")

if __name__ == "__main__":
    main()
