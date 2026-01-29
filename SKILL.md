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
    - "logger"
    - "log level"
    - "logging"
    - "reduce logs"
    - "debug logs"
---

# Home Assistant Manager

Expert-level Home Assistant configuration management with efficient workflows, remote CLI access, and verification protocols.

## 🚨🚨🚨 CRITICAL RULES (READ FIRST)

**1. NEVER RESTART WITHOUT ASKING** → See [docs/01_critical_safety.md](docs/01_critical_safety.md)
**2. ALWAYS use hass-cli, NEVER curl** → See [docs/07_remote_access.md](docs/07_remote_access.md)

### Quick Rule Reference

| Rule | Violation | Correct Approach |
|------|-----------|------------------|
| **NO restart without asking** | `ssh ha "ha core restart"` (without permission) | Always ask first: "May I restart?" |
| **NO curl for HA API** | `curl -H "Authorization: Bearer $TOKEN" $SERVER/api/...` | Use `hass-cli state get/service call` |
| **NO grep for SSH fingerprint** | `ssh ha ... \| grep -v "Host key..."` | Use `ssh -oVisualHostKey=no ha ...` |
| **NO blind git checkout** | `ssh ha "cd /homeassistant && git checkout ."` | Always `git diff` first to inspect |

---

## 🚨 CRITICAL: Start Here

**Before any Home Assistant operation, read these:**

1. **[docs/01_critical_safety.md](docs/01_critical_safety.md)** - NEVER RESTART WITHOUT ASKING, Reload vs Restart decision tree
2. **[docs/02_deployment.md](docs/02_deployment.md)** - Git vs SCP workflows, conflict resolution
3. **[docs/03_validation.md](docs/03_validation.md)** - Pre-deployment validation checklist
4. **[docs/07_remote_access.md](docs/07_remote_access.md)** - **hass-cli MANDATORY, curl prohibited**

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
| **Logger Configuration** | [09_logger_configuration.md](docs/09_logger_configuration.md) | When adjusting log levels |

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
ssh -oVisualHostKey=no ha "ha core check"

# 4. Deploy
scp file.yaml ha:/homeassistant/
# OR: git push && ssh -oVisualHostKey=no ha "cd /homeassistant && git pull"

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
| Find logger in config | `grep -n "logger:" -A 50 configuration.yaml \| grep pattern` |
| Deploy via SCP | `scp file.yaml ha:/homeassistant/` |
| Deploy via Git | `ssh ha "cd /homeassistant && git status"` → (if clean) → `git pull` |

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

## Subagent Delegation

This skill delegates specialized tasks to subagents for efficiency and expertise.

### HA Log Analyzer

**Location**: `.claude/skills/home-assistant-manager/subagents/ha-log-analyzer/` (skill-embedded)

**Purpose**: Monitor Home Assistant logs for errors, warnings, and automation execution traces

**Triggers** (auto-delegates to log analyzer):
- Keywords: "check logs", "log errors", "analyze logs", "automation fired?", "startup issues"
- Post-deployment: After any `hass-cli service call *.reload`
- Post-trigger: After `hass-cli service call automation.trigger`

**Workflows**:
- **Post-Deployment Check**: Scan logs for errors after reload (10s timeout)
- **Automation Execution Trace**: Monitor specific automation execution (30s timeout)
- **Startup Health Check**: Verify clean HA startup (15s timeout)
- **Real-Time Monitor**: Watch logs for specific patterns (60s timeout)

**Example usage**:
```bash
# After reloading automations
$ hass-cli service call automation.reload
# Skill automatically delegates to ha-log-analyzer for error check

# Manual log analysis
$ "Check for errors in the logs"
# Delegates to ha-log-analyzer

# Automation verification
$ hass-cli service call automation.trigger --arguments entity_id=automation.my_test
$ "Did it fire?"
# Delegates to ha-log-analyzer for execution trace
```

**Output format**:
```
[STATUS] ✅ Post-Deployment Log Check Complete

Errors: 0 | Warnings: 0 | Time: 14:32:18

✅ No errors detected in last 50 log lines.
```

**Key features**:
- **Timeout enforcement**: All `tail -f` commands wrapped with `timeout` (prevents hanging)
- **Pattern detection**: Identifies known error patterns (template errors, service call failures)
- **Actionable diagnosis**: Every error includes suggested fix
- **Structured output**: Clear status indicators (✅ ⚠️ 🚨) with context

**Critical safety rules** (inherited by subagent):
- **ALWAYS use timeouts**: `timeout 120 tail -f` (never indefinite)
- **VisualHostKey=no**: All SSH commands use `ssh -oVisualHostKey=no ha`
- **hass-cli preferred**: Use `hass-cli`, never curl
- **Exit cleanly**: Never block waiting for user input

**See also**: `.claude/skills/home-assistant-manager/subagents/ha-log-analyzer/PROMPT.md` for complete subagent documentation

---

### Automation Verifier

**Location**: `.claude/skills/home-assistant-manager/subagents/automation-verifier/` (skill-embedded)

**Purpose**: End-to-end testing and verification of automation changes with comprehensive validation

**Triggers** (auto-delegates to automation verifier):
- Keywords: "test automation", "verify automation", "automation working?", "did it work?"
- Context: After automation YAML changes
- Explicit: "Test automation end-to-end", "Verify this automation works"

**Workflows**:
- **Full Verification**: Complete testing cycle with validation (60s timeout)
  - Config validation → Deploy → Reload → Trigger → Monitor → Verify → Report
- **Quick Verification**: Fast verification during development (30s timeout)
  - Deploy → Reload → Trigger → Quick log check
- **Smoke Test**: Test multiple critical automations (120s timeout)
  - Select automations → Trigger each → Verify each → Summary report

