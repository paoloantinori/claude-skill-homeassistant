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

### Deployment Orchestrator

**Location**: `.claude/skills/home-assistant-manager/subagents/deployment-orchestrator/` (skill-embedded)

**Purpose**: Automate deployment workflow decisions and execution for Home Assistant configuration changes

**Triggers** (auto-delegates to deployment orchestrator):
- Keywords: "deploy to ha", "deploy changes", "git deployment", "scp deployment", "sync to server", "deployment status"
- Context: After automation/script/template changes, user asks "deploy this"
- Explicit: "Deploy via git", "Deploy via scp", "Check deployment status", "Sync changes to server"

**Workflows**:
- **Git Deployment (Final Changes)**: Deploy finalized changes via git with full version control (90s timeout)
  - Validate local → Commit and push → Check server status → (dirty?) → Diff inspection → Discard and pull → Reload → Verify
  - Returns: Deployment success with commit hash, component reloaded, verification status

- **Rapid SCP Deployment (Testing)**: Fast deployment iteration during development (30s timeout)
  - Quick validate → Deploy via SCP → Reload components → Quick test
  - Returns: Deployment success with iteration count, reminds to commit to git when done

- **SCP + Git Sync (Finalize Tested Changes)**: Sync SCP-tested changes to git (60s timeout)
  - Commit local → Check server status → Inspect changes → Discard and pull → Final reload
  - Returns: Sync success with commit hash, server state before/after

- **Deployment Status Check**: Check deployment state and identify issues (45s timeout)
  - Check local git → Check server git → Check component status → Check recent logs
  - Returns: Comprehensive status report with recommendations

**Example usage**:
```bash
# Deploy finalized changes via git
$ "Deploy this automation via git"
# Delegates to deployment-orchestrator for git deployment

# Rapid testing iteration
$ "Deploy this script via SCP for testing"
# Delegates for rapid SCP deployment

# Check deployment status
$ "Check deployment status"
# Delegates for comprehensive status check

# Sync tested changes to git
$ "Sync my SCP changes to git"
# Delegates for SCP + git sync workflow
```

**Output format**:
```
[STATUS] ✅ Git Deployment Complete

Method: Git
Files: 2
Components reloaded: automation, script
Commit: 1a2b3c4d

Deployment Steps:
✅ Local validation: PASS - All 2 files valid YAML
✅ Commit and push: SUCCESS - Committed and pushed to origin/master
✅ Server status: Clean - No uncommitted changes
✅ Git pull: SUCCESS - Updated to latest commit
✅ Reload: SUCCESS - automation and script reloaded
✅ Verification: PASS - Test entities responding correctly

[STATUS] Deployment successful. Changes are now active.
```

**Key features**:
- **Workflow selection**: Chooses appropriate deployment method (Git vs SCP) based on context
- **Conflict resolution**: Safely handles git conflicts and external modifications
- **Safety enforcement**: Never discards changes without inspection (git diff before checkout)
- **Deployment automation**: Executes deployment steps with validation and verification
- **State management**: Tracks deployment state and provides rollback if needed
- **Structured reporting**: Clear status with actionable steps and rollback information

**Safety rules** (inherited from HA Manager skill):
- **ALWAYS git status BEFORE git pull**: Never pull without checking state
- **ALWAYS git diff BEFORE git checkout**: Never discard changes without inspection
- **NEVER git reset --hard**: Can lose uncommitted work without warning
- **ALWAYS use hass-cli**: Never curl for HA API
- **Use timeouts**: All deployment commands must have timeouts

**Deployment patterns**:
- **Git Status Before Pull**: Check server git status before pulling to prevent conflicts
- **Git Diff Before Checkout**: Inspect changes before discarding to prevent data loss
- **Component Reload Selection**: Choose correct reload based on file type (automation/script/template)
- **Conflict Recovery**: Safely recover from git pull conflicts with inspection
- **Rollback on Failure**: Rollback deployment if verification fails

**Integration with other subagents**:
- **Config Validator**: Deployment Orchestrator calls Config Validator before deployment
- **Automation Verifier**: Deployment Orchestrator deploys → Automation Verifier verifies
- **HA Log Analyzer**: Deployment Orchestrator deploys → HA Log Analyzer checks logs
- **Complete lifecycle**: Validate (Config Validator) → Deploy (Deployment Orchestrator) → Verify (Automation Verifier) → Check Logs (HA Log Analyzer)

