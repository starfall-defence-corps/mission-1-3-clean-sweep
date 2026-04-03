"""
=== STARFALL DEFENCE CORPS ACADEMY ===
ARIA Automated Verification - Mission 1.3: Clean Sweep
========================================================
"""
import os
import re
import subprocess
import yaml
import pytest


def _root_dir():
    """Return the mission root directory."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(tests_dir, "..", "..", ".."))


def _workspace_dir():
    return os.path.join(_root_dir(), "workspace")


def _playbook_path():
    return os.path.join(_workspace_dir(), "playbook.yml")


def _load_playbook():
    path = _playbook_path()
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def _run_ansible(*args, **kwargs):
    """Run an ansible command from the workspace directory."""
    timeout = kwargs.pop("timeout", 60)
    result = subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=_workspace_dir(),
    )
    return result


def _count_real_tasks(data):
    """Count non-empty tasks in the first play."""
    if not data or not isinstance(data, list) or len(data) == 0:
        return 0
    play = data[0]
    tasks = play.get("tasks") or []
    return len([t for t in tasks if t])


# -------------------------------------------------------------------
# Phase 1: Playbook structure
# -------------------------------------------------------------------

class TestPlaybookStructure:
    """ARIA verifies: Has the cadet written a valid OPORD?"""

    def test_playbook_exists(self):
        """Playbook file must exist at workspace/playbook.yml"""
        assert os.path.isfile(_playbook_path()), (
            "ARIA: No playbook detected at workspace/playbook.yml. "
            "Cadet, an operation without an OPORD is chaos. "
            "Create your playbook and try again."
        )

    def test_playbook_is_valid_yaml(self):
        """Playbook must be valid YAML"""
        path = _playbook_path()
        if not os.path.isfile(path):
            pytest.skip("Playbook does not exist yet")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None, (
            "ARIA: Playbook is empty. A blank OPORD protects no one."
        )

    def test_playbook_has_tasks(self):
        """Playbook must contain at least 5 real tasks"""
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        count = _count_real_tasks(data)
        assert count >= 5, (
            f"ARIA: Insufficient tasks in playbook. Found {count} "
            f"task(s) — expected at least 5 (remove telnet, remove xinetd, "
            f"firewall allow SSH, enable firewall, deploy sysctl, fix shadow). "
            f"Complete the TODO sections in your playbook."
        )

    def test_playbook_has_handler(self):
        """Playbook must contain a sysctl handler"""
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        play = data[0]
        handlers = play.get("handlers") or []
        real_handlers = [h for h in handlers if h]
        assert len(real_handlers) >= 1, (
            "ARIA: No handlers found in playbook. "
            "When sysctl configuration changes, the new settings must be "
            "loaded. Add a handler that runs 'sysctl --system'."
        )


# -------------------------------------------------------------------
# Phase 2: Package cleanup
# -------------------------------------------------------------------

class TestPackageCleanup:
    """ARIA verifies: Have unnecessary packages been removed?"""

    @pytest.fixture(autouse=True)
    def _require_playbook(self):
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        if _count_real_tasks(data) < 5:
            pytest.skip("Playbook tasks not yet complete")

    def test_telnet_removed(self):
        """telnet package must be absent on all nodes"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "dpkg -l telnet 2>/dev/null | grep -q '^ii' && echo INSTALLED || echo ABSENT",
        )
        for host in ["sdc-web", "sdc-db", "sdc-comms"]:
            # Check this host's output section
            if host in result.stdout:
                section = result.stdout.split(host)[1].split("sdc-")[0] if "sdc-" in result.stdout.split(host)[1] else result.stdout.split(host)[1]
                assert "INSTALLED" not in section, (
                    f"ARIA: telnet is still installed on {host}. "
                    f"This package transmits data in cleartext. Remove it."
                )

    def test_xinetd_removed(self):
        """xinetd package must be absent on all nodes"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "dpkg -l xinetd 2>/dev/null | grep -q '^ii' && echo INSTALLED || echo ABSENT",
        )
        for host in ["sdc-web", "sdc-db", "sdc-comms"]:
            if host in result.stdout:
                section = result.stdout.split(host)[1].split("sdc-")[0] if "sdc-" in result.stdout.split(host)[1] else result.stdout.split(host)[1]
                assert "INSTALLED" not in section, (
                    f"ARIA: xinetd is still installed on {host}. "
                    f"This legacy super-server daemon is an unnecessary attack surface. Remove it."
                )

    def test_ufw_installed(self):
        """ufw package must be present on all nodes"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "dpkg -l ufw 2>/dev/null | grep -q '^ii' && echo INSTALLED || echo ABSENT",
        )
        assert "ABSENT" not in result.stdout or result.returncode != 0, (
            "ARIA: ufw is not installed on one or more nodes. "
            "Ensure the firewall package is present."
        )


# -------------------------------------------------------------------
# Phase 3: Firewall
# -------------------------------------------------------------------

