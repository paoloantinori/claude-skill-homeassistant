---
name: home-assistant-manager
description: Expert-level Home Assistant configuration management with efficient deployment workflows (git and rapid scp iteration), remote CLI access via SSH and hass-cli, automation verification protocols, log analysis, reload vs restart optimization, and comprehensive Lovelace dashboard management for tablet-optimized UIs. Includes template patterns, card types, debugging strategies, and real-world examples.
triggers:
  files:
    - "automations/**/*.yaml"
    - "automations/**/*.yml"
    - "scripts/**/*.yaml"
    - "scripts/**/*.yml"
    - "templates/**/*.yaml"
    - "templates/**/*.yml"
    - "pyscript/**/*.py"
    - "packages/**/*.yaml"
    - "packages/**/*.yml"
    - "configuration.yaml"
    - "**/lovelace/**/*.yaml"
    - "**/lovelace/**/*.yml"
    - "ui-lovelace.yaml"
  commands:
    - "scp *ha:/homeassistant/*"
    - "scp * ha:/homeassistant/*"
    - "ssh ha*"
    - "hass-cli*"
    - "curl *homeassistant*"
    - "curl *HASS_SERVER*"
    - "git pull*"
    - "git push*"
  keywords:
    - "home assistant"
    - "homeassistant"
    - "automation"
    - "lovelace"
    - "dashboard"
    - "deploy to ha"
    - "reload automation"
    - "reload script"
    - "reload template"
    - "pyscript"
    - "hass-cli"
---

# Home Assistant Manager

Expert-level Home Assistant configuration management with efficient workflows, remote CLI access, and verification protocols.

## 🚨 CRITICAL: Start Here

**Before any Home Assistant operation, read these:**

1. **[docs/01_critical_safety.md](docs/01_critical_safety.md)** - NEVER RESTART WITHOUT ASKING, Reload vs Restart decision tree
2. **[docs/02_deployment.md](docs/02_deployment.md)** - Git vs SCP workflows, conflict resolution
3. **[docs/03_validation.md](docs/03_validation.md)** - Pre-deployment validation checklist

## 📚 Documentation Index

| Topic | File | When to Read |
|-------|------|--------------|
| **Critical Safety** | [01_critical_safety.md](docs/01_critical_safety.md) | **READ FIRST** - Before ANY HA operation |
| **Deployment** | [02_deployment.md](docs/02_deployment.md) | Before deploying changes |
| **Validation** | [03_validation.md](docs/03_validation.md) | Before deployment |
| **Automation Testing** | [04_automation_testing.md](docs/04_automation_testing.md) | After automation changes |
| **Lovelace Dashboards** | [05_lovelace_dashboards.md](docs/05_lovelace_dashboards.md) | When working with UI |
| **Common Mistakes** | [06_common_mistakes.md](docs/06_common_mistakes.md) | When encountering errors |
| **Remote Access** | [07_remote_access.md](docs/07_remote_access.md) | For hass-cli/SSH patterns |
| **Quick Reference** | [08_quick_reference.md](docs/08_quick_reference.md) | Command cheat sheet |

## Quick Start

### Prerequisites

Before starting, verify:
1. SSH access: `ssh ha`
2. `hass-cli` installed
3. Environment loaded: `source .env`
4. Git connected to HA `/homeassistant`

### Quick Workflow

```bash
# 1. Source environment
source .env

# 2. Make changes locally
# Edit files...

# 3. Validate
ssh ha "ha core check"

# 4. Deploy
scp file.yaml ha:/homeassistant/
# OR: git push && ssh ha "cd /homeassistant && git pull"

# 5. Reload
hass-cli service call automation.reload

# 6. Verify
hass-cli state get entity.name
```

## Core Capabilities

- Remote HA management via SSH and hass-cli
- Smart deployment workflows (git + rapid scp iteration)
- Configuration validation and safety checks
- Automation testing and verification
- Log analysis and error detection
- Reload vs restart optimization
- Lovelace dashboard development
- Template syntax patterns and debugging

## Decision Trees

### Reload vs Restart?

```
Did you change...
├─ automation/script/template? → RELOAD (docs/01_critical_safety.md)
├─ configuration.yaml integration? → RESTART (ASK FIRST!)
├─ template entity? → RESTART (ASK FIRST!)
└─ Not sure? → Check docs/01_critical_safety.md
```

### Git vs SCP?

```
Are you still testing?
├─ YES → Use SCP (docs/02_deployment.md)
└─ NO → Use Git (docs/02_deployment.md)
```

## Auto-Improve Behavior

**When commands fail:**
1. Analyze error message carefully
2. Try correcting the command (not switching tools)
3. After success, document the pattern

See **[docs/06_common_mistakes.md](docs/06_common_mistakes.md)** for patterns.

## Quick Command Reference

| Task | Command |
|------|---------|
| Validate config | `ssh ha "ha core check"` |
| Reload automations | `hass-cli service call automation.reload` |
| Reload scripts | `hass-cli service call script.reload` |
| Reload templates | `hass-cli service call homeassistant.reload_template_entity` |
| Restart HA | `ssh ha "ha core restart"` (**ASK FIRST!**) |
| Get state | `hass-cli state get entity.name` |
| List states | `hass-cli state list` |
| Trigger automation | `hass-cli service call automation.trigger --arguments entity_id=automation.name` |
| View logs | `ssh ha "ha core logs \| tail -50"` |
| Deploy via SCP | `scp file.yaml ha:/homeassistant/` |
| Deploy via Git | `ssh ha "cd /homeassistant && git pull"` |

## 🚨 Most Critical Rules

1. **NEVER restart without asking** - See [docs/01_critical_safety.md](docs/01_critical_safety.md)
2. **Validate BEFORE deploy** - See [docs/03_validation.md](docs/03_validation.md)
3. **Inspect git diffs before checkout** - See [docs/02_deployment.md](docs/02_deployment.md)
4. **Prefer reload over restart** - See [docs/01_critical_safety.md](docs/01_critical_safety.md)
5. **Prefer hass-cli over curl** - See [docs/07_remote_access.md](docs/07_remote_access.md)

## Path Reference

| Location | Path |
|----------|------|
| Project root | `/home/pantinor/data/repo/personal/hassio/` |
| HA server (via SSH) | `ha:/homeassistant/` |
| Automations | `automations/*/` |
| Scripts | `scripts/*/` |
| Templates | `templates/` |
| Dashboards | `.storage/lovelace.*` |

## Troubleshooting

**If something goes wrong:**
1. Check logs: `ssh ha "ha core logs | grep -i error | tail -20"`
2. Review [docs/06_common_mistakes.md](docs/06_common_mistakes.md)
3. Verify config: `ssh ha "ha core check"`
4. Check git status: `ssh ha "cd /homeassistant && git status"`