**See also**: `.claude/skills/home-assistant-manager/subagents/deployment-orchestrator/PROMPT.md` for complete subagent documentation

---

### Lovelace Dashboard Tester

**Location**: `.claude/skills/home-assistant-manager/subagents/lovelace-dashboard-tester/` (skill-embedded)

**Purpose**: Validate and test Lovelace dashboard configurations with comprehensive JSON validation, entity verification, and card configuration checks

**Triggers** (auto-delegates to lovelace dashboard tester):
- Keywords: "validate dashboard", "check dashboard", "dashboard errors", "lovelace validation", "test dashboard"
- Context: Before deploying dashboard changes, after editing dashboards, dashboard not appearing in sidebar
- Explicit: "Validate dashboard configuration", "Check dashboard JSON", "Test dashboard loading"

**Workflows**:
- **JSON Syntax Validation**: Validate dashboard JSON structure (20s timeout)
  - Identify dashboards → Validate JSON → Parse structure
  - Returns: JSON validation results with error locations

- **Dashboard Registration Check**: Verify dashboards are registered (25s timeout)
  - Read registry → List dashboard files → Cross-reference
  - Returns: Registered/unregistered dashboards, orphaned registrations

- **Entity Reference Verification**: Verify all entities exist (30s timeout)
  - Extract entities → Fetch entity list → Verify existence
  - Returns: Missing/unavailable entities with card locations

- **Card Configuration Validation**: Validate card configurations (40s timeout)
  - Parse cards → Validate types → Check options → Validate templates
  - Returns: Invalid cards, missing options, template errors

- **Full Dashboard Validation**: Comprehensive validation (90s timeout)
  - JSON validation → Registration check → Entity verification → Card validation
  - Returns: Overall status with deployment readiness

**Example usage**:
```bash
# Validate dashboard JSON
$ "Check dashboard JSON for errors"
# Delegates to lovelace-dashboard-tester for JSON validation

# Full dashboard validation before deploy
$ "Validate my dashboard before deploying"
# Delegates for comprehensive validation

# Check if dashboard is registered
$ "Why is my dashboard not showing in sidebar?"
# Delegates for registration check
```

**Output format**:
```
[STATUS] ✅ Full Dashboard Validation Complete

Overall: PASS
Ready to deploy: YES

Validation Results:
✅ JSON Syntax: All 3 dashboards valid
✅ Registration: All dashboards registered
⚠️ Entity References: 2 unavailable entities
✅ Card Configuration: All 132 cards valid

[STATUS] Dashboard ready with warnings. Review unavailable entities.
```

**Key features**:
- **JSON syntax validation**: Catches JSON errors before deployment
- **Registration verification**: Ensures dashboards appear in sidebar
- **Entity reference checking**: Verifies all entities exist and are available
- **Card configuration validation**: Validates card types, options, and templates
- **Structured reporting**: Clear status with specific locations and fixes
- **Deployment readiness**: Overall assessment with deployment steps

**Dashboard patterns**:
- **Invalid JSON**: Trailing commas, missing commas, unclosed brackets
- **Dashboard not registered**: Missing from lovelace_dashboards registry
- **Entity not found**: Typos, deleted entities, wrong domains
- **Invalid card type**: Typos, custom cards not installed
- **Template errors**: Invalid Jinja2 syntax, undefined variables
- **Missing required options**: Card-specific required fields
- **Dashboard not loading**: Browser cache, JSON errors, missing custom cards

**Safety rules** (inherited from HA Manager skill):
- **ALWAYS backup before modifying**: Never modify dashboard without backup
- **Validate JSON before deployment**: Invalid JSON breaks dashboards
- **NEVER restart for dashboard changes**: Dashboards load on browser refresh
- **ALWAYS use hass-cli**: Never curl for HA API
- **Use timeouts**: All validation commands must have timeouts

**Integration with other subagents**:
- **Config Validator**: Can validate YAML entities referenced in dashboards
- **Deployment Orchestrator**: Deploys validated dashboards via SCP
- **HA Log Analyzer**: Checks logs for dashboard load errors
- **Note**: Dashboards don't require restart, just browser refresh

