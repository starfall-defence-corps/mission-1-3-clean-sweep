---
CLASSIFICATION: CADET EYES ONLY
MISSION: 1.3 — CLEAN SWEEP
DOCUMENT: EXERCISES — Phase-by-Phase Operational Instructions
---

# EXERCISES — MISSION 1.3: CLEAN SWEEP

Complete each phase in sequence. Run `make test` after each phase. Do not advance until ARIA confirms compliance.

**Two directories, two purposes:**

- **Ansible commands** (`ansible`, `ansible-playbook`): Run from `workspace/` where `ansible.cfg` lives.
- **Make commands** (`make test`, `make reset`): Run from the **project root** (where the `Makefile` lives).

When a phase says "Run ARIA's Verification", return to the project root first:

```bash
cd ..        # from workspace/ back to project root
make test
cd workspace # return to workspace for the next phase
```

---

## PHASE 0: Launch the Fleet

> Before any mission can begin, your fleet must be online.

### Step 0.1 — Start the Fleet

From the **project root directory** (not `workspace/`), run:

```bash
make setup
```

Wait for the output to confirm:

```
  Fleet Status: 3 nodes ONLINE
```

### Step 0.2 — Activate the Python Environment

`make setup` creates a Python virtual environment with Ansible and testing tools. **Activate it** before running any Ansible commands:

```bash
source venv/bin/activate
```

Your terminal prompt will show `(venv)` when active. You need to do this once per terminal session. If you open a new terminal, activate again.

### Step 0.3 — If Things Go Wrong

If containers are in a bad state or you need a clean start at any point:

```bash
make reset
```

This destroys all containers and rebuilds from scratch. Your work in `workspace/` is preserved.

---

## PHASE 1: Assess the Damage

> Before cleaning, understand the mess. Inspect every node for unnecessary packages, firewall state, file permissions, and kernel parameters.

### What You Are Doing

You will use ad-hoc commands to survey the current state of the fleet. This builds your situational awareness before writing a single line of playbook code.

All Ansible commands in this phase are run from `workspace/`.

### Step 1.1 — Change Into the Workspace Directory

```bash
cd workspace
```

### Step 1.2 — Verify Fleet Connectivity

```bash
ansible all -m ping
```

All three nodes should return `SUCCESS`.

### Step 1.3 — Check for Unnecessary Packages

**Check if telnet is installed:**

```bash
ansible all -m shell -a "dpkg -l telnet 2>/dev/null | grep '^ii' || echo 'not installed'"
```

You will see telnet is installed on every node. This package transmits credentials in cleartext.

**Check if xinetd is installed:**

```bash
ansible all -m shell -a "dpkg -l xinetd 2>/dev/null | grep '^ii' || echo 'not installed'"
```

xinetd is a legacy service launcher — a wide attack surface with no modern use.

### Step 1.4 — Check Firewall Status

```bash
ansible all -m shell -a "ufw status"
```

You will see `Status: inactive` on every node. The firewall is installed but not running. The fleet has no active network filtering.

### Step 1.5 — Check Kernel Parameters

```bash
ansible all -m shell -a "sysctl net.ipv4.ip_forward net.ipv4.conf.all.accept_redirects net.ipv4.tcp_syncookies"
```

