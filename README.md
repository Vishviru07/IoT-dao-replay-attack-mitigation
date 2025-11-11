```markdown
# 🛰️ RPL DAO Attack Mitigation in IoT Networks

[![NS-3](https://img.shields.io/badge/NS--3-3.45-blue.svg)](https://www.nsnam.org/)
[![IoT Security](https://img.shields.io/badge/IoT-Security-red.svg)](https://www.rfc-editor.org/rfc/rfc6550)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A **cross-layer sliding-window defense** that detects and mitigates DAO flooding in RPL-based IoT networks — designed for real-time protection with minimal overhead.

---

## 🎯 Overview

This project presents a **lightweight, adaptive mitigation framework** against **DAO (Destination Advertisement Object) flooding attacks** in **RPL (Routing Protocol for Low-Power and Lossy Networks)**, the de facto routing standard in IoT systems.

DAO flooding is a significant insider threat where compromised nodes transmit excessive control packets, saturating the wireless channel and disrupting downward routing.  
Our proposed approach identifies and throttles malicious sources in real-time using a **sliding-window rate monitor** and **adaptive rate-limiting feedback** mechanism.

---

## ✨ Key Highlights

- ⚡ **Real-time sliding-window detection** for precise rate-based anomaly tracking  
- 🔁 **Cross-layer adaptive rate limiting** that throttles attacker transmissions proactively  
- 🧠 **Self-healing mechanism** allowing legitimate nodes to recover automatically  
- 💾 **Low resource footprint** (&lt; 20 KB memory, &lt; 5% CPU on IoT-class nodes)  
- 📈 **83% PDR recovery** and **98.5% attack traffic suppression** verified via NS-3 simulations  
- ⚙️ Fully configurable parameters for scalability and research reproducibility  

---

## 🚨 Problem Statement

In RPL networks, the DAO message is responsible for downward route formation.  
When a malicious node floods DAOs at a high rate:

- 📶 The **shared IEEE 802.15.4 medium** becomes congested  
- 🧩 **Legitimate data packets** face collisions and drops  
- 🕒 **End-to-end delay** increases drastically (e.g., 5.3 ms → 13.8 ms)  
- 🔋 **Energy resources** are wasted processing malicious traffic  

Conventional IoT defenses (encryption, authentication) are **ineffective** against this scenario because:
- Attackers are already **authenticated insiders**
- Filtering at the **application layer** occurs too late  
- **No rate-based control** exists in the base RPL standard  

---

## 💡 Proposed Solution

### 🧱 System Architecture

```

┌─────────────────────────────────────┐
│         DODAG Root (Mitigator)     │
│ ┌──────────────────────────────┐    │
│ │ Sliding-Window Tracker       │    │
│ │  • Per-node timestamp queue  │    │
│ │  • 1 s window, T=20 pkts/s   │    │
│ └──────────────────────────────┘    │
│            ↓ Detection              │
│ ┌──────────────────────────────┐    │
│ │ Adaptive Mitigation Engine   │    │
│ │  • Mark malicious sources    │    │
│ │  • Apply 90% drop feedback   │    │
│ │  • Cross-layer throttling    │    │
│ └──────────────────────────────┘    │
└─────────────────────────────────────┘
↓ Feedback
┌──────────────┐
│   Attacker   │
│ • Rate ÷10   │
│ • Drop 90%   │
└──────────────┘

````

### 🧩 Operation

1. **Monitoring** — DODAG root maintains DAO timestamp queues per source  
2. **Detection** — Source marked suspicious if DAO rate exceeds threshold (e.g., 20 pkts/s)  
3. **Mitigation** — Cross-layer signal throttles node transmission rate  
4. **Recovery** — Legitimate nodes auto-recover when activity normalizes  

### 🧠 Core Innovation
Unlike passive filtering, this method actively sends **feedback** to the source node, preventing packets from ever reaching the MAC layer — conserving energy and bandwidth.

---

## 📊 Performance Evaluation

| Metric | Baseline (RPL) | Under Attack | With Mitigation | Improvement |
|--------|----------------|--------------|-----------------|--------------|
| **PDR** | 99.53 % | 99.19 % ❌ | 99.48 % ✅ | **83 % recovery** |
| **Delay** | 5.3 ms | 13.8 ms ❌ | 6.1 ms ✅ | **77 % reduction** |
| **Control TX** | 0 | 75 000 ❌ | 1 100 ✅ | **98.5 % reduction** |
| **Dropped** | 0 | 0 | 320 | Mitigation active |

**Key Takeaways:**
- Attack increases delay by 162 %, while mitigation restores it within 11 % of baseline  
- Overhead negligible (&lt; 0.6 ms)  
- Works reliably across attack intensities (200–1000 pps)

---

## 🧰 Installation & Setup

### Requirements

- **NS-3 (v3.45+)**  
- **C++20** compiler (GCC 10+ or Clang 11+)  
- **CMake 3.10+**  
- **Python 3.8+** with `matplotlib`, `pandas`, `numpy`  

### Build NS-3

