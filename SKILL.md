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

## Core Capabilities

- Remote Home Assistant instance management via SSH and hass-cli
- Smart deployment workflows (git-based and rapid iteration)
- Configuration validation and safety checks
- Automation testing and verification
- Log analysis and error detection
- Reload vs restart optimization
- Lovelace dashboard development and optimization
- Template syntax patterns and debugging
- Tablet-optimized UI design

## Prerequisites

Before starting, verify the environment has:
1. SSH access to Home Assistant instance (`ssh ha`)
2. `hass-cli` installed locally
3. Environment variables loaded (HASS_SERVER, HASS_TOKEN) - via `source .env`
4. Git repository connected to HA `/homeassistant` directory
5. Context7 MCP server with Home Assistant docs (optional)

**Note:** The `ha core` CLI commands are not available via the SSH add-on. Use `hass-cli` for service calls and API access instead.

---

## 🚨🚨🚨 CRITICAL: NEVER RESTART WITHOUT ASKING 🚨🚨🚨

**MEMORIZE THIS RULE - NO EXCEPTIONS:**

**You are FORBIDDEN from executing `ha core restart` without:**
1. Explaining why you think a restart is needed
2. Getting EXPLICIT permission from the user
3. Waiting for a clear "yes" or "go ahead"

**This rule applies EVEN IF you are 100% certain a restart is needed.**

**What this means:**
- ❌ NEVER execute restart immediately after deciding it's needed
- ❌ NEVER say "restarting..." and then do it without waiting
- ❌ NEVER assume silence or lack of objection means consent
- ✅ ALWAYS explain the reason first
- ✅ ALWAYS ask explicitly: "May I restart Home Assistant?"
- ✅ ALWAYS wait for explicit confirmation

**Why this exists:**
- Restarts disrupt ALL running automations and services for ~30 seconds
- There may be time-sensitive processes running
- The user may want to schedule the restart for a better time
- You might be WRONG about needing a restart (see warnings section below)

**If you violate this rule, you are breaking the user's trust and disrupting their home automation system.**

---

## 🚨 CRITICAL GUARDRAILS - Reload vs Restart

**NEVER use `ha core restart` unless EXPLICITLY required by the change type.**

### When to RELOAD (fast, non-disruptive):

**⚠️ ALWAYS source .env first:** `source /home/pantinor/data/repo/personal/hassio/.env`

| Change Type | Reload Command |
|-------------|----------------|
| Automations | `source .env && hass-cli service call automation.reload` |
| Scripts | `source .env && hass-cli service call script.reload` |
| Templates | `source .env && hass-cli service call template.reload` |
| Scenes | `source .env && hass-cli service call scene.reload` |
| Groups | `source .env && hass-cli service call group.reload` |
| Themes | `source .env && hass-cli service call frontend.reload_themes` |

**Note:** Without sourcing `.env`, hass-cli will fail with 401 Unauthorized.

### When RESTART is actually required:
- New integrations in `configuration.yaml`
- Min/Max sensors and platform-based sensors
- Core configuration changes
- New packages added

### If hass-cli fails (401/connection error) - Use REST API fallback:
```bash
# ✅ CORRECT: Use REST API for reload (non-disruptive)
source /home/pantinor/data/repo/personal/hassio/.env && \
curl -s -X POST \
  -H "Authorization: Bearer ${HASS_TOKEN}" \
  -H "Content-Type: application/json" \
  "${HASS_SERVER}/api/services/automation/reload"

# ❌ WRONG: Do NOT fall back to ha core restart for simple reloads!
# ssh ha "ha core restart"  # NEVER do this for automations/scripts/templates
```

### Guardrail Checklist:
0. ✅ **Source .env first:** `source /home/pantinor/data/repo/personal/hassio/.env`
1. ✅ Identify what changed (automations? scripts? templates?)
2. ✅ Use the appropriate reload service call
3. ✅ If hass-cli fails → Check if .env was sourced, then use REST API
4. ❌ NEVER use `ha core restart` as a lazy fallback

### 🛡️ Pre-Restart MANDATORY Checklist

**Before ANY restart command, you MUST complete ALL steps:**

- [ ] **Explained to user** why restart seems needed (configuration.yaml changes, new integration, etc.)
- [ ] **Asked explicitly**: "May I restart Home Assistant?" or "Should I restart HA?"
- [ ] **Received explicit confirmation** (clear "yes", "go ahead", "do it")
- [ ] **NOT assuming** silence = consent
- [ ] **NOT proceeding** without clear "yes"

**If ANY item is unchecked → STOP and ask the user**

**This checklist is MANDATORY. Skipping it violates the critical safety rule.**

**Verification before proceeding:**
```
User said: "yes" ✓
User said: "go ahead" ✓
User said: "ok" ✓
User said: [nothing] → ❌ ASK AGAIN, don't proceed
User said: "maybe" → ❌ CLARIFY, don't proceed
```

### ⚠️ Common Mistake: Don't Restart on Warnings

**CRITICAL:** If you see warnings after reload like:
```
Referenced entities automation.xyz are missing or not currently available
```

**DO NOT interpret this as requiring a restart!**

**What to do instead:**
1. ✅ **Wait 5-10 seconds** - The warning is usually just a timing issue from testing too quickly after reload
2. ✅ **Check YAML syntax** - Validate YAML with Python/yamllint, check logs for parse errors
3. ✅ **Verify logs** - Look for actual configuration errors in `ha core logs`
4. ✅ **Test again** - Try triggering the automation after waiting

**Only restart if:**
- Configuration.yaml changes (new integrations, platforms, sensors)
- Custom component updates requiring restart
- User explicitly requests a restart
- **NOT for warnings that appear immediately after a reload**

**Why this matters:**
- Reload takes ~2 seconds, restart takes ~30+ seconds
- Restart disrupts all running automations and services
- Most warnings after reload are timing issues, not configuration errors
- Automation/Script YAML changes NEVER need a restart

### 🛡️ MANDATORY: Always Ask Before Restart

**CRITICAL GUARDRAIL:** If you ever determine that a restart might be necessary:

**YOU MUST:**
1. ❌ **STOP** - Do not execute `ha core restart` immediately
2. 🤔 **EXPLAIN** - Tell the user why you think a restart is needed
3. ❓ **ASK** - Request explicit permission from the user before proceeding
4. ⏳ **WAIT** - Wait for user confirmation before running any restart command

**Example:**
```
I believe a restart might be needed because [reason: configuration.yaml changes,
new integration added, etc.]. However, restarts disrupt all running automations
and services for ~30 seconds.

May I proceed with restarting Home Assistant, or would you prefer to investigate
further first?
```

**NEVER restart without explicit user permission, even if you're certain it's needed.**

This guardrail exists because:
- Restarts are disruptive and should be a conscious decision
- There may be running automations or time-sensitive processes
- The user may want to schedule the restart for a better time
- You might be wrong about needing a restart (see warnings above)

## Quick Deployment (Claude Code)

Two methods available for deploying config changes from Claude Code:

### Method 1: SSH + tar (Direct, Always Works)
```bash
# Deploy all config files
tar czf - automations.yaml scripts.yaml templates/ | ssh ha "cd /homeassistant && sudo tar xzf -"

# Reload via hass-cli
export HASS_SERVER=http://homeassistant.lan:8123
export HASS_TOKEN=<token_from_.env>
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call template.reload
```

### Method 2: MCP Script (After Git SSH Setup)
Once git SSH is configured on HA, call via MCP:
```
script.deploy_from_github
```
This pulls from GitHub and reloads all YAML automatically.

### Environment Setup
Source credentials before using hass-cli:
```bash
export HASS_SERVER=http://homeassistant.lan:8123
export HASS_TOKEN=<from .env>
export HASS_SSH_USER=root
export HASS_SSH_HOST=homeassistant.lan
```

## Remote Access Patterns

### 🚨 PREFER hass-cli OVER curl

**Always use hass-cli first.** Do NOT fall back to curl for HA API access unless hass-cli is genuinely broken.

**Why:**
- hass-cli handles authentication automatically (uses HASS_SERVER/HASS_TOKEN from env)
- curl requires manual env var setup which often fails (source vs eval, subshell issues)
- hass-cli provides consistent output formatting
- Switching tools mid-session wastes time debugging env var issues

**If hass-cli fails:**
1. Check if `.env` was sourced: `echo $HASS_TOKEN | head -c 20`
2. Try explicit sourcing: `eval "$(cat /home/pantinor/data/repo/personal/hassio/.env)"`
3. Only then consider curl as last resort

**hass-cli capabilities (use these instead of curl):**
```bash
# State queries
hass-cli state get sensor.entity_name              # Basic state (table format)
hass-cli -o yaml state get sensor.entity_name      # With attributes (YAML format)

# Service calls
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name

# Raw API access (when you need JSON)
hass-cli raw get /api/states/sensor.entity_name
hass-cli raw post /api/template --json '{"template": "{{ now() }}"}'
```

### 🚨 hass-cli Global Options: MUST Come BEFORE Subcommand

**CRITICAL:** Global options like `-o`/`--output` must appear BEFORE the subcommand, not after.

```bash
# ✅ CORRECT - global options BEFORE subcommand
hass-cli -o yaml state get sensor.example
hass-cli --output json state list
hass-cli --timeout 30 service call automation.reload

# ❌ WRONG - global options AFTER subcommand (will fail)
hass-cli state get sensor.example --output yaml   # Error: No such option
hass-cli state list --timeout 30                   # Error: No such option
```

**Global Options Reference:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Format: `json`, `yaml`, `table`, `auto`, `ndjson` | `auto` |
| `--timeout INTEGER` | Network timeout in seconds | `5` |
| `-s, --server TEXT` | Server URL (or use `HASS_SERVER` env) | `auto` |
| `--token TEXT` | Bearer token (or use `HASS_TOKEN` env) | - |
| `-v, --verbose` | Verbose mode | - |
| `--columns TEXT` | Custom columns (e.g., `ENTITY=entity_id`) | - |
| `--no-headers` | Omit table headers | - |
| `--sort-by TEXT` | Sort by jsonpath expression | - |

**Subcommand-Specific Options:**

| Command | Option | Description |
|---------|--------|-------------|
| `service call` | `--arguments TEXT` | Comma-separated key=value pairs |
| `state get` | (none) | Just takes ENTITY positional arg |
| `state list` | (none) | Lists all states |

**Common Usage Patterns:**
```bash
# Get entity as YAML (includes attributes)
source .env && hass-cli -o yaml state get sensor.argo_nora_registro_compiti

# List all automations as JSON
source .env && hass-cli -o json state list | jq '.[] | select(.entity_id | startswith("automation."))'

# Trigger automation with argument
source .env && hass-cli service call automation.trigger --arguments entity_id=automation.notifiche_didup

# Reload with extended timeout
source .env && hass-cli --timeout 30 service call automation.reload
```

### 🚨 hass-cli Command Structure Mistakes

**Common mistakes with non-existent subcommands, flags, and incorrect command patterns.**

---

### ❌ Mistake 1: Non-Existent `automation` Subcommand

**Symptom:** `Error: No such command 'automation'`