You will see:
- `ip_forward = 1` — fleet nodes are acting as routers (they shouldn't be)
- `accept_redirects = 1` — vulnerable to route poisoning
- `tcp_syncookies = 0` or `1` — check the current value

### Step 1.6 — Check File Permissions

```bash
ansible all -m shell -a "stat -c '%a %U %G' /etc/shadow"
```

You should see `644 root shadow` — the permissions are too loose. `/etc/shadow` contains password hashes and should be `640` at most.

### Step 1.7 — Run ARIA's Verification

```bash
cd ..
make test
cd workspace
```

Phase 1 checks that the playbook exists and has valid structure.

---

## PHASE 2: Package Cleanup

> Remove what shouldn't be there. Ensure what should be there stays.

### What You Are Doing

You will write tasks to remove telnet and xinetd, and ensure ufw remains installed.

### Step 2.1 — Read Module Documentation

```bash
ansible-doc apt
```

Focus on the `name` and `state` parameters. The `state` parameter accepts:
- `present` — ensure the package is installed
- `absent` — ensure the package is removed
- `latest` — ensure the latest version is installed

### Step 2.2 — Task 1: Remove telnet

Open `workspace/playbook.yml` and find the first TODO block. Replace it with a task that:

1. Uses the `ansible.builtin.apt` module
2. Sets `name: telnet`
3. Sets `state: absent`

**Example for removing a DIFFERENT package (not your task):**

```yaml
    - name: Remove finger
      ansible.builtin.apt:
        name: finger
        state: absent
```

### Step 2.3 — Task 2: Remove xinetd

Find the second TODO block. Write a task following the same pattern to remove xinetd.

### Step 2.4 — Task 3: Ensure ufw is installed

Find the third TODO block. Write a task to ensure ufw is present:

```yaml
    - name: Ensure ufw is installed
      ansible.builtin.apt:
        name: ufw
        state: present
```

### Step 2.5 — Verify Syntax and Run ARIA

```bash
ansible-playbook playbook.yml --syntax-check
cd ..
make test
cd workspace
```

---

## PHASE 3: Firewall Configuration

> The firewall is present but inactive. Enable it — but allow SSH first, or you lock yourself out of every node.

### What You Are Doing

You will write two tasks: one to allow SSH through the firewall, and one to enable the firewall. The order is critical.

### Step 3.1 — Read the ufw Module Documentation

The `community.general.ufw` module manages firewall rules. Key parameters:

| Parameter | Purpose |
|-----------|---------|
| `rule` | `allow`, `deny`, `reject` |
| `port` | Port number (as string) |
| `proto` | Protocol: `tcp`, `udp`, `any` |
| `state` | `enabled`, `disabled`, `reloaded`, `reset` |

### Step 3.2 — Task 4a: Allow SSH Through the Firewall

Find the Task 4 TODO block. Write a task that allows SSH:

```yaml
    - name: Allow SSH through firewall
      community.general.ufw:
        rule: allow
        port: '22'
        proto: tcp
```

### Step 3.3 — Task 4b: Enable ufw

Immediately after the SSH allow task, write a task that enables the firewall:

```yaml
    - name: Enable firewall
      community.general.ufw:
        state: enabled
```

**WARNING**: If you reverse the order (enable before allow), the firewall blocks SSH and you lose access. Recovery: `make reset` from the project root.

### Step 3.4 — Verify and Run ARIA

```bash
ansible-playbook playbook.yml --syntax-check
cd ..
make test
cd workspace
```

---

## PHASE 4: System Hardening

> Deploy hardened kernel parameters and fix file permissions.

### What You Are Doing

You will copy a pre-written sysctl configuration file to all nodes using the `copy` module, add a handler to apply the settings, and fix `/etc/shadow` permissions using the `file` module.

### Step 4.1 — Examine the Hardened sysctl.conf

Read the provided configuration file:

```bash
cat files/sysctl-hardened.conf
```

This file disables IP forwarding, ignores ICMP redirects, enables SYN flood protection, and logs suspicious packets. You do not write this file — you deploy it.

### Step 4.2 — Read the copy Module Documentation

```bash
ansible-doc copy
```

Key parameters:

| Parameter | Purpose |
|-----------|---------|
| `src` | Path to the source file (on the control node) |
| `dest` | Path on the target node |
| `owner` | File owner |
| `group` | File group |
| `mode` | File permissions (e.g., `'0644'`) |

### Step 4.3 — Task 5: Deploy sysctl.conf

Find the Task 5 TODO block. Write a task that:

1. Uses `ansible.builtin.copy`
2. Copies `files/sysctl-hardened.conf` to `/etc/sysctl.d/99-fleet.conf`
3. Sets owner: `root`, group: `root`, mode: `'0644'`
4. Includes `notify: Apply sysctl` to trigger the handler

**Example for copying a DIFFERENT file:**

```yaml
    - name: Deploy NTP configuration
      ansible.builtin.copy:
        src: files/ntp.conf
        dest: /etc/ntp.conf
        owner: root
        group: root
        mode: '0644'
      notify: Restart NTP
```

### Step 4.4 — Write the Handler

Find the handler TODO at the bottom of the playbook. Write a handler that applies sysctl settings:

```yaml
  handlers:
    - name: Apply sysctl
      ansible.builtin.command:
        cmd: sysctl --system
```

The `sysctl --system` command reloads all configuration files from `/etc/sysctl.d/`.

### Step 4.5 — Read the file Module Documentation

```bash
ansible-doc file
```

The `file` module manages file attributes (permissions, ownership) without changing content.

### Step 4.6 — Task 6: Fix /etc/shadow Permissions

Find the Task 6 TODO block. Write a task that:

1. Uses `ansible.builtin.file`
2. Sets `path: /etc/shadow`
3. Sets `owner: root`, `group: shadow`, `mode: '0640'`

### Step 4.7 — Verify and Run ARIA

```bash
ansible-playbook playbook.yml --syntax-check
cd ..
make test
cd workspace
```

---

## PHASE 5: Verify & Harden

> Execute the complete playbook. Verify all changes. Confirm idempotency.

### Step 5.1 — Dry Run

```bash
ansible-playbook playbook.yml --check --diff
```

Review the predicted changes. You should see packages being removed, firewall rules being set, files being copied, and permissions being changed.

### Step 5.2 — Execute for Real

```bash
ansible-playbook playbook.yml
```

Watch the output. On the first run you should see multiple `changed` tasks per host.

### Step 5.3 — Verify the Changes

Run the same ad-hoc commands from Phase 1 to confirm:

```bash
# Packages removed?
ansible all -m shell -a "dpkg -l telnet 2>/dev/null | grep '^ii' || echo 'CLEAN'"
ansible all -m shell -a "dpkg -l xinetd 2>/dev/null | grep '^ii' || echo 'CLEAN'"

# Firewall active?
ansible all -m shell -a "ufw status"

# Kernel hardened?
ansible all -m shell -a "sysctl net.ipv4.ip_forward"

# Permissions fixed?
ansible all -m shell -a "stat -c '%a %U %G' /etc/shadow"
```

### Step 5.4 — Idempotency Check

Run the playbook a second time:

```bash
ansible-playbook playbook.yml
```

You should see `changed=0` for every host. If any task still reports `changed`, investigate:
- `command` and `shell` tasks always report `changed` unless you add conditions
- The sysctl handler should only fire when the file actually changes

### Step 5.5 — Final ARIA Verification

```bash
cd ..
make test
```

All five phases must pass.

---

## MISSION COMPLETE — DEBRIEF CHECKLIST

Before closing this mission, confirm the following:

- [ ] Identified unnecessary packages (telnet, xinetd) on all nodes
- [ ] Verified firewall was inactive and kernel unhardened
- [ ] Removed telnet and xinetd using `apt` module
- [ ] Allowed SSH through firewall before enabling it
- [ ] Enabled ufw on all nodes
- [ ] Deployed hardened sysctl.conf using `copy` module
- [ ] Applied sysctl settings via handler
- [ ] Fixed /etc/shadow permissions using `file` module
- [ ] All changes verified with ad-hoc commands
- [ ] Second playbook run produced `changed=0` (idempotent)
- [ ] `make test` — all ARIA checks pass

**What you learned in this mission:**

- [ ] Package management with `apt` module (`present` vs `absent`)
- [ ] Firewall management with `community.general.ufw`
- [ ] File deployment with `copy` module
- [ ] File permissions with `file` module
- [ ] Running commands with `command` module (and why to avoid it when a module exists)
- [ ] Defence in depth — multiple hardening layers in one playbook
- [ ] Order of operations matters (SSH allow before firewall enable)

---

*SDC Cyber Command — 2187 — CADET EYES ONLY*