**See also**: `.claude/skills/home-assistant-manager/subagents/lovelace-dashboard-tester/PROMPT.md` for complete subagent documentation

---

### Service Call Tester

**Location**: `.claude/skills/home-assistant-manager/subagents/service-call-tester/` (skill-embedded)

**Purpose**: Test Home Assistant service calls in isolation with parameter validation, response checking, and error diagnosis

**Triggers** (auto-delegates to service call tester):
- Keywords: "test service call", "validate service", "check service", "service call failed", "service parameters"
- Context: Before executing service calls, service call returned error, troubleshooting service issues
- Explicit: "Test this service call", "Validate service parameters", "Diagnose service error"

**Workflows**:
- **Service Existence Check**: Verify services exist and are registered (15s timeout)
  - List services → Verify service exists → Find similar services
  - Returns: Service existence status with alternatives

- **Parameter Schema Validation**: Validate service parameters against schema (20s timeout)
  - Fetch service schema → Validate parameters → Check types
  - Returns: Parameter validation results with errors and fixes

- **Dry-Run Service Call**: Test service call without executing (25s timeout)
  - Service existence → Parameter validation → Simulate call → Assess risk
  - Returns: Validation status with risk assessment and safe-to-execute

- **Execute Service Call (Read-Only)**: Execute read-only services for testing (20s timeout)
  - Validate read-only → Execute service → Validate response
  - Returns: Service call result with execution time

- **Service Call Diagnosis**: Diagnose service call failures (45s timeout)
  - Analyze error → Check service → Check parameters → Generate diagnosis
  - Returns: Root cause with fix steps and corrected example

**Example usage**:
```bash
# Check if service exists
$ "Does the notify.telegram service exist?"
# Delegates to service-call-tester for existence check

# Validate service parameters
$ "Validate parameters for automation.trigger"
# Delegates for parameter validation

# Test service call safely
$ "Test this service call in isolation"
# Delegates for dry-run validation

# Diagnose service error
$ "Why did this service call fail?"
# Delegates for error diagnosis
```

**Output format**:
```
[STATUS] ✅ Service Existence Check Complete

Service: automation.trigger
Status: EXISTS

✅ Service is registered and available

Similar Services:
- automation.reload
- automation.turn_on
- automation.turn_off

[STATUS] Service is registered and available.
```

**Key features**:
- **Service existence verification**: Confirms services are registered
- **Parameter schema validation**: Validates parameters against service schemas
- **Dry-run testing**: Validates without executing (risk assessment)
- **Read-only execution**: Safe testing of read-only services
- **Error diagnosis**: Root cause analysis with fix recommendations
- **Safety enforcement**: Tests in isolation, validates before execution

**Service call patterns**:
- **Service not found**: Typos, integration not loaded, incorrect format
- **Invalid parameters**: Missing required, extra parameters, wrong types
- **Entity not found**: Typos, deleted entities, wrong domains
- **Permission denied**: Requires admin, protected entities
- **Service timeout**: Device not responding, network issues
- **Invalid entity ID format**: Missing domain, wrong separator
- **Template errors**: Invalid Jinja2 syntax, undefined variables
- **No data returned**: Service completed silently, check logs

**Safety rules** (inherited from HA Manager skill):
- **Test in isolation first**: Never test in production without isolation
- **Use hass-cli**: NEVER curl for HA API
- **Validate before execute**: Always dry-run state-changing services
- **Read-only by default**: Never execute state-changing without explicit permission
- **Use timeouts**: All service calls must have timeouts

**Integration with other subagents**:
- **Config Validator**: Validates service calls in YAML configurations
- **Automation Verifier**: Tests service calls within automations
- **HA Log Analyzer**: Service call error diagnosis
- **Deployment Orchestrator**: Service call testing during deployment

**See also**: `.claude/skills/home-assistant-manager/subagents/service-call-tester/PROMPT.md` for complete subagent documentation

---

## Troubleshooting

**If something goes wrong:**
1. Check logs: `ssh ha "ha core logs | grep -i error | tail -20"`
2. Review [docs/06_common_mistakes.md](docs/06_common_mistakes.md)
3. Verify config: `ssh ha "ha core check"`
4. Check git status: `ssh ha "cd /homeassistant && git status"`