**What went wrong:**
```bash
# ❌ WRONG - No such subcommand exists
hass-cli automation info --id automation.sveglia_nora
hass-cli automation list
hass-cli automation trigger automation.name
```

**Root Cause:**
hass-cli does **not** have an `automation` subcommand. Automations are state entities in Home Assistant, accessed through the `state` commands.

**Correct usage:**
```bash
# ✅ CORRECT - Use state commands for automations
source .env && hass-cli state get automation.sveglia_nora

# ✅ List all automations
source .env && hass-cli state list | grep automation.

# ✅ Get automation state with attributes
source .env && hass-cli -o yaml state get automation.sveglia_nora

# ✅ Trigger automation (use service call, not automation subcommand)
source .env && hass-cli service call automation.trigger --arguments entity_id=automation.sveglia_nora
```

---

### ❌ Mistake 2: Non-Existent `--attributes` Flag

**Symptom:** `Error: No such option: --attributes`

**What went wrong:**
```bash
# ❌ WRONG - state get doesn't have an --attributes flag
hass-cli state get sensor.temperature --attributes
```

**Root Cause:**
`state get` automatically returns **all attributes** without needing a flag. The `--attributes` flag simply doesn't exist in hass-cli.

**Correct usage:**
```bash
# ✅ CORRECT - attributes are included by default
source .env && hass-cli state get sensor.temperature

# ✅ For cleaner output, use YAML format
source .env && hass-cli -o yaml state get sensor.temperature

# ✅ For JSON output
source .env && hass-cli -o json state get sensor.temperature
```

---

### ❌ Mistake 3: Global Options After Subcommand

**Symptom:** `Error: No such option` (already covered in detail above)

**Quick reminder:**
```bash
# ❌ WRONG
hass-cli state get sensor.temp --output yaml

# ✅ CORRECT - global options BEFORE subcommand
hass-cli -o yaml state get sensor.temp
```

---

### 📋 hass-cli Command Reference

**Available Subcommands:**

| Subcommand | Purpose | Example |
|------------|---------|---------|
| `state` | Get/list entity states | `hass-cli state get sensor.temp` |
| `service` | Call Home Assistant services | `hass-cli service call automation.reload` |
| `raw` | Direct REST API access | `hass-cli raw get /api/states` |
| `info` | System information (NOT entity-specific) | `hass-cli info` |

**Common Entity Access Patterns:**

| Task | Command |
|------|---------|
| Get automation state | `hass-cli state get automation.name` |
| List all automations | `hass-cli state list \| grep automation.` |
| Get sensor with attributes | `hass-cli -o yaml state get sensor.name` |
| Trigger automation | `hass-cli service call automation.trigger --arguments entity_id=automation.name` |

**Key Takeaway:** If a subcommand like `automation info`, `automation list`, or `--attributes` seems like it "should" exist but doesn't, check the actual command structure with `hass-cli --help` or `hass-cli <subcommand> --help`.

---

### Using hass-cli (Local, via REST API)

All `hass-cli` commands use environment variables automatically:

```bash
# List entities
hass-cli state list

# Get specific state
hass-cli state get sensor.entity_name

# Call services
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
```

### Using SSH for File Operations

```bash
# Deploy files via SCP
scp automations.yaml ha:/homeassistant/

# Pull latest from git
ssh ha "cd /homeassistant && git pull"

# Check git status on HA
ssh ha "cd /homeassistant && git status"
```

**SSH Fingerprint Display:** When connecting via SSH, you may see a host key fingerprint displayed as ASCII art:
```
+--[ED25519 256]--+
|        .o..    |
|       .  o     |
...
+----[SHA256]-----+
```
This is **normal visual confirmation**, NOT a prompt to accept an unknown host. The connection proceeds automatically - no action required. This appears because `VisualHostKey yes` is enabled in the SSH config.

**Note:** `ha core check/restart/logs` commands require Supervisor access (not available via SSH add-on). Use hass-cli instead:
```bash
# Reload automations (instead of restart)
hass-cli service call automation.reload

# Check for errors via API
hass-cli raw get /api/error/all
```

## 🚨 Service Call Mistakes: hass-cli vs REST API

**Common mistake patterns when choosing between hass-cli and REST API for service calls.**

### ❌ Mistake 1: hass-cli with Nested Data

**Symptom:** `ValueError: dictionary update sequence element #0 has length 1; 2 is required`

**What went wrong:**
```bash
# ❌ WRONG: hass-cli --arguments with JSON and nested data
hass-cli service call notify.mobile_app_telefono_clelia \
  --arguments '{"message":"command_high_accuracy_mode","data":{"command":"turn_off"}}'
```

**Root Cause:**
1. `--arguments` expects **comma-separated `key=value` pairs**, NOT JSON
2. `--arguments` **cannot handle nested dictionaries** like `data: {command: "turn_off"}`

**Correct hass-cli usage (simple cases only):**
```bash
# ✅ Works for flat structures
hass-cli service call automation.trigger --arguments 'entity_id=automation.name'

# ❌ Does NOT work for nested data like:
# data: {command: "turn_off"}  ← Nested = hass-cli cannot handle
```

**Lesson:** hass-cli is **not suitable** for service calls with nested data structures.

---

### ❌ Mistake 2: REST API Wrong Payload Format

**Symptom:** `400: Bad Request`

**What went wrong:**
```bash
# ❌ WRONG: Incorrect payload format
curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"notify.mobile_app_telefono_clelia","message":"command_high_accuracy_mode","data":{"command":"turn_off"}}' \
  "$HASS_SERVER/api/services/notify/mobile_app_telefono_clelia"
```

**Root Cause:**
1. `entity_id` should NOT be in the payload (service endpoint already specifies it)
2. Missing `target` array (required for notify services)

**Correct format:**
```bash
# ✅ CORRECT: Proper notify service payload
curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"command_high_accuracy_mode","data":{"command":"turn_off"},"target":["mobile_app_telefono_clelia"]}' \
  "$HASS_SERVER/api/services/notify/mobile_app_telefono_clelia"
```

**Payload comparison:**

| Element | Wrong | Correct |
|---------|-------|---------|
| `entity_id` | In payload | ❌ Don't include (endpoint specifies service) |
| `target` | Missing | ✅ Required array for notify services |
| `message` | ✅ Correct | ✅ Correct |
| `data` | ✅ Correct | ✅ Correct |

---

### ✅ Decision Tree: hass-cli vs REST API

```
Need to call a HA service?
│
├─ Simple flat parameters (no nested data)?
│  └─ Use hass-cli
│     hass-cli service call automation.trigger --arguments 'entity_id=automation.name'
│
└─ Nested data structures or complex payloads?
   └─ Use REST API with curl
      curl -X POST "$HASS_SERVER/api/services/<domain>/<service>" \
        -H "Authorization: Bearer $HASS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{ ... JSON payload ... }'
```

---

### 📋 Quick Reference: Correct Payload Formats

**hass-cli (flat parameters only):**
```bash
hass-cli service call <domain>.<service> --arguments 'key1=value1,key2=value2'
```

**REST API (supports nested data):**
```json
{
  "entity_id": "domain.service_name",     // For non-notify services
  "message": "...",                        // For notify services
  "data": {                                // Nested data
    "key": "value",
    "nested": {
      "key2": "value2"
    }
  },
  "target": ["entity_id"]                  // For notify services only
}
```

---

### 📱 Mobile App Commands Reference

| Command | REST API Payload |
|---------|-----------------|
| High accuracy ON | `{"message":"command_high_accuracy_mode","data":{"command":"turn_on"},"target":["mobile_app_xyz"]}` |
| High accuracy OFF | `{"message":"command_high_accuracy_mode","data":{"command":"turn_off"},"target":["mobile_app_xyz"]}` |
| Background fetch | `{"message":"command_background_fetch","data":{},"target":["mobile_app_xyz"]}` |

**Example:** Disable high accuracy mode
```bash
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"command_high_accuracy_mode","data":{"command":"turn_off"},"target":["mobile_app_telefono_clelia"]}' \
  "$HASS_SERVER/api/services/notify/mobile_app_telefono_clelia"
```

---

### Key Takeaways

1. **hass-cli `--arguments` = flat key=value pairs only** - No JSON, no nesting
2. **REST API = full JSON support** - Use for nested data structures
3. **Notify services need `target` array** - Specifies which device(s) to notify
4. **Never include `entity_id` in REST payload** - The URL endpoint specifies the service
5. **Test in Developer Tools first** - Verify service parameters before scripting

## Template Evaluation via REST API

Evaluate Jinja2 templates remotely using the `/api/template` endpoint. **Critical escaping rules apply.**

### Basic Template Evaluation
```bash
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states(\"sensor.temperature\") }}"}' \
  "$HASS_SERVER/api/template"
```

### ⚠️ JSON Escaping Rules (CRITICAL)

When embedding Jinja2 in JSON within bash:

| Character | Escape Method | Example |
|-----------|---------------|---------|
| Inner `"` | Use `\"` | `states(\"sensor.foo\")` |
| `$` in bash | Use single quotes for outer shell | `'{"template": "..."}'` |
| Emojis | **AVOID** - causes invalid JSON | Use text descriptions instead |
| Newlines | Use `\\n` or avoid | Single-line templates preferred |

### ✅ Correct Examples
```bash
# Simple state check
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states(\"cover.tapparella_nora\") }}"}' \
  "$HASS_SERVER/api/template"

# Multiple states with string concatenation
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "State: {{ states(\"sensor.a\") }}, Attr: {{ state_attr(\"sensor.a\", \"unit\") }}"}' \
  "$HASS_SERVER/api/template"

# Boolean logic
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ is_state(\"binary_sensor.foo\", \"on\") and is_state(\"binary_sensor.bar\", \"off\") }}"}' \
  "$HASS_SERVER/api/template"
```

### ❌ Common Mistakes
```bash
# WRONG: Emojis in template (invalid UTF-8/JSON)
-d '{"template": "Status: ✅ {{ states(\"sensor.foo\") }}"}'

# WRONG: Unescaped inner quotes
-d '{"template": "{{ states("sensor.foo") }}"}'

# WRONG: Double quotes for outer shell ($ expansion issues)
-d "{"template": "{{ states(\"sensor.foo\") }}"}"
```

### Alternative: Use hass-cli raw
For complex templates, use `hass-cli raw` with a JSON file:
```bash
# Create template file
echo '{"template": "{{ now() }}"}' > /tmp/tpl.json

# Execute
source .env && hass-cli raw post /api/template < /tmp/tpl.json
```

## Deployment Workflows

### Standard Git Workflow (Final Changes)

Use for changes you want in version control:

```bash
# 1. Make changes locally
# 2. Check validity
ssh ha "ha core check"

# 3. Commit and push
git add file.yaml
git commit -m "Description"
git push

# 4. CRITICAL: Pull to HA instance
ssh ha "cd /homeassistant && git pull"

# 5. Reload or restart
hass-cli service call automation.reload  # if reload sufficient
# OR
ssh ha "ha core restart"  # if restart needed

# 6. Verify
hass-cli state get sensor.new_entity
ssh ha "ha core logs | grep -i error | tail -20"
```

### Rapid Development Workflow (Testing/Iteration)