**Example usage**:
```bash
# After editing automation
$ "Test automation.telegram_test end-to-end"
# Delegates to automation-verifier for full verification

# Quick verification during development
$ "Quick verify automation.light_toggle"
# Delegates for rapid testing

# After system changes
$ "Run smoke test on security automations"
# Delegates for smoke testing
```

**Output format**:
```
[STATUS] ✅ Automation Verification Complete

Automation: automation.telegram_test
Overall: PASS

Step-by-Step Results:
✅ Config validation: PASS
✅ Deployment: PASS (via scp)
✅ Reload: PASS
✅ Trigger: PASS
✅ Execution: PASS (4.2 seconds, 3 actions)
✅ Verification: PASS (Telegram notification confirmed)

[STATUS] Automation is working correctly. Ready for production.
```

**Key features**:
- **End-to-end testing**: Complete workflow from deploy to verification
- **Multi-step orchestration**: Automates complex testing sequences
- **State verification**: Confirms expected outcomes actually occurred
- **Structured reporting**: [PASS|FAIL|WARN] with detailed diagnosis
- **Integration with HA Log Analyzer**: Delegates log analysis for consistency

**Verification types**:
- **Notification**: Verify Telegram/Alexa messages sent
- **State change**: Confirm entity state changed
- **Script execution**: Verify script completed
- **Service call**: Confirm service executed successfully

**Critical safety rules** (inherited by subagent):
- **Validate BEFORE deploy**: Always run `ha core check` first
- **ALWAYS use hass-cli**: Never curl for HA API
- **NEVER restart without asking**: Follow critical safety rules
- **Use timeouts**: All monitoring commands have timeouts
- **Exit cleanly**: Never block waiting for user input

**See also**: `.claude/skills/home-assistant-manager/subagents/automation-verifier/PROMPT.md` for complete subagent documentation

---

### Config Validator

**Location**: `.claude/skills/home-assistant-manager/subagents/config-validator/` (skill-embedded)

**Purpose**: Pre-deployment configuration validation to catch errors before they reach production

**Triggers** (auto-delegates to config validator):
- Keywords: "validate config", "check before deploy", "config errors", "is this valid?", "safe to deploy?"
- Context: Before ANY deployment (git or scp)
- Explicit: "Validate this configuration", "Check if there are errors"

**Workflows**:
- **Pre-Deployment Full Validation**: Comprehensive validation (60s timeout)
  - HA core check → YAML syntax → Entity existence → Service calls → Templates → Integrations
  - Returns: [PASS|FAIL|WARN] with specific issues and fixes
  - Safe to deploy: YES/NO

- **Quick Syntax Check**: Fast YAML syntax validation (20s timeout)
  - Identify files → YAML syntax check → Basic HA check
  - Returns: File-level syntax errors with line numbers

- **Entity Reference Checker**: Verify all referenced entities (30s timeout)
  - Extract entities → Fetch entity list → Verify existence → Check availability
  - Returns: Missing/unavailable entities with file locations

- **Template Validator**: Validate Jinja2 templates (30s timeout)
  - Extract templates → Syntax check → Variable verification → Test rendering
  - Returns: Template errors with context and fixes

**Example usage**:
```bash
# Before deploying
$ "Validate this configuration before deploy"
# Delegates to config-validator for full validation

# Quick syntax check while editing
$ "Check YAML syntax for this file"
# Delegates for rapid syntax validation

# After editing automation
$ "Are there any config errors?"
# Delegates to config-validator for validation
```

**Output format**:
```
[STATUS] ✅ Pre-Deployment Validation Complete

Overall: PASS
Safe to deploy: YES

Validation Results:
✅ HA Core Config: Valid
✅ YAML Syntax: All 3 files valid
✅ Entity References: All 12 entities exist
✅ Service Calls: All 5 service calls valid
✅ Templates: All 4 templates syntax correct
✅ Integrations: All required loaded

[STATUS] Configuration is valid. Safe to deploy.
```

**Key features**:
- **Pre-deployment validation**: Catches errors BEFORE deployment (not after)
- **Multi-layer checks**: YAML, entities, services, templates, integrations
- **Entity verification**: Confirms all referenced entities exist
- **Template validation**: Checks Jinja2 syntax and variables
- **Structured reporting**: [PASS|FAIL|WARN] with specific file:line locations
- **Actionable fixes**: Every error includes specific fix recommendation

**Validation types**:
- **YAML Syntax**: Indentation, quotes, colons, structure
- **Entity References**: Existence, availability, correct domains
- **Service Calls**: Valid services, correct parameters, schema compliance
- **Templates**: Jinja2 syntax, variable existence, attribute access
- **Integrations**: Loaded status, configuration errors

**Critical safety rules** (inherited by subagent):
- **Validate BEFORE deploy**: Never skip validation, even for "small" changes
- **ALWAYS use hass-cli**: Never curl for HA API
- **Use timeouts**: All validation commands have timeouts
- **Exit cleanly**: Never block waiting for user input

**Integration with other subagents**:
- **Pre-deployment**: Config Validator validates BEFORE deployment
- **Post-deployment**: Automation Verifier validates AFTER deployment
- **Complete lifecycle**: Validate → Deploy → Verify

**See also**: `.claude/skills/home-assistant-manager/subagents/config-validator/PROMPT.md` for complete subagent documentation

---

## Troubleshooting

**If something goes wrong:**
1. Check logs: `ssh ha "ha core logs | grep -i error | tail -20"`
2. Review [docs/06_common_mistakes.md](docs/06_common_mistakes.md)
3. Verify config: `ssh ha "ha core check"`
4. Check git status: `ssh ha "cd /homeassistant && git status"`
