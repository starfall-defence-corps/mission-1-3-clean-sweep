"""
ARIA Custom Test Reporter
Provides color-coded, phase-grouped output for mission verification.

Writes all output to stderr so check-work.sh can discard pytest's
default stdout while preserving our formatted display.
"""
import os
import pytest
import sys

# -- Phase and test name mappings -------------------------------------------

PHASES = {
    "TestPlaybookStructure": ("1", "OPORD Structure"),
    "TestPackageCleanup":    ("2", "Package Cleanup"),
    "TestFirewall":          ("3", "Firewall Status"),
    "TestSystemHardening":   ("4", "System Hardening"),
    "TestIdempotency":       ("5", "Idempotency"),
}

FRIENDLY = {
    "test_playbook_exists":             "Playbook file exists",
    "test_playbook_is_valid_yaml":      "Playbook is valid YAML",
    "test_playbook_has_tasks":          "Playbook contains sufficient tasks",
    "test_playbook_has_handler":        "Playbook contains sysctl handler",
    "test_telnet_removed":              "telnet package removed",
    "test_xinetd_removed":              "xinetd package removed",
    "test_ufw_installed":               "ufw package installed",
    "test_ufw_active":                  "Firewall is active",
    "test_ufw_ssh_allowed":             "SSH allowed through firewall",
    "test_sysctl_deployed":             "Hardened sysctl.conf deployed",
    "test_sysctl_ip_forward_disabled":  "IP forwarding disabled",
    "test_shadow_permissions":          "/etc/shadow permissions correct",
    "test_playbook_is_idempotent":      "Playbook is idempotent (changed=0)",
}

# -- Reporter ---------------------------------------------------------------

# The phase-oriented summary is rendered by the shared `aria-reporter`
# pytest plugin (installed via requirements.txt); this file only declares
# the mission's phases + friendly objective names.
from aria_reporter import configure  # noqa: E402

configure(phases=PHASES, friendly=FRIENDLY, mission_id="1-3")
