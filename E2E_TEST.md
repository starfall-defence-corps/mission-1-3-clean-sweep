# Mission 1.3: Clean Sweep — E2E Manual Test Script

**Purpose**: Verify the entire student workflow works end-to-end.
**Time**: ~15 minutes.
**Prerequisites**: Docker running, ports 2221-2223 free.

---

## 1. Setup

```bash
cd ~/projects/starfall-defence-corps/mission-1-3-clean-sweep
make destroy 2>/dev/null; true
make setup
```

**Expected**: All 3 nodes ONLINE. No errors.

```bash
cd workspace
ansible all -m ping
```

**Expected**: All 3 nodes return `SUCCESS` with `"ping": "pong"`.

---

## 2. Verify Starting State (Misconfigurations Present)

```bash
# Telnet should be installed
ansible all -m shell -a "dpkg -l telnet 2>/dev/null | grep '^ii' && echo INSTALLED || echo ABSENT"
```
**Expected**: `INSTALLED` on all 3 nodes.

```bash
# xinetd should be installed
ansible all -m shell -a "dpkg -l xinetd 2>/dev/null | grep '^ii' && echo INSTALLED || echo ABSENT"
```
**Expected**: `INSTALLED` on all 3 nodes.

```bash
# Firewall should be inactive
ansible all -m shell -a "ufw status | head -1"
```
**Expected**: `Status: inactive` on all 3 nodes.

```bash
# IP forwarding should be enabled (bad)
ansible all -m shell -a "sysctl net.ipv4.ip_forward"
```
**Expected**: `net.ipv4.ip_forward = 1` on all nodes.

```bash
# Shadow permissions should be too loose
ansible all -m shell -a "stat -c '%a' /etc/shadow"
```
**Expected**: `644` on all nodes.

---

## 3. Run ARIA Before Solution (Should Show Deficiencies)

```bash
cd ..
make test
```

**Expected**: Phase 1 partially passes (playbook exists, valid YAML). Later phases show deficiencies or skips.

```bash
cd workspace
```

---

## 4. Apply Solution

Overwrite the playbook with the complete solution:

```bash
cat > playbook.yml << 'PLAYBOOK'
---
- name: Clean Sweep — Fleet Hardening
  hosts: all
  become: true

  tasks:
    - name: Remove telnet
      ansible.builtin.apt:
        name: telnet
        state: absent

    - name: Remove xinetd
      ansible.builtin.apt:
        name: xinetd
        state: absent

    - name: Ensure ufw is installed
      ansible.builtin.apt:
        name: ufw
        state: present

    - name: Allow SSH through firewall
      community.general.ufw:
        rule: allow
        port: '22'
        proto: tcp

    - name: Enable firewall
      community.general.ufw:
        state: enabled

    - name: Deploy hardened sysctl configuration
      ansible.builtin.copy:
        src: files/sysctl-hardened.conf
        dest: /etc/sysctl.d/99-fleet.conf
        owner: root
        group: root
        mode: '0644'
      notify: Apply sysctl

    - name: Fix /etc/shadow permissions
      ansible.builtin.file:
        path: /etc/shadow
        owner: root
        group: shadow
        mode: '0640'

  handlers:
    - name: Apply sysctl
      ansible.builtin.command:
        cmd: sysctl --system
PLAYBOOK
```

---

## 5. Syntax Check

```bash
ansible-playbook playbook.yml --syntax-check
```

**Expected**: No errors. Output contains `playbook: playbook.yml`.

---

## 6. Dry Run

```bash
ansible-playbook playbook.yml --check --diff
```

**Expected**: Shows predicted changes. No errors. Return code 0.

---

## 7. Execute Playbook (First Run)

```bash
ansible-playbook playbook.yml
```

**Expected**:
- `changed` on telnet removal, xinetd removal
- `changed` on ufw allow SSH and enable
- `changed` on sysctl copy + handler fires
- `changed` on shadow permissions
- Play recap shows `changed` > 0 for each host

---

## 8. Verify Changes Applied

```bash
# Telnet removed
ansible all -m shell -a "dpkg -l telnet 2>/dev/null | grep '^ii' && echo INSTALLED || echo ABSENT"
```
**Expected**: `ABSENT` on all nodes.

```bash
# xinetd removed
ansible all -m shell -a "dpkg -l xinetd 2>/dev/null | grep '^ii' && echo INSTALLED || echo ABSENT"
```
**Expected**: `ABSENT` on all nodes.

```bash
# Firewall active
ansible all -m shell -a "ufw status | head -1"
```
**Expected**: `Status: active` on all nodes.

```bash
# SSH allowed
ansible all -m shell -a "ufw status | grep 22"
```
**Expected**: Shows `22/tcp ALLOW Anywhere` on all nodes.

