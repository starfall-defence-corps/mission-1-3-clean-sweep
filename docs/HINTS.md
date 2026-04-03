# Mission 1.3: Clean Sweep — Hints & Troubleshooting Guide

**Rank**: Cadet (Maximum Scaffolding)

This guide is your safety net. Read the relevant section carefully before asking for help.

---

## Phase 1 Hints: Assessing the Damage

**Reading `dpkg -l` output:**

The `dpkg -l` command lists installed packages. Lines starting with `ii` indicate an installed package:

```
ii  telnet    0.17-44build1    amd64    basic telnet client
```

If a package is not installed, `dpkg -l` returns nothing or an error. The ad-hoc command in the exercises handles this with a fallback `echo`.

**Reading `ufw status` output:**

When the firewall is inactive:
```
Status: inactive
```

When active with rules:
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
```

---

## Phase 2 Hints: Package Management

**The `apt` module — removing a package:**

```yaml
    - name: Remove a package
      ansible.builtin.apt:
        name: package-name
        state: absent
```

That is the entire task. No additional parameters needed for removal. The `absent` state ensures the package is not installed — if it is already absent, the task reports `ok` (idempotent).

**The `apt` module — ensuring a package is present:**

```yaml
    - name: Ensure a package is installed
      ansible.builtin.apt:
        name: package-name
        state: present
```

`present` installs if missing, does nothing if already installed.

**"Could not open lock file" error:**

If you see this, another apt process is running on the container. Wait a few seconds and try again, or run `make reset` to get clean containers.

---

## Phase 3 Hints: Firewall Configuration

**The `community.general.ufw` module:**

This module has two modes of operation:
1. **Rule mode** — add allow/deny rules
2. **State mode** — enable/disable the firewall

**Adding a rule:**

```yaml
    - name: Allow HTTP
      community.general.ufw:
        rule: allow
        port: '80'
        proto: tcp
```

Note: `port` must be a string (quoted), not an integer.

**Enabling the firewall:**

```yaml
    - name: Enable firewall
      community.general.ufw:
        state: enabled
```

**CRITICAL — Order matters:**

```yaml
    # CORRECT ORDER:
    - name: Allow SSH          # ← FIRST: punch a hole for SSH
      community.general.ufw:
        rule: allow
        port: '22'
        proto: tcp

    - name: Enable firewall    # ← THEN: turn on the firewall
      community.general.ufw:
        state: enabled
```

If you enable the firewall without allowing SSH first, the firewall blocks your connection and Ansible can no longer reach the nodes.

**Recovery from lockout:**

If you accidentally enable the firewall without the SSH rule:

```bash
make reset
```

This rebuilds the containers from scratch. Your playbook is preserved — fix the order, then run again.

**"No module named community.general" error:**

The `community.general` collection should be available by default with modern Ansible installations. If you get this error, install it:

```bash
ansible-galaxy collection install community.general
```

---

## Phase 4 Hints: System Hardening

**The `copy` module — deploying a file:**

```yaml
    - name: Deploy configuration file
      ansible.builtin.copy:
        src: files/my-config.conf
        dest: /etc/target-path/my-config.conf
        owner: root
        group: root
        mode: '0644'
      notify: My Handler Name
```

The `src` path is relative to the playbook's location. Since your playbook is in `workspace/` and the file is in `workspace/files/`, the src path is `files/sysctl-hardened.conf`.

**The `file` module — setting permissions:**

```yaml
    - name: Set correct permissions on a file
      ansible.builtin.file:
        path: /etc/some/file
        owner: root
        group: somegroup
        mode: '0640'
```

The `file` module only manages attributes (permissions, ownership, state). It does NOT copy or create file content. Use `copy` or `template` for that.

**For /etc/shadow:**

The correct permissions are:
- Owner: `root`
- Group: `shadow`
- Mode: `0640`

This allows root full access and the shadow group read access (needed by authentication tools), while preventing all other users from reading password hashes.

**The `command` module and idempotency:**

The `command` module always reports `changed` because Ansible cannot know whether the command actually changed anything. When used in a handler, this is acceptable — the handler only fires when the notifying task actually changed something.

If you use `command` as a regular task (not a handler), you must add `changed_when: false` or a conditional to make it idempotent:

```yaml
    - name: Check something
      ansible.builtin.command: some-command
      changed_when: false   # This task never changes state
```

For this mission, `sysctl --system` is in a handler, so idempotency is handled by the handler mechanism itself.

---

## Phase 5 Hints: Idempotency

**Common causes of idempotency failure:**

1. **`command` or `shell` tasks** — always report `changed` unless you add `changed_when: false`. Move them to handlers if possible.

2. **Package already absent** — the `apt` module handles this correctly. `state: absent` on an already-absent package reports `ok`, not `changed`.

3. **ufw rules** — the `ufw` module is idempotent. Adding the same rule twice reports `ok` on the second run.

4. **File permissions** — the `file` module checks current permissions before acting. If already correct, it reports `ok`.

**If your second run shows `changed` on the sysctl handler:**

The handler fires only when the `copy` task reports `changed`. If the file hasn't changed, the handler should NOT fire. Ensure your `copy` task has the correct `src` and `dest` — if the deployed file differs from the source (even trailing newlines), the task reports `changed` every time.

---

## Connection Hints

**"Connection refused"**
The containers are not running. Start them with `make setup`.

**"Permission denied (publickey)"**
Check that `workspace/.ssh/cadet_key` exists. Run `make setup` to regenerate if missing.

---

## WSL (Windows Subsystem for Linux) Hints

**"Ansible is ignoring my ansible.cfg"**
On WSL, set the environment variable:
```
export ANSIBLE_CONFIG=$(pwd)/ansible.cfg
```

---

## General Troubleshooting

**If everything is broken:**
```
make reset
```

**Quick diagnostic sequence:**
1. `docker ps` — are containers running?
2. `ansible all -m ping` — can Ansible reach them?
3. `ansible-playbook playbook.yml --syntax-check` — valid YAML?
4. Check indentation in `workspace/playbook.yml`

---

## Useful Commands Reference

| Command | Purpose |
|---------|---------|
| `ansible-doc apt` | Package module documentation |
| `ansible-doc copy` | File copy module documentation |
| `ansible-doc file` | File permissions module documentation |
| `ansible-doc community.general.ufw` | Firewall module documentation |
| `ansible-playbook playbook.yml --syntax-check` | Validate YAML |
| `ansible-playbook playbook.yml --check --diff` | Dry run with diff |
| `ansible-playbook playbook.yml` | Execute the playbook |
| `ansible all -m ping` | Test connectivity |

---

## CRITICAL SPOILER — Full Playbook Solution

> **STOP.** Only read this section if you are truly stuck and have exhausted all other hints. Writing the playbook yourself is the entire point of this mission.

> **LAST WARNING.** Scroll down only if you have spent real effort and need to compare your work to a working example.

<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>

```yaml
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
```

---

*SDC Cyber Command — 2187 — CADET EYES ONLY*