Use `scp` for quick testing before committing:

```bash
# 1. Make changes locally
# 2. Quick deploy
scp automations.yaml ha:/homeassistant/

# 3. Reload/restart
hass-cli service call automation.reload

# 4. Test and iterate (repeat 1-3 as needed)

# 5. Once finalized, commit and push to git
git add automations.yaml
git commit -m "Final tested changes"
git push

# 6. CRITICAL: Sync HA git state (reset scp'd files, then pull)
# First, discard local changes for the specific files we scp'd
ssh ha "cd /homeassistant && git checkout -- automations.yaml"
# Then pull (now clean, will succeed)
ssh ha "cd /homeassistant && git pull"
```

**Why `git checkout -- <files>` before `git pull`:**
After testing with `scp`, the HA instance has modified files. A regular `git pull` would fail with "uncommitted local changes" error. The safe approach:
1. `git checkout -- <files>` - reverts ONLY the specific files we scp'd to their last committed state
2. `git pull` - now succeeds since there are no conflicts

**Important:** Only checkout the files you explicitly scp'd. Do NOT use `git reset --hard` as it would discard ALL local modifications, including any unrelated changes on the server.

### CRITICAL: Never Use `git reset --hard` on HA Server

**FORBIDDEN command:**
```bash
# NEVER DO THIS - can lose uncommitted work on the server
ssh ha "cd /homeassistant && git reset --hard origin/master"
```

**Why this is dangerous:**
- The HA server may have uncommitted changes (manual edits, UI changes, other tools)
- `git reset --hard` discards ALL local modifications without warning
- There is no recovery from this operation

**Even after force-push, use this safe pattern instead:**
```bash
# 1. ALWAYS check for uncommitted changes first
ssh ha "cd /homeassistant && git status"

# 2. If only expected files are modified, checkout those specific files
ssh ha "cd /homeassistant && git checkout -- file1.yaml file2.yaml"

# 3. Then pull (or fetch + rebase for force-push scenarios)
ssh ha "cd /homeassistant && git fetch origin && git rebase origin/master"

# 4. If unexpected changes exist, ASK THE USER before proceeding
```

### 🚨 CRITICAL: INSPECT Before Discarding HA Server Changes

**NEVER run `git checkout --` on the HA server without FIRST inspecting the differences.**

When `git pull` fails with "uncommitted local changes":

```bash
# ✅ CORRECT WORKFLOW:
# Step 1: INSPECT what changed and WHY
ssh ha "cd /homeassistant && git diff automations.yaml"

# Step 2: ANALYZE the output
# - Are these MY scp-deployed changes from this session? → Safe to discard
# - Are these UNKNOWN changes from outside this session? → STOP, investigate

# Step 3: ONLY THEN decide
# If your own changes: git checkout -- file.yaml
# If unknown changes: Ask user, do NOT discard blindly

# ❌ FORBIDDEN: Blind discard without inspection
ssh ha "cd /homeassistant && git checkout -- file.yaml"  # NEVER without diff first!
```

**Why this matters:**
- The HA server may have legitimate changes from: UI edits, other tools, manual SSH sessions, or another developer
- Blindly discarding loses those changes with NO recovery
- This violates the "Evidence > assumptions" principle

**Evidence > Assumptions**: Always verify the nature of conflicts before discarding.

### 🚨 MANDATORY: Git Conflict Resolution Protocol

**When `git pull` fails with "local changes would be overwritten":**

**NEVER run `git checkout` or `git reset` without inspection. Follow this protocol:**

1. **INSPECT FIRST - What changed and why?**
   ```bash
   ssh ha "cd /homeassistant && git status"
   ssh ha "cd /homeassistant && git diff <file>"
   ```