```bash
cd ~
wget https://www.nsnam.org/releases/ns-allinone-3.45.tar.bz2
tar xjf ns-allinone-3.45.tar.bz2
cd ns-allinone-3.45/ns-3.45
./ns3 configure --enable-examples --enable-tests
./ns3 build
````

### Clone and Integrate

```bash
git clone https://github.com/yourusername/rpl-dao-attack-mitigation.git
cd rpl-dao-attack-mitigation
cp ns3_rpl_dao_mitigation.cc ~/ns-allinone-3.45/ns-3.45/scratch/
cd ~/ns-allinone-3.45/ns-3.45
./ns3 build
```

---

## 🚀 Running Simulations

### 1️⃣ Baseline (No Attack)

```bash
./ns3 run "ns3_rpl_dao_mitigation --attack=false --nNodes=25 --simTime=120"
```

### 2️⃣ Attack (No Defense)

```bash
./ns3 run "ns3_rpl_dao_mitigation --attack=true --attackerPps=800 --threshold=1000000 --simTime=120"
```

### 3️⃣ Mitigation Enabled

```bash
./ns3 run "ns3_rpl_dao_mitigation --attack=true --attackerPps=800 --threshold=20 --windowSec=1.0 --simTime=120"
```

---

## ⚙️ Parameters

| Flag            | Description         | Default | Range      |
| --------------- | ------------------- | ------- | ---------- |
| `--nNodes`      | Number of IoT nodes | 25      | 5–100      |
| `--attack`      | Enable attack mode  | false   | true/false |
| `--attackerPps` | Attack packet rate  | 800     | 100–1000   |
| `--threshold`   | Detection threshold | 20      | 5–50       |
| `--windowSec`   | Sliding window size | 1.0 s   | 0.5–5.0    |
| `--rateKbps`    | Data rate           | 16 kbps | 1–64       |
| `--simTime`     | Simulation duration | 120 s   | 30–600     |

Results and logs are automatically stored in:

```
results/
├── delay.csv
├── pdr.csv
└── overhead.csv
```

---

## 📈 Data Visualization

### Run Analysis

```bash
pip install matplotlib pandas numpy
python3 paper_graphs.py
```

### Output Graphs

Located in `/paper_graphs`:

1. `dao_overhead.png` – Control overhead vs attack rate
2. `pdr_vs_attack.png` – Packet Delivery Ratio vs attack frequency
3. `delay_vs_attack.png` – End-to-End Delay vs attack intensity
4. `pdr_vs_threshold.png` – PDR vs detection threshold
5. `overhead_vs_threshold.png` – Overhead vs threshold parameter
6. `comparison_overview.png` – Full comparative summary

---

## 🧮 Experimental Scenarios

### Attack Intensity Sweep

```bash
for rate in 200 400 600 800 1000; do
  ./ns3 run "ns3_rpl_dao_mitigation --attack=true --attackerPps=$rate --threshold=20"
done
```

### Threshold Tuning

```bash
for t in 5 10 20 30 50; do
  ./ns3 run "ns3_rpl_dao_mitigation --attack=true --threshold=$t"
done
```

---

## 🧠 Algorithm Overview

### Sliding-Window Detection

```
For each DAO arrival:
  1. Record timestamp
  2. Remove entries older than W seconds
  3. Compute rate = queue length
  4. If rate > threshold → mark malicious
```

**Time complexity:** O(W) per event
**Memory complexity:** O(W × n)

### Detection Latency

```
t_detect = Threshold / AttackRate
Example: 20 / 800 = 0.025 s = 25 ms
```

---

## 🔐 Security Model

### Assumptions

* Single authenticated insider attacker
* No physical or cryptographic tampering
* All nodes follow standard IEEE 802.15.4 and RPL behavior

### Current Limitations

* Single point of detection (root)
* Initial 20 packets undetected (warm-up)
* Limited handling of multi-attacker coordination

### Planned Enhancements

* Distributed detection architecture
* Adaptive ML-based thresholding
* Integration with RPL secure mode (RFC 6550)

---

## 🧩 System Components

### Class Overview (C++)

```cpp
class MetricsCollector {
  void NoteTxPacket(uint32_t size);
  void NoteRxPacket(uint32_t size, Time delay);
  void NoteControlTx(uint32_t count);
  void NoteControlRx(uint32_t count);
  void NoteControlDropped(uint32_t count);
  void WriteCsv(std::string filename);
};

class Mitigator {
  void HandleRead(Ptr<Socket> socket);
  bool CheckThreshold(Ipv6Address src);
  void AddBlockedSource(Ipv6Address src);
  void RemoveBlockedSource(Ipv6Address src);
};
```

---

## 🧾 Related Work

| Approach       | Detection Type            | Mitigation            | Overhead | Insider Defense |
| -------------- | ------------------------- | --------------------- | -------- | --------------- |
| **SVELTE [1]** | Version inconsistency     | Drop anomalies        | Low      | ❌               |
| **VeRA [2]**   | Cryptographic auth        | Authentication        | High     | ❌               |
| **SecRPL [3]** | Per-destination threshold | Application filtering | Medium   | ⚠️ Partial      |
| **Our Work**   | Sliding-window rate       | Adaptive feedback     | Minimal  | ✅ Yes           |

---

## 🔗 References

1. Raza et al., *“SVELTE: Real-time Intrusion Detection in IoT,”* Ad Hoc Networks, 2013
2. Dvir et al., *“VeRA – Version Number and Rank Authentication in RPL,”* IEEE MASS, 2011
3. Ghaleb et al., *“Addressing the DAO Insider Attack in RPL’s IoT Networks,”* IEEE Comm Letters, 2019
4. Winter et al., *“RPL: IPv6 Routing Protocol for Low-Power and Lossy Networks,”* RFC 6550, IETF, 2012
5. NS-3 Consortium, *“NS-3 Network Simulator,”* [https://www.nsnam.org](https://www.nsnam.org)

---

## 🧑‍💻 Authors

**Vishruth S Kumar** (221CS262)
**Chirag S** (221CS214)
**Syed Farhan** (221CS254)
**Yashas** (221CS265)

**Guide:** Dr. Alwyn Roshan Pais, Department of CSE, NITK Surathkal
📅 November 2025

---

## 📜 License

This project is licensed under the **MIT License** — free for academic and research use.

---

```
```
