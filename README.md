# 🛡️ RPL DAO Attack Mitigation — Sliding Window Based Defense

[![NS-3](https://img.shields.io/badge/NS--3-3.45-blue.svg)](https://www.nsnam.org/)
[![IoT Security](https://img.shields.io/badge/IoT-Security-red.svg)](https://www.rfc-editor.org/rfc/rfc6550)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A lightweight and real-time mitigation framework for **DAO replay and flooding attacks** in RPL-based IoT networks.  
> Built on NS-3 with a **sliding-window rate detector** and **adaptive cross-layer feedback** mechanism.

---

## 🎯 Overview

This project introduces a practical security enhancement for **RPL (Routing Protocol for Low-Power and Lossy Networks)**.  
It mitigates **DAO flooding attacks** that cause severe congestion and packet loss in IoT networks by integrating **rate-based detection** and **adaptive mitigation**.

### ✨ Key Contributions

- 🔍 Sliding-window based real-time detection (1-second window, 20 pkts/sec threshold)  
- 🔁 Adaptive rate limiting via cross-layer feedback  
- 💡 Achieves **82% PDR recovery** and **98.6% attack traffic reduction**  
- 🧠 Fully tunable thresholds and parameters  
- 💾 Lightweight implementation, no cryptography overhead  

---

## 🚨 Problem Statement

DAO flooding is a control-plane attack where malicious nodes send excessive DAO messages, leading to:

- **MAC-layer congestion** and **queue overflow**
- **Increased end-to-end delay** (e.g., 5.3 ms → 13.9 ms)
- **Battery drain** due to repeated retransmissions
- **Loss of routing stability** in downward paths  

Conventional RPL security measures like authentication or encryption **cannot prevent insider nodes** from performing such flooding attacks.

---

## 💡 Proposed Solution

The proposed defense introduces a **centralized mitigation logic** at the DODAG root that:

1. Tracks DAO message rates per node using a **time-stamped sliding window**  
2. Detects anomalies exceeding a defined threshold (20 pkts/s)  
3. Initiates **adaptive feedback** to slow down transmission by 10×  
4. Drops 90 % of DAO packets at the attacker source itself  
5. Automatically unblocks legitimate nodes once behavior normalizes  

**Detection latency:** ~25 ms for 800 pps attack rate  
**Overhead:** Negligible (O(W) per packet, O(W×n) memory)

---

## 📊 Performance Evaluation

| Metric | Baseline (RPL) | Attack (InsecRPL) | Mitigation (SecRPL) |
|:--------|:----------------|:------------------|:--------------------|
| **PDR (%)** | 99.53 | 99.19 | **99.47** |
| **Delay (ms)** | 5.3 | 13.9 | **5.9** |
| **Control TX** | 0 | 76 000 | **1 045** |
| **Traffic Reduction (%)** | — | — | **98.6 %** |
| **PDR Recovery (%)** | — | — | **82 %** |

✅ Maintains near-baseline PDR  
✅ 78 % delay improvement under attack  
✅ Works reliably up to 1000 pps attack rate  

---

## ⚙️ Implementation Details

- **Simulator:** NS-3 v3.45  
- **Protocol Stack:** IEEE 802.15.4 → 6LoWPAN → IPv6 → RPL → UDP  
- **Network Setup:** 25 nodes, 60 m × 60 m grid, one root and one attacker  
- **OS:** Ubuntu 22.04 LTS  
- **Simulation Duration:** 120 s (with 10 s warm-up)

### 🧩 Core Components

| Class | Functionality |
|:------|:---------------|
| `MetricsCollector` | Collects transmission/reception statistics, delay, and control metrics |
| `Mitigator` | Maintains sliding window, detects over-threshold senders, and manages blocking |
| `SmartAttacker` | Generates DAO floods, reduces rate dynamically when feedback is received |
| `DownSender` / `DownSink` | Emulates normal sensor data transmission and reception |

---

## 🧱 Installation Guide

### Prerequisites

- **NS-3 v3.45+**  
- **g++ 10+** with C++20  
- **Python 3.8+** with `matplotlib`, `numpy`, and `pandas`

### Build Instructions

```bash
# Clone the repository
git clone https://github.com/<yourusername>/IoT-dao-replay-attack-mitigation.git

# Copy to NS-3 scratch folder
cp rpl_dao_attack_mitigation.cc ~/ns-allinone-3.45/ns-3.45/scratch/

# Build inside NS-3 directory
cd ~/ns-allinone-3.45/ns-3.45
./ns3 build
```
## 🧪 Running Simulations

### 1️⃣ Baseline (No Attack)
```bash
./ns3 run "rpl_dao_attack_mitigation --attack=false"
```

### 2️⃣ Attack Only (No Mitigation)
```bash
./ns3 run "rpl_dao_attack_mitigation --attack=true --attackerPps=800 --threshold=999999"
```

### 3️⃣ Attack + Mitigation
```bash
./ns3 run "rpl_dao_attack_mitigation --attack=true --attackerPps=800 --threshold=20 --windowSec=1"
```

---

## 📈 Result Visualization

**Outputs** (saved in `/analysis_graphs`):

- `pdr_vs_attack.jpg` — PDR vs. attack frequency
- `delay_vs_attack.jpg` — Delay vs. attack rate
- `dao_overhead.jpg` — Control overhead
- `pdr_vs_threshold.jpg` — Threshold sensitivity
- `comparison_overview.jpg` — Overall performance summary

---

## 📐 Parameter Configuration

| Parameter       | Description                  | Default   | Range         |
|-----------------|-----------------------------|-----------|--------------|
| `--nNodes`      | Total nodes                 | 25        | 10–100       |
| `--area`        | Deployment area (m)         | 60        | 20–200       |
| `--attack`      | Enable attacker             | false     | true/false   |
| `--attackerPps` | Packets/sec from attacker   | 800       | 100–1000     |
| `--threshold`   | Detection threshold         | 20        | 5–50         |
| `--windowSec`   | Window size (s)             | 1.0       | 0.5–5.0      |
| `--simTime`     | Duration (s)                | 120       | 60–600       |

---

## 🔬 Experimental Variations

**Varying Attack Frequency**
for pps in 200 400 600 800 1000; do
```bash
./ns3 run "rpl_dao_attack_mitigation --attack=true --attackerPps=$pps --threshold=20"
done
```

**Varying Detection Threshold**
for t in 5 10 20 30 50; do
```bash
./ns3 run "rpl_dao_attack_mitigation --attack=true --threshold=$t"
```

---

## 🧠 Research Insights

- **Detection Latency:** ≈ 25 ms @ 800 pps
- **Computation:** O(W) per packet
- **Storage:** ~20 KB for a 25-node network
- **Energy Savings:** >95% fewer radio transmissions

---

## 🔮 Future Work

- Distributed mitigation across multiple parent nodes
- ML-based adaptive thresholding
- Real-device testing on Contiki-NG / RIOT-OS
- Standardization as an RPL security extension (IETF)

---

## 📚 References

- T. Winter et al., RPL: IPv6 Routing Protocol for Low-Power and Lossy Networks, RFC 6550, 2012
- S. Raza et al., SVELTE: Real-time Intrusion Detection in IoT, Ad Hoc Networks, 2013
- A. Dvir et al., VeRA – Version Number and Rank Authentication in RPL, IEEE MASS, 2011
- B. Ghaleb et al., Addressing the DAO Insider Attack in RPL IoT Networks, IEEE Comm. Letters, 2019
- NS-3 Consortium, https://www.nsnam.org
- Contiki-NG Project, https://www.contiki-ng.org

---

## 👨‍💻 Contributors

- Chirag S (221CS214)
- Syed Farhan (221CS254)
- Vishruth S Kumar (221CS262)
- Yashas (221CS265)