2. **ANALYZE: Categorize the changes**
   - ✅ **My scp changes from THIS session** → Safe to discard (they're in commits being pulled)
   - ⚠️ **Unknown changes** → STOP, ask user, do NOT discard
   - ⚠️ **UI-generated changes** (automations.yaml, scenes.yaml) → May be legitimate
   - ⚠️ **File timestamps different** → Investigate why

3. **DECISION TREE:**
   ```
   Are these MY scp changes from this session?
   ├─ YES, and commits being pulled contain these changes
   │  └─ SAFE: git checkout <files> && git pull
   ├─ YES, but commits DON'T contain these changes
   │  └─ DANGER: Ask user - these changes would be LOST
   └─ NO / UNKNOWN
      └─ DANGER: Ask user - potential data loss
   ```

4. **Only then checkout:**
   ```bash
   ssh ha "cd /homeassistant && git checkout <file1> <file2>"
   ssh ha "cd /homeassistant && git pull"
   ```

**Evidence > Assumptions**: The HA server may have legitimate changes from:
- UI edits (automations, scripts, scenes created via UI)
- Other tools (Studio Code Server, File Editor)
- Manual SSH edits
- Automated processes (integrations writing config)

**Blindly discarding = Data loss with NO recovery**

**Example from 2026-01-16 session:**
```bash
# ❌ WRONG: Immediately discarding without inspection
ssh ha "cd /homeassistant && git checkout ."

# ✅ RIGHT: Inspect first
ssh ha "cd /homeassistant && git diff pyscript/portaleargo_telegram_notifier.py" | head -50
# → Saw these were MY scp changes from earlier
# → Commits being pulled (7bd5fa7, 5111060, a771ad2) contain these changes
# → SAFE to discard
ssh ha "cd /homeassistant && git checkout pyscript/portaleargo_telegram_notifier.py automations/tests/tests.yaml"
```

**When to use scp:**
- 🚀 Rapid iteration and testing
- 🔄 Frequent small adjustments
- 🧪 Experimental changes
- 🎨 UI/Dashboard work

**When to use git:**
- ✅ Final tested changes
- 📦 Version control tracking
- 🔒 Important configs
- 👥 Changes to document

### ⚙️ SCP + Git Pull Workflow: Avoiding Conflicts

**Problem**: When you deploy via scp for rapid iteration, those changes create local modifications on the HA server. Later git pull operations will conflict.

**Solution Patterns:**

#### Pattern 1: SCP for Testing, Git for Final (RECOMMENDED)
```bash
# 1. Rapid iteration with scp
scp automations/test.yaml ha:/homeassistant/automations/
hass-cli service call automation.reload

# Test, verify, iterate...

# 2. When satisfied, commit locally
git add automations/test.yaml
git commit -m "Add test automation"
git push

# 3. Clean server state and pull
ssh ha "cd /homeassistant && git checkout automations/test.yaml"  # Discard scp version
ssh ha "cd /homeassistant && git pull"  # Pull committed version
```

#### Pattern 2: SCP-Only for Throwaway Changes
```bash
# For one-off tests that won't be committed
scp test_script.py ha:/tmp/  # Use /tmp, not /homeassistant
ssh ha "python /tmp/test_script.py"
```

#### Pattern 3: Git-Only for Production Changes
```bash
# Skip scp entirely
git add <files>
git commit -m "message"
git push
ssh ha "cd /homeassistant && git pull"
hass-cli service call <reload_service>
```

**Decision Tree:**
```
Is this a quick test/debug change?
├─ YES → SCP to /tmp or use Pattern 1 (scp → test → commit → git pull)
└─ NO → Git-only workflow (Pattern 3)

Multiple rapid iterations needed?
├─ YES → SCP workflow, then final git commit + pull
└─ NO → Git-only workflow
```

**Server State Awareness:**
Always know what's on the server:
```bash
ssh ha "cd /homeassistant && git status"  # Check for uncommitted changes
ssh ha "cd /homeassistant && git log --oneline -5"  # Check current commit
```

## Reload vs Restart Decision Making

**ALWAYS assess if reload is sufficient before requiring a full restart.**

### Can be reloaded (fast, preferred):
- ✅ Automations: `hass-cli service call automation.reload`
- ✅ Scripts: `hass-cli service call script.reload`
- ✅ Scenes: `hass-cli service call scene.reload`
- ✅ Template entities: `hass-cli service call template.reload`
- ✅ Groups: `hass-cli service call group.reload`
- ✅ Themes: `hass-cli service call frontend.reload_themes`

### Require full restart:
- ❌ Min/Max sensors and platform-based sensors
- ❌ New integrations in configuration.yaml
- ❌ Core configuration changes
- ❌ MQTT sensor/binary_sensor platforms

## Automation Locations

**Automations can exist in multiple locations:**

| Location | Description |
|----------|-------------|
| `automations.yaml` | Main automation file (HA default) |
| `automations/*/` | Split automations by category |
| `packages/*/` | HA packages bundling automations with related entities |

**Important:** When searching for or analyzing automations, always check ALL three locations. Packages can contain automations alongside input_booleans, sensors, scripts, and other related entities.

**Entity Registry:** The unique_id in the entity registry corresponds to the `id:` field in the automation YAML. If automations appear duplicated in the UI, check for:
- Mismatched `id:` vs `alias:` (ID should match the purpose)
- Orphaned registry entries from deleted automations
- Old numeric IDs that were migrated to descriptive IDs

### Modifying the Entity Registry

**CRITICAL:** The entity registry is cached in memory. Edits while HA is running will be overwritten on shutdown.

**Correct procedure:**
```bash
# 1. STOP HA first
ssh ha "ha core stop"
sleep 10

# 2. Edit the registry (example: remove orphaned entries)
ssh ha "python3 << 'EOF'
import json
with open('/homeassistant/.storage/core.entity_registry', 'r') as f:
    data = json.load(f)

# Remove specific entries
data['data']['entities'] = [
    e for e in data['data']['entities']
    if e.get('unique_id') not in ['id_to_remove']
]

with open('/homeassistant/.storage/core.entity_registry', 'w') as f:
    json.dump(data, f, indent=2)
EOF"

# 3. START HA - new entries will be created from YAML
ssh ha "ha core start"
```

**Common registry operations:**
- Remove orphaned entries (unique_id no longer in YAML)
- Fix entity_id mismatches (rename entity_id field)
- Clean up duplicate entries with `_2`, `_3` suffixes

## Automation Verification Workflow

**ALWAYS verify automations after deployment:**

### Step 1: Deploy
```bash
git add automations.yaml && git commit -m "..." && git push
ssh ha "cd /homeassistant && git pull"
```

### Step 2: Check Configuration
```bash
ssh ha "ha core check"
```

### Step 3: Reload
```bash
hass-cli service call automation.reload
```

### Step 4: Manually Trigger
```bash
hass-cli service call automation.trigger --arguments entity_id=automation.name
```

**Why trigger manually?**
- Instant feedback (don't wait for scheduled triggers)
- Verify logic before production
- Catch errors immediately

### Step 5: Check Logs
```bash
sleep 3
ssh ha "ha core logs | grep -i 'automation_name' | tail -20"
```

**Success indicators:**
- `Initialized trigger AutomationName`
- `Running automation actions`
- `Executing step ...`
- No ERROR or WARNING messages

**Error indicators:**
- `Error executing script`
- `Invalid data for call_service`
- `TypeError`, `Template variable warning`

### Step 6: Verify Outcome

**For notifications:**
- Ask user if they received it
- Check logs for mobile_app messages

**For device control:**
```bash
hass-cli state get switch.device_name
```

**For sensors:**
```bash
hass-cli state get sensor.new_sensor
```

### Step 7: Fix and Re-test if Needed
If errors found:
1. Identify root cause from error messages
2. Fix the issue
3. Re-deploy (steps 1-2)
4. Re-verify (steps 3-6)

## Dashboard Management

### Dashboard Fundamentals

**What are Lovelace Dashboards?**
- JSON files in `.storage/` directory (e.g., `.storage/lovelace.control_center`)
- UI configuration for Home Assistant frontend
- Optimizable for different devices (mobile, tablet, wall panels)

**Critical Understanding:**
- Creating dashboard file is NOT enough - must register in `.storage/lovelace_dashboards`
- Dashboard changes don't require HA restart (just browser refresh)
- Use panel view for full-screen content (maps, cameras)
- Use sections view for organized multi-card layouts

### Dashboard Development Workflow

**Rapid Iteration with scp (Recommended for dashboards):**

```bash
# 1. Make changes locally
vim .storage/lovelace.control_center

# 2. Deploy immediately (no git commit yet)
scp .storage/lovelace.control_center ha:/homeassistant/.storage/

# 3. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
# No HA restart needed!

# 4. Iterate: Repeat 1-3 until perfect

# 5. Commit when stable
git add .storage/lovelace.control_center
git commit -m "Update dashboard layout"
git push
ssh ha "cd /homeassistant && git pull"
```

**Why scp for dashboards:**
- Instant feedback (no HA restart)
- Iterate quickly on visual changes
- Commit only stable versions

### Creating New Dashboard

**Complete workflow:**

```bash
# Step 1: Create dashboard file
cp .storage/lovelace.my_home .storage/lovelace.new_dashboard

# Step 2: Register in lovelace_dashboards
# Edit .storage/lovelace_dashboards to add:
{
  "id": "new_dashboard",
  "show_in_sidebar": true,
  "icon": "mdi:tablet-dashboard",
  "title": "New Dashboard",
  "require_admin": false,
  "mode": "storage",
  "url_path": "new-dashboard"
}

# Step 3: Deploy both files
scp .storage/lovelace.new_dashboard ha:/homeassistant/.storage/
scp .storage/lovelace_dashboards ha:/homeassistant/.storage/

# Step 4: Restart HA (required for registry changes)
ssh ha "ha core restart"
sleep 30

# Step 5: Verify appears in sidebar
```

**Update .gitignore to track:**
```gitignore
# Exclude .storage/ by default
.storage/

# Include dashboard files
!.storage/lovelace.new_dashboard
!.storage/lovelace_dashboards
```

### View Types Decision Matrix

**Use Panel View when:**
- Displaying full-screen map (vacuum, cameras)
- Single large card needs full width
- Want zero margins/padding
- Minimize scrolling

**Use Sections View when:**
- Organizing multiple cards
- Need responsive grid layout
- Building multi-section dashboards

**Layout Example:**
```json
// Panel view - full width, no margins
{
  "type": "panel",
  "title": "Vacuum Map",
  "path": "map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "entity": "vacuum.dusty"
    }
  ]
}

// Sections view - organized, has ~10% margins
{
  "type": "sections",
  "title": "Home",
  "sections": [
    {
      "type": "grid",
      "cards": [...]
    }
  ]
}
```

### Card Types Quick Reference

**Mushroom Cards (Modern, Touch-Optimized):**
```json
{
  "type": "custom:mushroom-light-card",
  "entity": "light.living_room",
  "use_light_color": true,
  "show_brightness_control": true,
  "collapsible_controls": true,
  "fill_container": true
}
```
- Best for tablets and touch screens
- Animated, colorful icons
- Built-in slider controls

**Mushroom Template Card (Dynamic Content):**
```json
{
  "type": "custom:mushroom-template-card",
  "primary": "All Doors",
  "secondary": "{% set sensors = ['binary_sensor.front_door'] %}\n{% set open = sensors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ sensors | length }} open",
  "icon": "mdi:door",
  "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
}
```
- Use Jinja2 templates for dynamic content
- Color-code status with icon_color
- Multi-line templates use `\n` in JSON

**Tile Card (Built-in, Modern):**
```json
{
  "type": "tile",
  "entity": "climate.thermostat",
  "features": [
    {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
    {"type": "target-temperature"}
  ]
}
```
- No custom cards required
- Built-in features for controls

### Common Template Patterns

**Counting Open Doors:**
```jinja2
{% set door_sensors = [
  'binary_sensor.front_door',
  'binary_sensor.back_door'
] %}
{% set open = door_sensors | select('is_state', 'on') | list | length %}
{{ open }} / {{ door_sensors | length }} open
```

**Color-Coded Days Until:**
```jinja2
{% set days = state_attr('sensor.bin_collection', 'daysTo') | int %}
{% if days <= 1 %}red
{% elif days <= 3 %}amber
{% elif days <= 7 %}yellow
{% else %}grey
{% endif %}
```

**Conditional Display:**
```jinja2
{% set bins = [] %}
{% if days and days | int <= 7 %}
  {% set bins = bins + ['Recycling'] %}
{% endif %}
{% if bins %}This week: {{ bins | join(', ') }}{% else %}None this week{% endif %}
```

**IMPORTANT:** Always use `| int` or `| float` to avoid type errors when comparing

### Tablet Optimization

**Screen-specific layouts:**
- 11-inch tablets: 3-4 columns
- Touch targets: minimum 44x44px
- Minimize scrolling: Use panel view for full-screen
- Visual feedback: Color-coded status (red/green/amber)

**Grid Layout for Tablets:**
```json
{
  "type": "grid",
  "columns": 3,
  "square": false,
  "cards": [
    {"type": "custom:mushroom-light-card", "entity": "light.living_room"},
    {"type": "custom:mushroom-light-card", "entity": "light.bedroom"}
  ]
}
```

### Common Dashboard Pitfalls

**Problem 1: Dashboard Not in Sidebar**
- **Cause:** File created but not registered
- **Fix:** Add to `.storage/lovelace_dashboards` and restart HA

**Problem 2: "Configuration Error" in Card**
- **Cause:** Custom card not installed, wrong syntax, template error
- **Fix:**
  - Check HACS for card installation
  - Check browser console (F12) for details
  - Test templates in Developer Tools → Template

**Problem 3: Auto-Entities Fails**
- **Cause:** `card_param` not supported by card type
- **Fix:** Use cards that accept `entities` parameter:
  - ✅ Works: `entities`, `vertical-stack`, `horizontal-stack`
  - ❌ Doesn't work: `grid`, `glance` (without specific syntax)

**Problem 4: Vacuum Map Has Margins/Scrolling**
- **Cause:** Using sections view (has margins)
- **Fix:** Use panel view for full-width, no scrolling

**Problem 5: Template Type Errors**
- **Error:** `TypeError: '<' not supported between instances of 'str' and 'int'`
- **Fix:** Use type filters: `states('sensor.days') | int < 7`

### Dashboard Debugging

**1. Browser Console (F12):**
- Check for red errors when loading dashboard
- Common: "Custom element doesn't exist" → Card not installed

**2. Validate JSON Syntax:**
```bash
python3 -m json.tool .storage/lovelace.control_center > /dev/null
```

**3. Test Templates:**
```
Home Assistant → Developer Tools → Template
Paste template to test before adding to dashboard
```

**4. Verify Entities:**
```bash
hass-cli state get binary_sensor.front_door
```

**5. Clear Browser Cache:**
- Hard refresh: Ctrl+F5 or Cmd+Shift+R
- Try incognito window

## Real-World Examples

### Quick Controls Dashboard Section
```json
{
  "type": "grid",
  "title": "Quick Controls",
  "cards": [
    {
      "type": "custom:mushroom-template-card",
      "primary": "All Doors",
      "secondary": "{% set doors = ['binary_sensor.front_door', 'binary_sensor.back_door'] %}\n{% set open = doors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ doors | length }} open",
      "icon": "mdi:door",
      "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
    },
    {
      "type": "tile",
      "entity": "climate.thermostat",
      "features": [
        {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
        {"type": "target-temperature"}
      ]
    }
  ]
}
```

### Individual Light Cards (Touch-Friendly)
```json
{
  "type": "grid",
  "title": "Lights",
  "columns": 3,
  "cards": [
    {
      "type": "custom:mushroom-light-card",
      "entity": "light.office_studio",
      "name": "Office",
      "use_light_color": true,
      "show_brightness_control": true,
      "collapsible_controls": true
    }
  ]
}
```

### Full-Screen Vacuum Map
```json
{
  "type": "panel",
  "title": "Vacuum",
  "path": "vacuum-map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "vacuum_platform": "Tasshack/dreame-vacuum",
      "entity": "vacuum.dusty"
    }
  ]
}
```

## Common Commands Quick Reference

```bash
# Configuration
ssh ha "ha core check"
ssh ha "ha core restart"

# Logs
ssh ha "ha core logs | tail -50"
ssh ha "ha core logs | grep -i error | tail -20"

# State/Services
hass-cli state list
hass-cli state get entity.name
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name

# Deployment
git add . && git commit -m "..." && git push
ssh ha "cd /homeassistant && git pull"
scp file.yaml ha:/homeassistant/

# Dashboard deployment
scp .storage/lovelace.my_dashboard ha:/homeassistant/.storage/
python3 -m json.tool .storage/lovelace.my_dashboard > /dev/null  # Validate JSON

# Quick test cycle
scp automations.yaml ha:/homeassistant/
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
ssh ha "ha core logs | grep -i 'automation' | tail -10"
```

## 📁 Path Management: Project vs User vs Server

**Common Path Confusion Sources:**

| Context | Correct Path | WRONG Path |
|---------|-------------|------------|
| **Claudedocs** (investigation notes) | `/home/pantinor/data/repo/personal/hassio/.claude/claudedocs/` | `/home/pantinor/.claude/claudedocs/` ❌ |
| **Serena memories** | `.serena/memories/` (project-relative) | `/home/pantinor/.serena/` ❌ |
| **HA config on server** | `ha:/homeassistant/` (SSH alias) | `root@homeassistant.local:/config/` ❌ |
| **Temp files on server** | `ha:/tmp/` | `ha:/homeassistant/tmp/` ❌ |
| **Global Claude config** | `/home/pantinor/.claude/` | Project `.claude/` ❌ |

**Rules:**
1. **Investigation notes** → Always project `.claude/claudedocs/`
2. **SSH operations** → Always use `ha:` alias (defined in `~/.ssh/config`)
3. **Server paths** → Always `/homeassistant/` not `/config/` (they're symlinked but /homeassistant is git root)
4. **Temp files** → `/tmp/` on server, NOT in git-tracked directories

## 🛡️ MANDATORY: Validate BEFORE Deploy

**CRITICAL RULE:** Always run `ha core check` BEFORE deploying changes, not after.

```bash
# ✅ CORRECT order
# 1. Make local changes
# 2. Validate configuration FIRST
ssh ha "ha core check"
# 3. Only if valid, deploy
scp file.yaml ha:/homeassistant/
# OR: git push && ssh ha "cd /homeassistant && git pull"
# 4. Reload/restart as needed
# 5. Verify behavior

# ❌ WRONG order (catches problems too late)
scp file.yaml ha:/homeassistant/
hass-cli service call automation.reload
# Error occurs...
ssh ha "ha core check"  # Too late!
```

**Why this matters:**
- Catches syntax errors before they reach production
- Avoids deploying broken config to running HA instance
- Prevents unnecessary restart attempts with invalid config
- Follows "Evidence > assumptions" principle

## Built-in Logger Filters (No Custom Components Needed)

**HA has native regex log filtering** - always use this instead of custom components for suppressing noisy log messages.

**Location:** `configuration.yaml` under `logger: filters:`

```yaml
logger:
  default: info
  filters:
    <logger_name>:
      - "^regex_pattern_to_filter"
```

**Example - Filter Ariston cycle messages:**
```yaml
logger:
  filters:
    homeassistant.components.sensor.recorder:
      - "^Detected new cycle for sensor\\.ariston_"
```

**Finding the logger name:** Look at log message format:
```
INFO (Recorder) [homeassistant.components.sensor.recorder] Detected new cycle...
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                 This is the logger name to use in filters
```

**Reload behavior:** Logger filters require a **restart** to take effect. `homeassistant.reload_core_config` does NOT reload logger filters.

## Best Practices Summary

1. **🧪 TEST templates BEFORE suggesting fixes** - ALWAYS use `/api/template` endpoint to verify expressions work before modifying code. See "Template Testing Protocol" below.
2. **Validate configuration BEFORE deploy**: `ssh ha "ha core check"` (see section above)
3. **Prefer reload over restart** when possible
4. **Test automations manually** after deployment
5. **Check logs** for errors after every change
6. **Use scp for rapid iteration**, git for final changes
7. **Verify outcomes** - don't assume it worked
8. **Use Context7** for current documentation
9. **Test templates in Dev Tools** before adding to dashboards
10. **Validate JSON syntax** before deploying dashboards
11. **Test on actual device** for tablet dashboards
12. **Color-code status** for visual feedback (red/green/amber)
13. **Commit only stable versions** - test with scp first
14. **Add user-friendly logging** to automations and scripts - use emoji-based `system_log.write` for clarity

### 🧪 Template Testing Protocol (MANDATORY)

**🚨 CRITICAL: Before suggesting ANY template fix, you MUST test it via the REST API.**

**Why:** Jinja2 filter behavior in Home Assistant can be counterintuitive. Testing prevents breaking working automations with "fixes" that don't actually work.

#### How to Test Templates

```bash
# Test a simple template
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states('\''sensor.example'\'') }}"}' \
  "$HASS_SERVER/api/template"

# Test with state_attr and defaults
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ state_attr('\''device_tracker.phone'\'', '\''gps_accuracy'\'')|int(999) }}"}' \
  "$HASS_SERVER/api/template"

# Test multi-line templates (use \\n for newlines in JSON)
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "Line 1\\nLine 2: {{ now() }}"}' \
  "$HASS_SERVER/api/template"
```

#### Common Jinja2 Filter Pitfalls

| Pattern | Works? | Explanation |
|---------|--------|-------------|
| `value|int(999)` | ✅ | `int` filter with default parameter |
| `value|default(999)|int` | ❌ | `default` returns string/None, `int` can't handle it |
| `value|default('unknown')` | ✅ | String default works fine |
| `value|int` | ❌ | Fails if value is `None` (no default) |

**Example from 2026-01-20 session:**
```yaml
# ❌ BROKEN - This was in the automation:
{{ state_attr('device_tracker.phone', 'gps_accuracy')|default(999)|int }}

# ✅ FIXED - Changed to:
{{ state_attr('device_tracker.phone', 'gps_accuracy')|int(999) }}
```

**The error:** `ValueError: int got invalid input 'None'` with "but no default was specified"
**The root cause:** `|default(999)|int` passes `None` to `int` filter, which doesn't recognize it as having a default.

#### Testing Checklist

Before suggesting any template fix:
- [ ] Tested the CURRENT broken expression - confirmed it fails
- [ ] Tested the PROPOSED fix - confirmed it works
- [ ] Tested edge cases (None, missing attribute, wrong type)
- [ ] Compared both outputs side-by-side

**Only then suggest the fix.**

#### Quick Test Patterns

```bash
# Test state attribute exists
state_attr('entity_id', 'attribute_name')|default('not set')

# Test state attribute with int conversion and default
state_attr('entity_id', 'attr')|int(999)  # NOT: |default(999)|int

# Test state with default
states('sensor.missing')|default('unknown')

# Test numeric state with conversion
states('sensor.temperature')|float(0)|round(1)  # Has default parameter

# Test nested attribute access
state_attr('entity_id', 'attr.subattr')|default({})
```

#### 🛡️ Prevention Pattern: Safe Template Defaults

**The best way to avoid template errors is to use safe patterns from the start.**

**Golden Rule:** When using conversion filters (`int`, `float`, `round`), ALWAYS provide the default as a **filter parameter**, not a separate `|default` filter.

```yaml
# ✅ SAFE PATTERNS - Use these by default:

# Integer with default (parameter syntax)
{{ state_attr('device_tracker.phone', 'gps_accuracy')|int(999) }}

# Float with default (parameter syntax)
{{ states('sensor.temperature')|float(0) }}

# Round with default (parameter syntax)
{{ value|round(1) }}
{{ states('sensor.probability')|float(0)|round(1) }}

# String defaults work fine with |default
{{ state_attr('entity', 'source')|default('unknown') }}

# ❌ UNSAFE PATTERNS - Avoid these:

# Don't use |default before |int/|float
{{ state_attr('device_tracker.phone', 'gps_accuracy')|default(999)|int }}  # ERROR!

# Don't use |int/|float without default when value might be None
{{ state_attr('device_tracker.phone', 'gps_accuracy')|int }}  # ERROR if None!
```

**Decision Tree for Safe Templates:**

```
Need to convert attribute/state to a number?
│
├─ Value might be None or missing?
│  └─ Use filter parameter default: |int(999) or |float(0)
│
└─ Value is always present?
   └─ Plain filter is OK: |int or |float

Need a string default?
│
└─ Use |default('fallback')  # This works fine for strings
```

**Copy-Paste Safe Templates:**

```yaml
# GPS accuracy with safe default
{{ state_attr('device_tracker.X', 'gps_accuracy')|int(999) }}

# Temperature with safe default
{{ states('sensor.temperature')|float(0) }}°C

# Probability percentage with safe default
{{ (state_attr('binary_sensor.X', 'probability')|float(0) * 100)|round(1) }}%

# Distance with safe default
{{ states('sensor.distance')|int(0) }} meters
```

**Why this prevents errors:**
- Filter parameters (`|int(999)`) are evaluated BEFORE the filter processes the value
- The `int` filter sees `None` and returns the parameter value `999`
- `|default` creates a separate filter step that passes `None` to `int`, which fails

**Key insight:** In Home Assistant's Jinja2, `int(value, default=999)` works, but `value|default(999)|int` doesn't because the default is "lost" in the filter chain.

### 📝 Logging Best Practices

**Philosophy:** Logs should tell a story that humans can understand at a glance, not just technical execution steps.

#### User-Friendly Logging Pattern

**Use `system_log.write` with emoji indicators:**

```yaml
- action: system_log.write
  data:
    message: "🚪 Gate Opened: {{ person_name }} opened the gate"
    level: info

- action: system_log.write
  data:
    message: "🔊 Alexa Announcement: Sent to 3 devices → \"{{ message }}\""
    level: info

- action: system_log.write
  data:
    message: "📱 Phone Notification: Sent to {{ person_name }}'s phone"
    level: info
```

#### Emoji Guide for Consistency

| Emoji | Use Case | Example |
|-------|----------|---------|
| 🚪 | Door/gate events | "🚪 Gate Opened: Paolo opened the gate" |
| 💡 | Light automation | "💡 Auto Light Off: Bedroom lights timed out" |
| 🪟 | Window checks | "🪟 Window Check: Studio OPEN ⚠️" |
| 🌙 | Night mode | "🌙 Motion Sensor: LOW sensitivity (night)" |
| 📡 | MQTT/network | "📡 MQTT Published: topic → payload" |
| 🔊 | Audio/Alexa | "🔊 Alexa Announcement: Sent to 3 devices" |
| 📱 | Phone notifications | "📱 Phone Notification: Sent vibration alert" |
| ⏰ | Time/schedule | "⏰ Time Window Check: Within hours ✓" |
| 🌡️ | Temperature/climate | "🌡️ Thermostat: Set to 20°C" |
| 🔌 | Power/device control | "🔌 Device Turned ON: Coffee maker" |
| ⚠️ | Warnings | "⚠️ Battery Low: Front door sensor 15%" |
| ❌ | Errors/failures | "❌ Failed: Could not reach device" |
| ✅ | Success/confirmation | "✅ Completed: Backup finished" |

#### Logging Level Guidelines

**Use appropriate log levels:**

```yaml
# INFO - Normal operation, status updates
level: info
message: "🚪 Gate Opened: Paolo opened the gate"

# WARNING - Attention needed, but not critical
level: warning
message: "⚠️ Window Alert: Studio window open during rain"

# ERROR - Something failed that should have worked
level: error
message: "❌ Failed: Could not send notification to Paolo's phone"
```

#### Template Safety in Logs

**Always check trigger context availability:**

```yaml
- variables:
    person_name: >
      {% if trigger.to_state is not defined %}
        Test  # Manual trigger
      {% else %}
        {% set user_id = trigger.to_state.context.user_id %}
        {% if user_id is none %}
          Sistema  # System/automation trigger
        {% else %}
          {% set p = states.person | selectattr('attributes.user_id', 'eq', user_id) | list %}
          {{ p[0].attributes.friendly_name if p | count == 1 else 'Sconosciuto' }}
        {% endif %}
      {% endif %}

- action: system_log.write
  data:
    message: "🚪 Gate Opened: {{ person_name }} opened the gate"
    level: info
```

**Why:** Manual triggers don't have `trigger.to_state`, natural triggers do. Always provide fallbacks.

#### Suppress Verbose Technical Logs

**Add to `configuration.yaml` to reduce noise:**

```yaml
logger:
  default: info
  logs:
    homeassistant.components.automation: warning  # Hide step execution logs
    homeassistant.components.script: warning      # Hide step execution logs
```

**Result:** Your custom `system_log.write` messages appear clearly, without cluttering step-by-step execution noise.

#### When to Add Logging

**Add logs at these key points:**

1. **Automation trigger** - Who/what triggered it
2. **Decision points** - Conditions evaluated (passed/failed)
3. **External actions** - Notifications sent, devices controlled
4. **Important state changes** - Mode changes, threshold crossings
5. **Error conditions** - Failures, timeouts, unavailable devices

**Don't log:**
- Every single action in a sequence (too verbose)
- Internal variable assignments (not user-facing)
- Trivial state checks (unless they affect decisions)

#### Example: Comprehensive Automation Logging

```yaml
- id: window_check_before_rain
  alias: Window Check Before Rain
  triggers:
    - platform: state
      entity_id: sensor.weather_forecast
      to: 'rainy'
  actions:
    - variables:
        open_windows: >
          {% set windows = ['binary_sensor.window_studio', 'binary_sensor.window_salone'] %}
          {{ windows | select('is_state', 'on') | list }}

    - action: system_log.write
      data:
        message: "🌧️ Rain Check: Scanning {{ windows | length }} windows"
        level: info

    - if:
        - condition: template
          value_template: "{{ open_windows | length > 0 }}"
      then:
        - action: system_log.write
          data:
            message: "⚠️ Window Alert: {{ open_windows | length }} window(s) OPEN before rain!"
            level: warning

        - action: notify.telegram
          data:
            message: "⚠️ Chiudi le finestre! Sta per piovere."

        - action: system_log.write
          data:
            message: "📱 Notification: Sent rain alert via Telegram"
            level: info
      else:
        - action: system_log.write
          data:
            message: "✅ All Clear: All windows closed"
            level: info
```

**Log output:**
```
🌧️ Rain Check: Scanning 2 windows
⚠️ Window Alert: 1 window(s) OPEN before rain!
📱 Notification: Sent rain alert via Telegram
```

Clear, informative, human-readable.

### ✅ Pre-Deployment Verification Checklist

**Before ANY deployment (scp or git pull), verify:**

#### File-Level Checks
- [ ] Absolute paths used (no `~`, no relative paths)
- [ ] SSH alias `ha:` used (not `root@homeassistant.local`)
- [ ] Target directory correct (`/homeassistant/` not `/config/`)
- [ ] File permissions will be preserved

#### Git Checks (for git pull deployments)
- [ ] Local commits pushed to remote
- [ ] Server state inspected: `ssh ha "cd /homeassistant && git status"`
- [ ] No uncommitted server changes OR inspected and categorized
- [ ] Current server commit known: `git log --oneline -5`

#### Service Call Checks (for automation/script changes)
- [ ] Service schemas verified in Developer Tools first
- [ ] All required parameters present
- [ ] No deprecated parameters used (check HA version release notes)
- [ ] Target entities exist and are correct entity IDs

#### Reload vs Restart
- [ ] Correct reload service chosen (automation.reload vs script.reload vs pyscript.reload)
- [ ] Full restart NOT used for simple config changes
- [ ] Restart only for: new integrations, configuration.yaml changes, breaking changes

#### Post-Deployment Validation
- [ ] Logs checked: `ssh ha "ha core log | grep -i error | tail -20"`
- [ ] Automation/script manually triggered to verify
- [ ] No unexpected errors in logs

## Workflow Decision Tree

```
Configuration Change Needed
├─ Is this final/tested?
│  ├─ YES → Use git workflow
│  └─ NO → Use scp workflow
├─ Check configuration valid
├─ Deploy (git pull or scp)
├─ Needs restart?
│  ├─ YES → ha core restart
│  └─ NO → Use appropriate reload
├─ Verify in logs
└─ Test outcome

Dashboard Change Needed
├─ Make changes locally
├─ Deploy via scp for testing
├─ Refresh browser (Ctrl+F5)
├─ Test on target device
├─ Iterate until perfect
└─ Commit to git when stable
```

## Entity Registry Management

### 🚨 CRITICAL SAFETY RULE - ALWAYS BACKUP REGISTRY FIRST

**BEFORE making ANY modification to the entity registry, you MUST create a backup.**

The entity registry (`.storage/core.entity_registry`) is a critical Home Assistant database file. If corrupted, **ALL entity metadata is lost** (labels, icons, areas, customizations, disabled states, etc.).

**Mandatory backup procedure:**
```bash
# 1. ALWAYS backup BEFORE any registry operation
ssh ha "cp /config/.storage/core.entity_registry /config/.storage/core.entity_registry.backup_$(date +%Y%m%d_%H%M%S)"

# 2. Verify backup was created successfully
ssh ha "ls -lh /config/.storage/core.entity_registry.backup*" | tail -1

# 3. Only THEN proceed with registry modifications
```

**When this applies:**
- Enabling/disabling entities via API or registry editing
- Fixing duplicate `_2` entities
- Modifying unique_ids or entity_ids
- Running any script that touches the registry
- Manual JSON editing of the registry file
- Using REST API endpoints that modify entity registry

**Recovery if corrupted:**
```bash
# Restore from backup
ssh ha "cp /config/.storage/core.entity_registry.backup_YYYYMMDD_HHMMSS /config/.storage/core.entity_registry"
# Then restart HA
```

**Home Assistant maintains automatic backups:**
- `.storage/core.entity_registry.bak` - Most recent automatic backup
- Check with: `ssh ha "ls -lht /config/.storage/*.entity_registry*"`

**NEVER skip the backup step.** Registry corruption requires manual restoration and can cause significant downtime.

---

### Enabling/Disabling Entities Safely

**🚨 CRITICAL: The ONLY safe method to enable/disable entities is via the Web UI while HA is running.**

#### ✅ CORRECT Method: Web UI (Recommended)

```
1. Open: http://homeassistant.local:8123
2. Navigate: Settings → Devices & Services → Entities
3. Search for the entity (e.g., "telefono_chiara_is_charging")
4. Click on the disabled/enabled entity
5. Click "Enable" or "Disable" button
6. Wait a few seconds - no restart needed
```

**Why this is safe:**
- HA handles all registry updates in-memory
- No file corruption risk
- Changes take effect immediately
- No restart required
- HA validates the operation

#### ❌ DANGEROUS Methods That WILL Fail or Corrupt

**1. REST API Entity Registry Endpoints (DO NOT USE)**

These endpoints **DO NOT EXIST** or **DO NOT WORK** as expected:
```bash
# ❌ WRONG - These will return 404 or fail
curl -X POST "http://homeassistant.local:8123/api/config/entity_registry/ENTITY_ID"
curl -X POST "http://homeassistant.local:8123/api/config/entity_registry/update/ENTITY_ID"
```

**Reality:** Home Assistant's REST API does NOT support direct entity enable/disable operations. The entity registry is managed through WebSocket API (undocumented) or the UI only.

**2. Direct File Editing While HA is Running (EXTREMELY DANGEROUS)**

```bash
# ❌ WRONG - This WILL corrupt the registry
ssh ha "cat /config/.storage/core.entity_registry | jq '...' > /tmp/new.json"
scp /tmp/new.json ha:/config/.storage/core.entity_registry

# ❌ WRONG - SCP can create 0-byte files
scp local_registry.json ha:/config/.storage/core.entity_registry
```

**Why this fails:**
- HA keeps the registry **in memory** while running
- Any file changes are **overwritten on HA shutdown**
- SCP errors or pipe failures create **0-byte files** → complete corruption
- jq piping can fail silently and output nothing
- No atomic write protection

**3. Python Scripts on Running HA (WILL FAIL)**

```bash
# ❌ WRONG - Changes lost when HA shuts down
ssh ha "python3 /tmp/enable_entity.py"
```

**Why this fails:**
- HA loads registry into memory at startup
- File modifications don't affect running HA
- HA overwrites file from memory on shutdown
- Your changes are silently lost

#### ⚠️ Advanced Method: Registry Editing (ONLY When HA is Stopped)

**Use ONLY for:**
- Fixing corrupt registries
- Bulk operations on stopped systems
- Recovery scenarios

**Requirements:**
1. HA **MUST be completely stopped** (not just restarting)
2. Backup MUST be verified before editing
3. Use proper Python JSON handling (NOT jq/sed)
4. Verify file size after writing
5. Reboot to restart HA

**Correct procedure:**
```bash
# 1. BACKUP FIRST (verify size)
ssh ha "cp /config/.storage/core.entity_registry /config/.storage/core.entity_registry.backup_$(date +%Y%m%d_%H%M%S)"
ssh ha "ls -lh /config/.storage/core.entity_registry.backup*" | tail -1
# VERIFY: File size should be ~4MB, NOT 0 bytes

# 2. STOP HA COMPLETELY
source .env && hass-cli service call homeassistant.stop
sleep 30

# 3. Verify HA is stopped
# Check that API is unreachable or use system check

# 4. Download registry to local machine
scp ha:/config/.storage/core.entity_registry /tmp/registry_local.json

# VERIFY: Check file size locally
ls -lh /tmp/registry_local.json
# MUST be ~4MB, NOT 0 bytes - if 0, SCP failed, restore backup immediately

# 5. Edit locally with Python (NEVER jq/sed)
python3 /tmp/edit_registry.py  # Proper JSON handling

# 6. VERIFY edited file before uploading
ls -lh /tmp/registry_edited.json
# MUST be reasonable size, NOT 0 bytes

# 7. Upload edited file
scp /tmp/registry_edited.json ha:/config/.storage/core.entity_registry

# 8. VERIFY uploaded file
ssh ha "ls -lh /config/.storage/core.entity_registry"
# If 0 bytes: RESTORE BACKUP IMMEDIATELY
# ssh ha "cp /config/.storage/core.entity_registry.backup_YYYYMMDD_HHMMSS /config/.storage/core.entity_registry"

# 9. Reboot system (can't start HA via SSH add-on)
ssh ha "sudo reboot"
```

#### Common Mistakes and Their Consequences

| Mistake | Consequence | Recovery |
|---------|-------------|----------|
| Edit registry while HA running | Changes silently lost on shutdown | Re-edit with HA stopped |
| SCP without size verification | 0-byte file = total corruption | Restore from backup immediately |
| Use jq/sed piping | Empty output = total corruption | Restore from backup immediately |
| No backup before editing | Unrecoverable data loss | None - all metadata lost |
| REST API enable/disable | 404 error or no effect | Use Web UI instead |
| Restart instead of stop | Registry rewritten from memory | Changes lost, must stop HA |

#### Verification Checklist

Before proceeding with ANY registry operation:

```bash
# ✅ 1. Backup exists and is valid
ssh ha "ls -lh /config/.storage/core.entity_registry.backup_*" | tail -1
# Must show file size ~4MB

# ✅ 2. HA is actually stopped (for advanced editing only)
curl -f http://homeassistant.local:8123/api/ || echo "HA is stopped"

# ✅ 3. After any file operation, verify size
ssh ha "ls -lh /config/.storage/core.entity_registry"
# Must be ~4MB, NOT 0 bytes

# ✅ 4. If 0 bytes detected, restore IMMEDIATELY
ssh ha "cp /config/.storage/core.entity_registry.bak /config/.storage/core.entity_registry"
```

#### Summary: Decision Tree

```
Need to enable/disable an entity?
├─ HA is running? → YES → Use Web UI (ONLY safe method)
├─ HA is running? → NO  → Can you start HA?
   ├─ YES → Start HA, use Web UI
   └─ NO  → Advanced registry editing (follow full procedure above)

Need to bulk edit entities?
├─ < 10 entities → Use Web UI (tedious but safest)
└─ > 10 entities → Stop HA, edit registry with Python, verify at each step
```

**Default recommendation: ALWAYS use the Web UI unless absolutely impossible.**

---

### Understanding Automation IDs vs Entity IDs

**Critical distinction:**
- **YAML `id` field** → becomes `unique_id` in entity registry (internal identifier)
- **YAML `alias` field** → becomes `entity_id` (e.g., `automation.kitchen_thermostat_schedule`)

**WARNING: Changing automation IDs causes problems!**
When you change an automation's `id` field:
1. HA sees it as a completely NEW automation
2. Creates a new entity registry entry
3. Since the `alias` generates the same `entity_id`, HA adds `_2` suffix
4. Old metadata (area, icon, labels) is orphaned on the old entry

### Labels, Icons, and Areas are UI-Only

**These CANNOT be set via YAML:**
- Labels
- Icons (for automations)
- Area assignments

**They are stored in:** `.storage/core.entity_registry`

**To set them:**
1. Via HA UI: Settings → Automations → Select → 3-dot menu → Edit metadata
2. Via WebSocket API (undocumented): `config/entity_registry/update`

**The MCP server does NOT support setting labels/icons** - it only provides device control.

### Fixing Duplicate `_2` Automation Entries

If you changed automation IDs and have duplicates:

**The Fix Process:**
```bash
# 1. Stop HA (NOT restart - must stop completely)
curl -X POST "http://homeassistant.local:8123/api/services/homeassistant/stop" \
  -H "Authorization: Bearer $HASS_TOKEN"

# 2. Wait for HA to stop
sleep 15

# 3. Run fix script (updates unique_ids, removes duplicates)
# See /tmp/ha_fix_registry_final.py or create similar

# 4. Reboot system (since we can't start HA via SSH add-on)
ssh ha "sudo reboot"
```

**Fix Script Logic:**
```python
# For each _2 entry:
#   1. Find matching non-_2 entry (has metadata)
#   2. Update non-_2 entry's unique_id to match new YAML id
#   3. Delete the _2 entry
# Result: Clean entity_ids with preserved metadata
```

**Key insight:** Registry changes must be made while HA is STOPPED. HA overwrites registry from memory on shutdown.

### Entity Registry Structure

```json
{
  "entity_id": "automation.kitchen_thermostat_schedule",
  "unique_id": "climate_kitchen_thermostat_schedule",  // <-- matches YAML id
  "area_id": "kitchen",
  "icon": "mdi:home-thermometer-outline",
  "labels": ["thermostat"],
  "platform": "automation"
}
```

### Best Practices for Automation IDs

1. **Pick descriptive IDs from the start** - avoid changing them later
2. **Use consistent naming convention:** `domain_room_action` (e.g., `climate_kitchen_thermostat_schedule`)
3. **If you must change IDs:** Be prepared to run the registry fix process
4. **Document your ID scheme** to maintain consistency

## Automation Metadata Tools

Scripts in `scripts/` directory for managing automation labels, icons, and areas programmatically.

### Prerequisites

```bash
pip install websockets pyyaml
```

### Tool 1: Registry Backup (`ha_backup_registry.py`)

Create timestamped backups of the entity registry before making changes.

```bash
# Create backup
python3 scripts/ha_backup_registry.py backup

# List existing backups
python3 scripts/ha_backup_registry.py list

# Restore from backup (requires HA stopped)
python3 scripts/ha_backup_registry.py restore 20260107_120000

# Clean old backups (keep last 5)
python3 scripts/ha_backup_registry.py clean --keep 5
```

Backups stored in: `scripts/backups/entity_registry.<timestamp>.json`

### Tool 2: Entity Metadata (`ha_entity_metadata.py`)

Bulk assign labels, icons, and areas via WebSocket API.

```bash
# ALWAYS START WITH STATS - shows what's missing
python3 scripts/ha_entity_metadata.py stats

# Export ALL automations (including those without metadata)
python3 scripts/ha_entity_metadata.py export --all > all_automations.yaml

# Export only automations that already have metadata
python3 scripts/ha_entity_metadata.py export > metadata.yaml

# Apply metadata from config file
python3 scripts/ha_entity_metadata.py apply metadata.yaml

# Preview changes without applying
python3 scripts/ha_entity_metadata.py apply metadata.yaml --dry-run

# Set single automation
python3 scripts/ha_entity_metadata.py set automation.kitchen_thermostat \
    --icon mdi:thermometer --area kitchen --labels thermostat,climate

# Label management
python3 scripts/ha_entity_metadata.py labels list
python3 scripts/ha_entity_metadata.py labels create climate --icon mdi:thermometer --color blue
python3 scripts/ha_entity_metadata.py labels delete climate
python3 scripts/ha_entity_metadata.py labels suggest climate --pattern "automation.*thermostat*"
```

**IMPORTANT:** Always run `stats` first to see total automation count and coverage!

**Config file format (`automation_metadata.yaml`):**
```yaml
automations:
  automation.kitchen_thermostat_schedule:
    icon: mdi:home-thermometer-outline
    area_id: kitchen
    labels:
      - climate
      - scheduled
```

**Important:** Labels must exist before assignment. Create them first or use the Claude-assisted workflow.

### Tool 3: ID Migration (`ha_migrate_automation_ids.py`)

Safely migrate automation IDs while preserving metadata.

```bash
# Generate migration plan from current state
python3 scripts/ha_migrate_automation_ids.py generate > migration.yaml

# Preview what will change
python3 scripts/ha_migrate_automation_ids.py preview migration.yaml

# Execute full migration (stops HA, updates registry, reboots)
python3 scripts/ha_migrate_automation_ids.py execute migration.yaml

# Fix registry after YAML already updated (removes _2 duplicates)
python3 scripts/ha_migrate_automation_ids.py fix-registry
```

**Migration workflow:**
1. Update YAML `id` fields with new descriptive IDs
2. Generate or edit migration.yaml
3. Run `execute` - tool handles stop/migrate/reboot

### Tool 4: Entity Exposure (`ha_expose_entities.py`)

Manage which entities are exposed to the conversation agent (AI assistant).

```bash
# Expose entities to conversation agent
python3 scripts/ha_expose_entities.py expose sensor.flex_d_status sensor.nas_status

# Unexpose entities
python3 scripts/ha_expose_entities.py unexpose sensor.old_sensor

# List all currently exposed entities
python3 scripts/ha_expose_entities.py list

# Check if specific entities are exposed
python3 scripts/ha_expose_entities.py check sensor.flex_d_status
```

**Use cases:**
- Expose new summary sensors to AI assistant
- Bulk expose/unexpose entities
- Audit what the AI can see

### Label Management Workflow (Claude-Assisted)

Labels require thoughtful planning. Use this workflow:

1. **Check current coverage (CRITICAL FIRST STEP):**
   ```bash
   python3 scripts/ha_entity_metadata.py stats
   ```

2. **List existing labels:**
   ```bash
   python3 scripts/ha_entity_metadata.py labels list
   ```

3. **Export ALL automations for analysis:**
   ```bash
   python3 scripts/ha_entity_metadata.py export --all > all_automations.yaml
   ```

4. **Plan label taxonomy** (Claude can help analyze automations and suggest labels)

5. **Create labels:**
   ```bash
   python3 scripts/ha_entity_metadata.py labels create climate --icon mdi:thermometer
   python3 scripts/ha_entity_metadata.py labels create scheduled --icon mdi:clock
   ```

6. **Apply labels to automations:**
   ```bash
   python3 scripts/ha_entity_metadata.py apply metadata.yaml
   ```

7. **Verify coverage:**
   ```bash
   python3 scripts/ha_entity_metadata.py stats
   ```

**Suggested label taxonomy:**

| Label         | Icon                | Purpose                     |
|---------------|---------------------|-----------------------------|
| climate       | mdi:thermometer     | Heating/cooling automations |
| lighting      | mdi:lightbulb       | Light control automations   |
| vacuum        | mdi:robot-vacuum    | Robot vacuum automations    |
| media         | mdi:television      | Media player automations    |
| notifications | mdi:bell            | Alert automations           |
| scheduled     | mdi:clock           | Time-triggered automations  |
| presence      | mdi:account         | Occupancy-based automations |
| safety        | mdi:shield          | Critical/safety automations |

### Common Mistakes to Avoid

1. **Not running `stats` first** - The `export` command without `--all` only shows automations that ALREADY have metadata. Always run `stats` to see the true count.

2. **Assuming export shows everything** - Use `export --all` to see ALL automations including those without any metadata assigned.

3. **Not verifying after bulk updates** - Always run `stats` after applying changes to confirm coverage.

4. **Forgetting labels must exist first** - Labels must be created before they can be assigned to automations.

5. **Changes are immediate via WebSocket** - No git push or HA restart needed. Changes apply instantly to HA's entity registry. Just refresh browser to see them.

## AI Assistant Integration

### Understanding HA Conversation Agent Limitations

**Critical insight:** The HA Conversation agent (OpenAI integration) only exposes entity **state** to the AI, NOT attributes. This means:
- ✅ AI sees: `sensor.nas_status` state = "Storage 93% full"
- ❌ AI cannot see: attributes like `cpu_percent`, `memory_percent`, `summary`

**Implication:** Rich attribute data is invisible to voice/chat assistants. Design sensors accordingly.

### AI-Optimized Sensor Pattern

Pack all key metrics into the **state** string (max 255 chars) instead of attributes:

```yaml
# BAD: Metrics in attributes (AI can't see these)
- name: "Device Status"
  state: "Healthy"
  attributes:
    cpu: "{{ states('sensor.cpu') }}"
    memory: "{{ states('sensor.memory') }}"

# GOOD: All metrics in state (AI can parse this)
- name: "Device Status"
  state: >-
    Device — Status: {{ status }}{% if issues %} ({{ issues | join(', ') }}){% endif %} ·
    CPU {{ cpu }}% · Mem {{ mem }}% · Temp {{ temp }}°C
```

**Format guidelines:**
- Start with device name and explicit status verdict: `Healthy`, `Warning`, `Critical`
- Include reason in parentheses: `Warning (Storage high)`
- Use `·` or `|` as separators (speakable)
- Label metrics clearly: "Storage 93% **used**" not just "93%"
- Keep under 200 chars for readability

**Example - NAS Status Sensor:**
```
Soundwave NAS — Status: Warning (Storage high) · Storage 93% used · CPU 5% · Mem 30% · System 40°C · Drives OK (37–38°C) · Security OK
```

### Exposing Entities to Conversation Agent

**Two different systems - don't confuse them:**

| File | Purpose |
|------|---------|
| `.storage/homeassistant.exposed_entities` | Alexa/Google Home exposure |
| `.storage/core.entity_registry` → `options.conversation.should_expose` | **Conversation agent (OpenAI)** |

**To expose an entity to the AI assistant via WebSocket:**

```python
import asyncio
import json
import websockets

async def expose_entity(entity_id):
    uri = f"ws://{HASS_HOST}:8123/api/websocket"
    async with websockets.connect(uri) as ws:
        # Auth
        await ws.recv()  # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": HASS_TOKEN}))
        await ws.recv()  # auth_ok

        # Expose to conversation agent
        await ws.send(json.dumps({
            "id": 1,
            "type": "homeassistant/expose_entity",
            "assistants": ["conversation"],
            "entity_ids": [entity_id],
            "should_expose": True
        }))
        result = await ws.recv()
        return json.loads(result).get('success')

asyncio.run(expose_entity("sensor.nas_status"))
```

**Note:** Changes take effect immediately - no restart needed.

### Testing Conversation Agent

Test AI assistant responses via curl:

```bash
# Ask the assistant a question
curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  "$HASS_SERVER/api/conversation/process" \
  -d '{"agent_id":"conversation.your_agent", "text":"How is the NAS doing?"}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['response']['speech']['plain']['speech'])"
```

**Find your agent_id:**
```bash
hass-cli state list | grep conversation
# Example: conversation.anna
```

### Synology DSM Status Reference

When creating sensors for Synology NAS, handle all possible states:

**Volume Status:**
| Status | Severity | Meaning |
|--------|----------|---------|
| `normal` | OK | Volume healthy |
| `attention` | Warning | Needs attention (e.g., >90% full) |
| `degraded` | Critical | RAID degraded (drive failed, array functional) |
| `crashed` | Critical | RAID failed (data at risk) |
| `repairing` | Info | RAID rebuilding |

**Drive Status:**
| Status | Severity | Meaning |
|--------|----------|---------|
| `normal` / `healthy` | OK | Drive healthy |
| `warning` | Warning | Issues detected, bad sectors |
| `critical` | High | Critical issues |
| `failing` | Critical | Severe issues, integrity not guaranteed |
| `crashed` | Critical | Drive removed from pool |

**Security Status (binary_sensor):**
- `off` = Security OK
- `on` = Security Alert

## Android TTS Notifications

### Correct Service Call Format

When sending TTS notifications to Android phones via the Companion App, **all these fields are required**:

```yaml
action: notify.mobile_app_telefono_paolo
data:
  message: TTS
  data:
    ttl: 0
    priority: high
    media_stream: alarm_stream_max
    tts_text: "Your message here"
```

**Critical fields:**
- `ttl: 0` - Prevents notification delay/suppression in doze mode
- `priority: high` - Ensures immediate delivery
- `media_stream: alarm_stream_max` - Plays at maximum volume on alarm stream
- `tts_text` - The actual text to speak (NOT `message` or `title`)

**Common mistakes:**
- ❌ Missing `ttl: 0` and `priority: high` → notification may be delayed or silent
- ❌ Using `message:` for the spoken text → must use `tts_text:` inside nested `data:`
- ❌ Wrong indentation → YAML parsing errors

### Pronunciation Workarounds

Android TTS does **NOT** support SSML tags. For proper name pronunciation issues:

| Problem | Solution | Example |
|---------|----------|---------|
| Name spelled letter-by-letter | Add/double vowels | "Ada" → "Aada" |
| Acronym-like words | Use lowercase or accents | "ADA" → "Àda" |
| Foreign words mispronounced | Phonetic spelling | Use intuitive spellings |

**Note:** The TTS engine is controlled by Android device settings (Settings → Accessibility → Text-to-speech), not by Home Assistant.

## 🔍 Troubleshooting Integration Errors

### 🚨 CRITICAL RULE: Documentation First, Assumptions Never

**Before making ANY suggestions about Home Assistant integrations or services, you MUST:**

1. **Check official documentation** via WebFetch: `https://www.home-assistant.io/integrations/[integration_name]/`
2. **Search for recent changes** via Tavily: "Home Assistant [integration] 2025 2026 changes breaking"
3. **Verify service parameters** against current API documentation
4. **Check GitHub issues** for known limitations and ongoing work

**NEVER:**
- Suggest solutions based on assumptions or outdated knowledge
- Propose service calls without verifying parameter schemas
- Ignore that integrations configured via UI may have different behavior than YAML
- Assume chat IDs, entity names, or service formats are correct without verification

### Telegram Integration (2025.11+ Breaking Changes)

**Critical Changes in Home Assistant 2025.11:**

1. **Configuration Moved to UI**
   - `telegram_bot:` YAML config is deprecated and ignored
   - All configuration now via: Settings → Devices & Services → Telegram
   - Chat IDs must be added through UI integration config

2. **Two Coexisting Approaches**

   **✅ telegram_bot.send_message (RECOMMENDED for advanced features)**
   ```yaml
   action: telegram_bot.send_message
   data:
     message: "Your message"
     target: [123456789]  # or [-4996384291] for groups
     parse_mode: html  # or markdown, markdownv2
     disable_notification: false
     inline_keyboard:  # Advanced feature
       - "Button:/command"
   ```

   **Features:**
   - ✅ Inline keyboards and buttons
   - ✅ Photos, videos, documents (`telegram_bot.send_photo`, etc.)
   - ✅ Full formatting (HTML, Markdown)
   - ✅ Group chat support
   - ✅ All Telegram Bot API features

   **❌ notify.send_message (LIMITED, still evolving)**
   ```yaml
   action: notify.send_message
   target:
     entity_id: notify.telegram_bot_123456789_987654321
   data:
     message: "Your message"
   ```

   **Current Limitations (as of 2025.11-2026.01):**
   - ❌ No photos/videos (in development, expected Jan 2026)
   - ❌ No inline keyboards
   - ❌ Limited group support (in development)
   - ❌ No advanced formatting options

3. **Common Chat ID Issues**

   **Valid Chat ID Format:**
   - Individual users: Positive numbers (e.g., `363645715`)
   - Groups/channels: Negative numbers (e.g., `-4996384291`)
   - Must be allowlisted in integration configuration

   **Symptoms of Wrong Chat ID:**
   ```
   ERROR: Invalid chat IDs
   ERROR: Unauthorized
   ERROR: Chat not found
   ```

   **How to Get Correct Chat IDs:**
   ```
   1. Use @getmyid_bot in Telegram
   2. For users: Start bot, get your ID
   3. For groups: Forward any group message to bot
   4. For channels: Forward any channel message to bot
   5. Verify in HA: Settings → Devices & Services → Telegram → Configure
   ```

   **⚠️ Chat IDs Can Change:**
   - Groups recreated → new ID
   - Channel settings changed → new ID
   - **Always verify** chat IDs in integration config match what's used in automations

4. **Debugging Telegram Errors**

   **Error: "Invalid chat IDs"**
   ```bash
   # 1. Check integration configuration
   # Settings → Devices & Services → Telegram → Configure → Allowed chat IDs

   # 2. Find chat IDs used in automations
   grep -r "telegram_bot.send_message" automations/ -A5 | grep "target:"

   # 3. Verify they match configuration
   # If mismatch, update automations with correct IDs
   ```

   **Error: "Extra keys not allowed @ data['X']"**
   - Service parameter schema changed
   - Check current documentation: https://www.home-assistant.io/integrations/telegram_bot/
   - Use WebFetch to get latest parameter list

### General Integration Troubleshooting Workflow

```
Integration Error Occurs
├─ 1. DON'T assume - Research first
│  ├─ WebFetch: https://www.home-assistant.io/integrations/[name]/
│  ├─ Tavily: "Home Assistant [name] 2025 2026"
│  └─ Check GitHub: Known issues and PRs
│
├─ 2. Identify Configuration Method
│  ├─ UI-configured? → Settings → Devices & Services
│  ├─ YAML-configured? → Check configuration.yaml
│  └─ Mixed? → UI config takes precedence
│
├─ 3. Verify Service Parameters
│  ├─ Check official docs for current schema
│  ├─ Test in Developer Tools → Actions
│  └─ Check logs for specific parameter errors
│
├─ 4. Check for Breaking Changes
│  ├─ Release notes for HA version
│  ├─ Integration-specific migration guides
│  └─ Community forums for migration patterns
│
└─ 5. Validate Fix Before Applying
   ├─ Test in Developer Tools first
   ├─ Check logs after test
   └─ Only then update automations
```

### Service Parameter Verification

**Before suggesting ANY service call, verify parameters:**

```bash
# Option 1: Developer Tools → Actions (UI)
# - Select service
# - UI shows available parameters with descriptions
# - Test before coding

# Option 2: WebFetch official documentation
# https://www.home-assistant.io/integrations/[integration]/#services
```

**Common Parameter Errors:**

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "extra keys not allowed @ data['X']" | Parameter no longer exists | Remove parameter, check docs |
| "required key not provided @ data['X']" | Missing required parameter | Add parameter from docs |
| "invalid data for call_service" | Wrong parameter type | Check type (string/int/list) |
| "Entity not found" | Entity ID changed or disabled | Verify in States list |

### UI-Configured Integration Gotchas

**Telegram, Alexa, Google, Notify integrations:**
1. Configuration in UI, not YAML
2. Entity IDs auto-generated from config
3. Service schemas may differ from YAML era
4. Check integration page in UI for current entities

**Migration Pattern (2024-2025):**
```
Old (YAML):
notify:
  - platform: telegram
    chat_id: 123456789

New (UI + automation):
# 1. Add via UI: Settings → Add Integration → Telegram
# 2. Use in automations:
action: telegram_bot.send_message
data:
  target: [123456789]
```

## 🐛 Common Mistake Patterns & Prevention

### Mistake 1: Git Pull Without Inspection
**Symptom**: "Your local changes would be overwritten by merge"

**What NOT to do:**
```bash
# ❌ WRONG: Immediate checkout without inspection
ssh ha "cd /homeassistant && git checkout ."
```

**Correct procedure:**
```bash
# ✅ RIGHT: Inspect → Categorize → Decide
ssh ha "cd /homeassistant && git diff <file>"
# Analyze: Are these MY changes from this session?
# Only then: checkout if safe
```

**Prevention**: Always run `git status` before attempting `git pull`

---

### Mistake 2: SCP Then Git Pull Conflicts
**Symptom**: Git pull fails due to local modifications from earlier scp deployments

**What happened:**
1. Deployed via scp for testing
2. Later committed and pushed changes
3. Git pull on server conflicts with scp-modified files

**Prevention**:
- Document which files were deployed via scp
- Checkout scp files BEFORE git pull
- OR use scp-only for /tmp, git-only for /homeassistant

---

### Mistake 3: Using Wrong Paths
**Symptom**: File operations fail or files created in wrong location

**Common errors:**
- Claudedocs in `/home/pantinor/.claude/` instead of project `.claude/`
- SSH to `root@homeassistant.local` instead of `ha:` alias
- Target `/config/` instead of `/homeassistant/`

**Prevention**: Use path reference table (see "Path Management" section)

---

### Mistake 4: Service Call Parameters Not Verified
**Symptom**: Service call fails with "Extra keys not allowed" or "Required key missing"

**What happened:**
- Used service parameters based on old documentation
- HA version changed service schema
- Parameters removed or added

**Prevention**:
- ALWAYS verify in Developer Tools → Services before deploying
- Check release notes for service schema changes
- Test service call manually before adding to automation

---

### Mistake 5: Reload Instead of Restart (or vice versa)
**Symptom**: Changes not applied despite "successful" reload

**Common errors:**
- Using `automation.reload` for integration config changes (needs restart)
- Using full restart for simple automation edits (reload sufficient)

**Prevention**: Use reload decision tree (see "Reload vs Restart" section)

---

This skill encapsulates efficient Home Assistant management workflows developed through iterative optimization and real-world dashboard development. Apply these patterns to any Home Assistant instance for reliable, fast, and safe configuration management.
