# 🛡️ RPL DAO Attack Mitigation — Sliding Window Based Approach

[![NS-3](https://img.shields.io/badge/NS--3-3.45-blue.svg)](https://www.nsnam.org/)
[![IoT Security](https://img.shields.io/badge/IoT-Security-red.svg)](https://www.rfc-editor.org/rfc/rfc6550)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A lightweight, real-time mitigation framework against DAO replay and flooding attacks in RPL-based IoT networks.  
> Implements sliding-window rate detection with adaptive cross-layer feedback.

---

## 🚀 Overview

This project presents an **NS-3 simulation-based defense mechanism** for DAO flooding attacks in **RPL (Routing Protocol for Low-Power and Lossy Networks)**.  
By combining **sliding-window rate tracking** with **adaptive rate limiting**, the system proactively mitigates congestion caused by insider nodes while maintaining near-baseline network performance.

### 🔍 Highlights

- ⚡ Real-time sliding-window detection (1-second window, 20 pkt/sec threshold)  
- 🔁 Adaptive feedback that slows malicious transmission rates by 99%  
- 💡 Achieves **82% packet delivery recovery** and **98.6% traffic reduction**  
- 💾 Lightweight, cryptography-free design for constrained IoT devices  
- 🔧 Fully parameterized — supports attack intensity, threshold, and topology variation

---

## ⚠️ Problem Statement

DAO flooding overwhelms the downward routing path in RPL networks by injecting excessive control messages, causing:

- Severe **MAC-layer congestion** and **queue overflow**
- Up to **160% delay increase** during attack scenarios  
- **Battery depletion** due to unnecessary transmissions  
- **Limited resilience** of standard RPL security extensions

Existing cryptographic or blacklist-based defenses **fail against insider threats**, since authenticated nodes can still exploit their credentials.

---

## 💡 Solution Design

### 📘 System Architecture

