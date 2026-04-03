# Mission 1.3: Clean Sweep — Progress Tracker

**Rank**: Cadet
**Mission Progress**: 3 of 5 toward Ensign

Check each item off as you complete it. If a phase is blocked, see `docs/HINTS.md`.

---

## Phase 1: Assess the Damage

- [ ] Fleet nodes are online (`make setup` succeeded)
- [ ] Verified connectivity with `ansible all -m ping`
- [ ] Confirmed telnet is installed on all nodes
- [ ] Confirmed xinetd is installed on all nodes
- [ ] Confirmed firewall is inactive (`ufw status` shows inactive)
- [ ] Confirmed IP forwarding is enabled (should be disabled)
- [ ] Confirmed /etc/shadow has overly permissive permissions (644)

---

## Phase 2: Package Cleanup

- [ ] Completed Task 1: Remove telnet (`state: absent`)
- [ ] Completed Task 2: Remove xinetd (`state: absent`)
- [ ] Completed Task 3: Ensure ufw is installed (`state: present`)
- [ ] Playbook passes syntax check

---

## Phase 3: Firewall Configuration

- [ ] Completed Task 4a: Allow SSH through firewall (rule: allow, port 22)
- [ ] Completed Task 4b: Enable ufw (state: enabled)
- [ ] Confirmed SSH allow rule comes BEFORE firewall enable
- [ ] Playbook still passes syntax check

---

## Phase 4: System Hardening

- [ ] Reviewed `files/sysctl-hardened.conf` contents
- [ ] Completed Task 5: Deploy sysctl.conf via `copy` module
- [ ] Added `notify: Apply sysctl` to the copy task
- [ ] Wrote the `Apply sysctl` handler (`sysctl --system`)
- [ ] Completed Task 6: Fix /etc/shadow permissions (0640, root:shadow)

---

## Phase 5: Verify & Harden

- [ ] Dry run succeeded (`ansible-playbook playbook.yml --check --diff`)
- [ ] Playbook executed successfully — changes applied on all nodes
- [ ] Verified: telnet and xinetd removed
- [ ] Verified: firewall active with SSH allowed
- [ ] Verified: IP forwarding disabled (sysctl applied)
- [ ] Verified: /etc/shadow permissions corrected
- [ ] Second run is idempotent — `changed=0` on all hosts
- [ ] `make test` — all ARIA checks pass

---

## Verification

- [ ] `make test` — all ARIA checks pass
