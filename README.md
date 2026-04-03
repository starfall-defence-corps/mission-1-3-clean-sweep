# Starfall Defence Corps Academy

## Mission 1.3: Clean Sweep

> *"Half the fleet runs services nobody asked for. FTP. Telnet. The firewall? Not running. Not enabled. Fix this."*

You are a cadet at the Starfall Defence Corps Academy. The fleet's SSH was hardened in Mission 1.2, but that was just one door. Every node is running unnecessary services, the firewall is inactive, kernel parameters are unhardened, and file permissions are too loose. Your mission: write an Ansible playbook to sweep every node clean.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with Docker Compose v2)
- [GNU Make](https://www.gnu.org/software/make/)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/) (`ansible-core`)
- Python 3.10+ (for test environment)
  - On Debian/Ubuntu: `sudo apt install python3-venv`
- Git

> **Windows users**: This mission requires a Linux environment. Install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) and run all commands from within your WSL terminal. Docker Desktop should be configured to use the WSL2 backend.

## Quick Start

```bash
# 1. Use this template on GitHub (green button, top right)
#    This creates YOUR OWN copy of the repo.
#    Set it to Public, then clone it:
git clone https://github.com/YOUR-USERNAME/mission-1-3-clean-sweep.git
cd mission-1-3-clean-sweep

# 2. Start the fleet
make setup
```

3. **Read your orders**: [Mission Briefing](docs/BRIEFING.md)
4. **Complete the exercises**: [Exercises](docs/EXERCISES.md)
5. **Stuck?** [Hints & Troubleshooting](docs/HINTS.md)
6. **Track progress**: [Checklist](CHECKLIST.md)

## Lab Architecture

```
 Your Machine
+------------------------------------------+
|  workspace/                              |
|    ansible.cfg                           |
|    inventory/hosts.yml  (pre-configured) |
|    playbook.yml         (you complete)   |
|    files/sysctl-hardened.conf (provided) |
|    .ssh/cadet_key       (auto-generated) |
|                                          |
|  Docker Network: 172.30.0.0/24           |
|  +------------+ +----------+ +----------+|
|  | sdc-web    | | sdc-db   | | sdc-comms||
|  | :2221      | | :2222    | | :2223    ||
|  | Ubuntu22.04| | Ubuntu   | | Ubuntu   ||
|  | systemd    | | systemd  | | systemd  ||
|  | Telnet, xinetd, no firewall, loose   ||
|  | permissions (starting state)          ||
|  +------------+ +----------+ +----------+|
+------------------------------------------+
```

## Available Commands

```
make help       Show available commands
make setup      Start the fleet (3 target nodes)
make test       Ask ARIA to verify your work
make reset      Destroy and rebuild all fleet nodes
make destroy    Tear down everything (containers, keys, venv)
make ssh-web    SSH into sdc-web (fleet web server)
make ssh-db     SSH into sdc-db (fleet database server)
make ssh-comms  SSH into sdc-comms (fleet comms relay)
```

## Mission Files

| File | Purpose |
|------|---------|
| [BRIEFING.md](docs/BRIEFING.md) | Mission briefing — **read this first** |
| [EXERCISES.md](docs/EXERCISES.md) | Step-by-step exercises (5 phases) |
| [HINTS.md](docs/HINTS.md) | Troubleshooting and hints |
| [CHECKLIST.md](CHECKLIST.md) | Progress tracker |

## ARIA Review (Pull Request Workflow)

**ARIA** (Automated Review & Intelligence Analyst) reviews your work in two ways:

**Locally** — run `make test` for instant pass/fail verification. No API key needed.

**On Pull Request** — push your work to a branch, open a PR to `main`, and ARIA reads your playbook and posts a qualitative review as a PR comment (structure, security, recommendations).

To enable PR reviews, add an API key to your repo:
1. Get a key from [platform.claude.com](https://platform.claude.com/)
2. In your repo: **Settings** > **Secrets and variables** > **Actions** > **New repository secret**
3. Name: `ANTHROPIC_API_KEY`, Value: your key

If no key is configured, ARIA skips the PR review — `make test` still works locally.

## Troubleshooting

**Containers won't start**: Ensure Docker Desktop is running. Check for port conflicts on 2221-2223.

**SSH connection refused**: Run `make setup` to ensure containers are running and SSH is ready.

**`make test` fails with "No module named pytest"**: Run `make setup` first — it creates the Python virtual environment automatically.

**Locked out of nodes after enabling firewall**: You enabled ufw without allowing SSH first. Run `make reset` to rebuild containers.

**Need a clean slate**: Run `make reset` to destroy and rebuild everything.

**Docker network conflict**: If you see "Pool overlaps with other one on this address space", another Docker network is using the 172.30.0.0/24 subnet. Stop conflicting containers or edit `.docker/docker-compose.yml` to use a different subnet.