class TestFirewall:
    """ARIA verifies: Is the firewall active and configured?"""

    @pytest.fixture(autouse=True)
    def _require_playbook(self):
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        if _count_real_tasks(data) < 5:
            pytest.skip("Playbook tasks not yet complete")

    def test_ufw_active(self):
        """ufw must be active on all nodes"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "ufw status | head -1",
        )
        assert result.returncode == 0, (
            "ARIA: Could not check firewall status. "
            "Ensure ufw is installed and your playbook has run."
        )
        for host in ["sdc-web", "sdc-db", "sdc-comms"]:
            if host in result.stdout:
                section = result.stdout.split(host)[1].split("sdc-")[0] if "sdc-" in result.stdout.split(host)[1] else result.stdout.split(host)[1]
                assert "inactive" not in section.lower(), (
                    f"ARIA: Firewall is inactive on {host}. "
                    f"Enable ufw. Remember to allow SSH first."
                )

    def test_ufw_ssh_allowed(self):
        """SSH (port 22) must be allowed through ufw"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "ufw status | grep -E '22/(tcp|udp)|22 '",
        )
        assert result.returncode == 0, (
            "ARIA: SSH is not allowed through the firewall on one or more nodes. "
            "Add a ufw rule to allow port 22/tcp before enabling the firewall."
        )


# -------------------------------------------------------------------
# Phase 4: System hardening
# -------------------------------------------------------------------

class TestSystemHardening:
    """ARIA verifies: Is the system hardened?"""

    @pytest.fixture(autouse=True)
    def _require_playbook(self):
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        if _count_real_tasks(data) < 5:
            pytest.skip("Playbook tasks not yet complete")

    def test_sysctl_deployed(self):
        """Hardened sysctl.conf must be deployed to all nodes"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "test -f /etc/sysctl.d/99-fleet.conf && echo EXISTS || echo MISSING",
        )
        assert "MISSING" not in result.stdout, (
            "ARIA: Hardened sysctl configuration not found on one or more nodes. "
            "Copy files/sysctl-hardened.conf to /etc/sysctl.d/99-fleet.conf."
        )

    def test_sysctl_ip_forward_disabled(self):
        """IP forwarding must be disabled (net.ipv4.ip_forward = 0)"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "sysctl net.ipv4.ip_forward",
        )
        assert result.returncode == 0, (
            "ARIA: Could not read sysctl settings."
        )
        # Check all nodes report ip_forward = 0
        for host in ["sdc-web", "sdc-db", "sdc-comms"]:
            if host in result.stdout:
                section = result.stdout.split(host)[1].split("sdc-")[0] if "sdc-" in result.stdout.split(host)[1] else result.stdout.split(host)[1]
                assert "= 1" not in section, (
                    f"ARIA: IP forwarding is still enabled on {host}. "
                    f"Deploy the hardened sysctl.conf and run the handler "
                    f"to apply settings."
                )

    def test_shadow_permissions(self):
        """/etc/shadow must have permissions 0640 or stricter"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "stat -c '%a' /etc/shadow",
        )
        assert result.returncode == 0, (
            "ARIA: Could not check /etc/shadow permissions."
        )
        for host in ["sdc-web", "sdc-db", "sdc-comms"]:
            if host in result.stdout:
                section = result.stdout.split(host)[1].split("sdc-")[0] if "sdc-" in result.stdout.split(host)[1] else result.stdout.split(host)[1]
                # 640 is correct; 600 is also acceptable (stricter)
                assert "644" not in section and "666" not in section and "777" not in section, (
                    f"ARIA: /etc/shadow has overly permissive permissions on {host}. "
                    f"Set to 0640 (owner: root, group: shadow)."
                )


# -------------------------------------------------------------------
# Phase 5: Idempotency
# -------------------------------------------------------------------

class TestIdempotency:
    """ARIA verifies: Is the playbook idempotent?"""

    def test_playbook_is_idempotent(self):
        """Running the playbook must show changed=0"""
        data = _load_playbook()
        if data is None:
            pytest.skip("Playbook does not exist yet")
        if _count_real_tasks(data) < 5:
            pytest.skip("Playbook tasks not yet complete")

        # Check if hardening has been applied — skip if not
        check = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "ufw status | head -1",
        )
        if "inactive" in check.stdout.lower() or check.returncode != 0:
            pytest.skip(
                "Fleet not yet hardened — run your playbook first"
            )

        result = _run_ansible(
            "ansible-playbook", "playbook.yml",
        )
        assert result.returncode == 0, (
            "ARIA: Playbook failed. "
            "Fix the errors reported by 'ansible-playbook playbook.yml'."
        )
        changed_match = re.findall(r"changed=(\d+)", result.stdout)
        total_changed = sum(int(c) for c in changed_match)
        assert total_changed == 0, (
            f"ARIA: Idempotency failure. Playbook changed "
            f"{total_changed} task(s). A well-written playbook should make "
            f"no changes when run against an already-configured system. "
            f"Common cause: 'command' or 'shell' tasks always report changed. "
            f"Use 'creates' parameter or convert to a proper module."
        )
