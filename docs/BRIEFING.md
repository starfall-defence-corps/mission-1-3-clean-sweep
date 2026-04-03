---
CLASSIFICATION: CADET EYES ONLY
MISSION: 1.3 — CLEAN SWEEP
THEATRE: Starfall Defence Corps Academy
AUTHORITY: SDC Cyber Command, 2187
---

# OPERATION ORDER — MISSION 1.3: CLEAN SWEEP

---

## 1. SITUATION

### 1a. Enemy Forces

No single Voidborn agent is responsible for this disaster. This is the result of **neglect** — months of deferred maintenance, ignored baselines, and the attitude of "it works, don't touch it." The fleet's nodes are running unnecessary services, firewalls are inactive, kernel parameters are unhardened, and file permissions are too loose. Every misconfiguration is an open invitation to the Voidborn.

### 1b. Friendly Forces

The **Starfall Defence Corps (SDC)** fleet has been inventoried (Mission 1.1) and SSH has been hardened (Mission 1.2). But SSH is just one door. The fleet still runs services nobody asked for, has no active firewall, and lacks basic kernel hardening. The nodes are catalogued and SSH-locked, but otherwise defenceless.

### 1c. Attachments / Support

**ARIA** (Automated Review & Intelligence Analyst) is assigned to this mission. ARIA will verify package state, firewall status, file permissions, and kernel parameters across all nodes.

### 1d. Operational Tools

This mission introduces several new Ansible modules:

| Module | Purpose |
|--------|---------|
| `ansible.builtin.apt` | Install or remove packages |
| `community.general.ufw` | Manage firewall rules and state |
| `ansible.builtin.copy` | Deploy files from the control node to targets |
| `ansible.builtin.file` | Set file permissions and ownership |
| `ansible.builtin.command` | Run commands (used for sysctl reload) |

---

## 2. MISSION

Write and execute an Ansible playbook to clean up and harden all fleet nodes. Remove unnecessary packages. Enable and configure the firewall. Deploy hardened kernel parameters. Correct file permissions.

**End state**: Every node stripped of unnecessary services, firewall active with SSH allowed, kernel hardened against common network attacks, and sensitive file permissions corrected. All changes verified as idempotent.

---

## 3. EXECUTION

### 3a. Commander's Intent

SSH was the first door locked. Now lock the rest. A fleet node with telnet installed, no firewall, and world-readable shadow files is still compromised — just through a different door. This mission establishes defence in depth: multiple layers of hardening applied uniformly via automation.

### 3b. Concept of Operations

Five sequential phases. Complete each phase before advancing. Full procedural detail is in **EXERCISES.md**.

| Phase | Task | Objective |
|-------|------|-----------|
| 1 | Assess the Damage | Inspect current package state, firewall, permissions, kernel params |
| 2 | Package Cleanup | Remove telnet and xinetd, ensure ufw present |
| 3 | Firewall Configuration | Allow SSH, enable ufw on all nodes |
| 4 | System Hardening | Deploy sysctl.conf, fix /etc/shadow permissions |
| 5 | Verify & Harden | Dry run, execute, confirm idempotency, pass all ARIA checks |

### 3c. Fleet Assets

All nodes are accessible via SSH. Credentials are uniform across the fleet. Inventory is pre-configured from Mission 1.1.

| Designation | Role | IP Address | SSH Port |
|-------------|------|------------|----------|
| `sdc-web` | Fleet Web Server | localhost | 2221 |
| `sdc-db` | Fleet Database Server | localhost | 2222 |
| `sdc-comms` | Fleet Communications Relay | localhost | 2223 |

**SSH User**: `cadet`
**Authentication**: SSH key located at `workspace/.ssh/cadet_key`

### 3d. Rules of Engagement

- Cadets must write the playbook themselves. The skeleton has TODO markers — replace them.
- A hardened `sysctl.conf` is provided at `workspace/files/sysctl-hardened.conf`. You deploy it — you do not write it.
- All changes must be applied via the playbook. Do not manually configure nodes.
- **CRITICAL**: Allow SSH through the firewall BEFORE enabling it. If you enable the firewall first, you lose access to every node. `make reset` is your recovery.

---

## 4. SUPPORT

| Resource | Function | Command |
|----------|----------|---------|
| **ARIA** | Verifies mission compliance; reports pass/fail per phase | `make test` |
| **HINTS.md** | Operational guidance if mission stalls | — |
| **Fleet Reset** | Rebuilds all fleet containers from scratch | `make reset` |
| **Module Docs** | Ansible module documentation | `ansible-doc apt` / `ansible-doc copy` / `ansible-doc file` |

Run `make test` after each phase. Do not advance until ARIA confirms the phase complete.

Consulting **HINTS.md** is authorised at Cadet rank. Using available intelligence is not weakness — it is doctrine.

---

## 5. COMMAND AND SIGNAL

**Reporting**: ARIA is your automated reporting chain. Her output is your after-action record.

**Commander's Final Order**: Neglect is the Voidborn's greatest ally. Every unnecessary service is an open port. Every inactive firewall is an invitation. Every loose permission is a foothold. Sweep every node clean. Leave nothing for the enemy to exploit.

Proceed to **EXERCISES.md** for phase-by-phase operational instructions.

---

*SDC Cyber Command — 2187 — CADET EYES ONLY*