```bash
# IP forwarding disabled
ansible all -m shell -a "sysctl net.ipv4.ip_forward"
```
**Expected**: `net.ipv4.ip_forward = 0` on all nodes.

```bash
# Shadow permissions fixed
ansible all -m shell -a "stat -c '%a' /etc/shadow"
```
**Expected**: `640` on all nodes.

---

## 9. Idempotency Check (Second Run)

```bash
ansible-playbook playbook.yml
```

**Expected**: `changed=0` on ALL hosts. No handler fires.

---

## 10. Full ARIA Verification

```bash
cd ..
make test
```

**Expected**: All 5 phases pass. Exit code 0. "Mission 1.3 status: COMPLETE".

---

## 11. Edge Case Tests

### 11a. Missing sysctl file

```bash
cd workspace
mv files/sysctl-hardened.conf files/sysctl-hardened.conf.bak
ansible-playbook playbook.yml 2>&1 | tail -5
```

**Expected**: Task fails with "could not find" error. Playbook does NOT silently skip.

```bash
mv files/sysctl-hardened.conf.bak files/sysctl-hardened.conf
```

### 11b. Firewall enable without SSH allow (lockout scenario)

```bash
cd ..
make reset
cd workspace
```

Write a BAD playbook that enables firewall before allowing SSH:

```bash
cat > /tmp/bad-playbook.yml << 'EOF'
---
- name: Bad order
  hosts: all
  become: true
  tasks:
    - name: Enable firewall FIRST (bad)
      community.general.ufw:
        state: enabled
EOF
ansible-playbook /tmp/bad-playbook.yml 2>&1 | tail -10
```

**Expected**: Either task fails (connection lost) or subsequent commands fail. This validates that order matters.

```bash
cd ..
make reset
cd workspace
```

### 11c. Partial playbook (only 3 tasks)

```bash
cat > /tmp/partial.yml << 'EOF'
---
- name: Partial
  hosts: all
  become: true
  tasks:
    - name: Remove telnet
      ansible.builtin.apt:
        name: telnet
        state: absent
    - name: Remove xinetd
      ansible.builtin.apt:
        name: xinetd
        state: absent
    - name: Ensure ufw
      ansible.builtin.apt:
        name: ufw
        state: present
EOF
cp /tmp/partial.yml playbook.yml
cd ..
make test 2>&1 | grep -E "(✓|✗|○|deficient|verified)"
```

**Expected**: Phase 1 fails (insufficient tasks — found 3, expected >= 5). Later phases skip.

### 11d. Restore solution and verify recovery

```bash
cd workspace
cat > playbook.yml << 'PLAYBOOK'
---
- name: Clean Sweep — Fleet Hardening
  hosts: all
  become: true

  tasks:
    - name: Remove telnet
      ansible.builtin.apt:
        name: telnet
        state: absent

    - name: Remove xinetd
      ansible.builtin.apt:
        name: xinetd
        state: absent

    - name: Ensure ufw is installed
      ansible.builtin.apt:
        name: ufw
        state: present

    - name: Allow SSH through firewall
      community.general.ufw:
        rule: allow
        port: '22'
        proto: tcp

    - name: Enable firewall
      community.general.ufw:
        state: enabled

    - name: Deploy hardened sysctl configuration
      ansible.builtin.copy:
        src: files/sysctl-hardened.conf
        dest: /etc/sysctl.d/99-fleet.conf
        owner: root
        group: root
        mode: '0644'
      notify: Apply sysctl

    - name: Fix /etc/shadow permissions
      ansible.builtin.file:
        path: /etc/shadow
        owner: root
        group: shadow
        mode: '0640'

  handlers:
    - name: Apply sysctl
      ansible.builtin.command:
        cmd: sysctl --system
PLAYBOOK
ansible-playbook playbook.yml
cd ..
make test
```

**Expected**: All phases pass again.

---

## 12. Cleanup

```bash
make destroy
```

**Expected**: Containers stopped, SSH keys removed, venv removed.

---

## Test Summary

| # | Test | Expected |
|---|------|----------|
| 1 | Setup | 3 nodes online |
| 2 | Starting state | Misconfigs present |
| 3 | ARIA before solution | Deficiencies shown |
| 4-6 | Solution + syntax + dry run | No errors |
| 7 | First run | Changes applied |
| 8 | Verify changes | All hardening confirmed |
| 9 | Second run | changed=0 (idempotent) |
| 10 | ARIA after solution | All phases pass |
| 11a | Missing file | Task fails cleanly |
| 11b | Bad firewall order | Lockout/failure |
| 11c | Partial playbook | Insufficient tasks detected |
| 11d | Recovery | Full pass after fix |
| 12 | Cleanup | Everything torn down |
