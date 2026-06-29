# 07. Remote Access & Tools

**Home Assistant Manager - Remote CLI Access**

---

## 📌 Channel Selection (read this first)

Prefer channels in this order. The rest of this document is the **hass-cli reference**
(useful as the SSH-side fallback and for raw API access).

1. **ha MCP tools (primary):** `ha_get_state`, `ha_call_service`, `ha_eval_template`,
   `ha_search`, `ha_config_get_*`, `ha_get_logs`, `ha_get_history`. Always-connected;
   they work even when your dev host cannot reach HA's LAN.
2. **hass-cli over SSH (fallback):** `ssh -oVisualHostKey=no ha "hass-cli …"` for what
   MCP can't do (`ha core check`, server-side git, docker).
3. **hass-cli from the dev host (tertiary):** only works when this machine resolves
   `homeassistant.local`. If `hass-cli` errors with "Error connecting to …", do NOT
   switch to curl — use channel 1 or 2.
4. **curl:** forbidden (auth/header maintenance burden).

> **Note:** `hass-cli` run from a dev host that is *not* on the home LAN usually cannot
> resolve `homeassistant.local` (mDNS). That is an environment limitation, not a hass-cli
> bug — route through the ha MCP server or SSH instead.

## 🚨 CRITICAL: Use hass-cli, NOT curl

**hass-cli is MANDATORY for all Home Assistant API interactions.**

**NEVER use curl unless:**
1. hass-cli is genuinely broken OR
2. You need an API endpoint that hass-cli cannot access

**🚨 CRITICAL: When a command fails, ALWAYS use --help FIRST:**
```bash
hass-cli [subcommand] --help
```

**NEVER immediately switch to curl when a command fails.** Use --help to:
- Verify the correct syntax
- Check if the option/feature exists
- Find the correct alternative approach

### Why This Rule?

| Aspect | hass-cli | curl |
|--------|----------|------|
| Authentication | ✅ Automatic (HASS_TOKEN) | ❌ Manual headers |
| Environment | ✅ Uses HASS_SERVER | ❌ Manual URLs |
| Output formatting | ✅ Structured (table/yaml/json) | ❌ Raw JSON |
| Error handling | ✅ Clear messages | ❌ HTTP codes only |
| Command complexity | ✅ Simple | ❌ Long, error-prone |
| Maintainability | ✅ Self-documenting | ❌ Hard to read |

---

## Decision Table: When to Use What

| Scenario | Tool | Example |
|----------|------|---------|
| Get entity state | ✅ **hass-cli** | `hass-cli state get sensor.example` |
| List entities | ✅ **hass-cli** | `hass-cli state list` |
| Call service | ✅ **hass-cli** | `hass-cli service call automation.reload` |
| Reload core config | ✅ **hass-cli** | `hass-cli service call homeassistant.reload_core_config` |
| Get raw JSON | ✅ **hass-cli -o json** | `hass-cli -o json state get sensor.example` |
| Call custom API | ⚠️ **hass-cli raw** | `hass-cli raw post /api/custom` |
| Test template | ✅ **hass-cli raw** | `hass-cli raw post /api/template --json '{"template": "..."}'` |
| **hass-cli genuinely broken** | ⚠️ **curl ONLY** | Last resort after troubleshooting |

---

## curl → hass-cli Translation Guide

**Memorize these patterns. Never use the curl equivalents.**

### State Operations

| Task | ❌ WRONG (curl) | ✅ CORRECT (hass-cli) |
|------|----------------|---------------------|
| Get state | `curl -H "Authorization: Bearer $TOKEN" $SERVER/api/states/sensor.example` | `hass-cli state get sensor.example` |
| Get with attributes | `curl ... \| jq '.attributes'` | `hass-cli -o yaml state get sensor.example` |
| List all states | `curl ... /api/states` | `hass-cli state list` |
| Filter states | `curl ... \| jq '.[] \| select(...)'` | `hass-cli state list \| grep pattern` |

### Service Calls

| Task | ❌ WRONG (curl) | ✅ CORRECT (hass-cli) |
|------|----------------|---------------------|
| Reload automations | `curl -X POST -H "Authorization: Bearer $TOKEN" $SERVER/api/services/automation/reload` | `hass-cli service call automation.reload` |
| Reload core config | `curl -X POST -H "Authorization: Bearer $TOKEN" $SERVER/api/services/homeassistant/reload_core_config` | `hass-cli service call homeassistant.reload_core_config` |
| Trigger automation | `curl -X POST -d '{"entity_id": "automation.name"}' ...` | `hass-cli service call automation.trigger --arguments entity_id=automation.name` |
| Call script | `curl -X POST ... /api/services/script/turn_on` | `hass-cli service call script.turn_on` |

### Template Evaluation

| Task | ❌ WRONG (curl) | ✅ CORRECT (hass-cli) |
|------|----------------|---------------------|
| Test template | `curl -d '{"template": "{{ now() }}"}' -H "Authorization: Bearer $TOKEN" $SERVER/api/template` | `hass-cli raw post /api/template --json '{"template": "{{ now() }}"}'` |

### Raw JSON Output

| Task | ❌ WRONG (curl) | ✅ CORRECT (hass-cli) |
|------|----------------|---------------------|
| Get JSON for parsing | `curl -H "Authorization: Bearer $TOKEN" $SERVER/api/states/sensor.example` | `hass-cli -o json state get sensor.example` |
| Pipe to jq | `curl ... \| jq '.state'` | `hass-cli -o json state get sensor.example \| jq '.state'` |

---

## Troubleshooting Before Using curl

**If hass-cli "doesn't work", FIX IT. Do NOT switch to curl.**

## 🚨 MANDATORY: Use --help BEFORE Trying Alternatives

**When a command fails, you MUST follow this sequence:**

```bash
# Step 1: ALWAYS check help first
hass-cli [subcommand] --help

# Step 2: Verify the exact syntax from help
# Step 3: Try the corrected command
# Step 4: ONLY if help confirms feature doesn't exist, consider alternatives
```

**Examples:**

```bash
# ❌ WRONG: Immediately try curl when command fails
hass-cli state get --attributes
# Error: No such option
# → Immediately tries curl instead (WRONG!)

# ✅ CORRECT: Check help, learn correct syntax
hass-cli state get --help
# Output shows: Usage: hass-cli state get [OPTIONS] ENTITY
# → No --attributes option exists
# → Try: hass-cli -o yaml state get sensor.example (includes attributes)
```

### Decision Flow: When to Use --help

```
Command fails?
├─ Yes → Run: hass-cli [subcommand] --help
│         ├─ Syntax error? → Fix syntax based on help output
│         ├─ Missing option? → Check if option exists, find correct alternative
│         └─ Feature doesn't exist? → Then consider hass-cli raw or curl
└─ No → Success!
```

### Step 1: Verify Environment

```bash
# Check if .env is sourced
echo $HASS_TOKEN | head -c 20

# If empty, source it
source /home/pantinor/data/repo/personal/hassio/.env
```

### Step 2: Check Help for Correct Syntax

```bash
# ALWAYS verify syntax with --help before trying alternatives
hass-cli state --help       # Check state subcommand options
hass-cli service --help     # Check service subcommand options
hass-cli --help             # Check global options
```

### Step 3: Test Basic Connectivity

```bash
# Simple state query
hass-cli state get sensor.example

# If this fails, the issue is NOT with hass-cli
# Check: network, HA server status, credentials
```

### Step 4: Check Output Format Issues

```bash
# Want JSON? Use -o flag (GLOBAL option, comes FIRST)
hass-cli -o json state get sensor.example

# Want YAML with attributes? Use -o yaml
hass-cli -o yaml state get sensor.example

# Want raw output? Use raw subcommand
hass-cli raw get /api/states/sensor.example
```

### Step 5: Last Resort - Only Then Consider curl

**Valid reasons to use curl:**
- hass-cli has a confirmed bug blocking your use case
- You need an API endpoint not exposed by hass-cli (very rare)
- You're accessing a non-Home Assistant API

**Invalid reasons (FIX THESE instead):**
- "curl command is shorter" → NO, hass-cli is simpler
- "I know curl better" → Learn hass-cli, it's worth it
- "Need JSON output" → Use `hass-cli -o json`
- "Need raw API access" → Use `hass-cli raw`

---

## hass-cli Capabilities Reference

### State Queries

```bash
# Basic state
hass-cli state get sensor.entity_name

# With attributes (YAML)
hass-cli -o yaml state get sensor.entity_name

# JSON output for parsing
hass-cli -o json state get sensor.entity_name

# List and filter
hass-cli state list | grep automation
hass-cli state list | jq '.[] | select(.entity_id | startswith("sensor."))'
```

### Service Calls

```bash
# Reload automations
hass-cli service call automation.reload

# Trigger with arguments
hass-cli service call automation.trigger --arguments entity_id=automation.name

# Call script
hass-cli service call script.my_script

# Reload core config
hass-cli service call homeassistant.reload_core_config
```

### Raw API Access

```bash
# GET request
hass-cli raw get /api/states/sensor.entity_name

# POST with JSON
hass-cli raw post /api/template --json '{"template": "{{ now() }}"}'

# Custom endpoints
hass-cli raw post /api/services/custom/do_something --json '{"data": "value"}'
```

---

## 🚨 CRITICAL: hass-cli Global Options MUST Come First

**Global options must appear BEFORE the subcommand, not after.**

```bash
# ✅ CORRECT - global options BEFORE subcommand
hass-cli -o yaml state get sensor.example
hass-cli --output json state list
hass-cli --timeout 30 service call automation.reload

# ❌ WRONG - global options AFTER subcommand
hass-cli state get sensor.example --output yaml   # Error: No such option
hass-cli state list --timeout 30                   # Error: No such option
```

### Global Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Format: `json`, `yaml`, `table`, `auto` | `auto` |
| `--timeout INTEGER` | Network timeout in seconds | `5` |
| `-s, --server TEXT` | Server URL (or HASS_SERVER env) | `auto` |
| `--token TEXT` | Bearer token (or HASS_TOKEN env) | - |
| `-v, --verbose` | Verbose mode | - |

### Common Usage Patterns

```bash
# Get entity as YAML (includes attributes)
hass-cli -o yaml state get sensor.example

# List all automations as JSON
hass-cli -o json state list | jq '.[] | select(.entity_id | startswith("automation."))'

# Trigger automation with argument
hass-cli service call automation.trigger --arguments entity_id=automation.name

# Reload with extended timeout
hass-cli --timeout 30 service call automation.reload
```

---

## 🚨 Common hass-cli Mistakes

### Mistake 0: Not Using --help Before Trying Alternatives

**❌ WRONG:**
```bash
hass-cli state get sensor.example --some-flag
# Error: No such option: --some-flag

# Immediately tries curl instead (WRONG!)
curl -H "Authorization: Bearer $HASS_TOKEN" $HASS_SERVER/api/states/sensor.example
```

**✅ CORRECT:**
```bash
# Step 1: Check help to verify correct syntax
hass-cli state get --help
# Output shows available options (none for --some-flag)

# Step 2: Find correct alternative from help or global options
hass-cli --output json state get sensor.example

# Step 3: Only if help confirms feature doesn't exist, consider raw/curl
hass-cli raw get /api/states/sensor.example
```

**🚨 RULE: Whenever you get an error, run `--help` BEFORE trying any alternative.**

### Mistake 1: Non-Existent `automation` Subcommand

**❌ WRONG:**
```bash
hass-cli automation info --id automation.name
hass-cli automation list
```

**✅ CORRECT:**
```bash
# Automations are state entities, use state commands
hass-cli state get automation.name
hass-cli state list | grep automation
```

### Mistake 2: `--attributes` Flag Doesn't Exist

**❌ WRONG:**
```bash
hass-cli state get device_tracker.phone --attributes
# Error: No such option: --attributes
```

**✅ CORRECT:**
```bash
# state get returns attributes automatically
hass-cli state get device_tracker.phone

# Or use YAML output for full details
hass-cli -o yaml state get device_tracker.phone
```

### Mistake 3: Wrong `state get` Syntax

**❌ WRONG:**
```bash
hass-cli state get | grep automation
# Error: Missing argument 'ENTITY'
```

**✅ CORRECT:**
```bash
hass-cli state list | grep automation
```

---

## Template Evaluation via REST API

When you need to test templates:

```bash
source .env
curl -s -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  http://$HASS_SERVER/api/template \
  -d '{"template": "{{ states(''sensor.example'') }}"}'
```

---

## SSH Access Patterns

### Clean SSH Output (No Visual Host Key)

**Use `-oVisualHostKey=no` to suppress the visual fingerprint display.**

```bash
# ✅ CORRECT - Clean output without grep filtering
ssh -oVisualHostKey=no ha "ha core logs | tail -50"

# ❌ INEFFICIENT - Uses grep to filter fingerprint
ssh ha "ha core logs | tail -50" 2>/dev/null | grep -v "Host key\|ED25519\|+--\||\|--\|SHA256"
```

**Why this matters:**
- `-oVisualHostKey=no` disables the fingerprint at the source
- No need for post-processing with `grep`
- More efficient and cleaner command structure
- Works with any SSH command (logs, git, docker, etc.)

**Best Practice:** Configure this permanently in `~/.ssh/config`:

```bash
# ~/.ssh/config
Host ha
    HostName homeassistant.local
    User root
    VisualHostKey no
```

Then `ssh ha` never shows the fingerprint.

### Quick Commands

```bash
# Check logs (clean output)
ssh -oVisualHostKey=no ha "ha core logs | tail -50"

# Validate configuration
ssh -oVisualHostKey=no ha "ha core check"

# Restart (ASK FIRST!)
ssh -oVisualHostKey=no ha "ha core restart"

# Check git status
ssh -oVisualHostKey=no ha "cd /homeassistant && git status"

# Pull changes (if clean)
ssh -oVisualHostKey=no ha "cd /homeassistant && git pull"
```

### Docker Commands

```bash
# Check container status
ssh -oVisualHostKey=no ha "docker ps --filter name=homeassistant"

# View container logs
ssh -oVisualHostKey=no ha "docker logs homeassistant"
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **🚨 Check syntax FIRST** | `hass-cli [subcommand] --help` |
| Get entity state | `hass-cli state get entity.name` |
| Get with attributes | `hass-cli -o yaml state get entity.name` |
| List all states | `hass-cli state list` |
| Call service | `hass-cli service call domain.service --arguments key=value` |
| Reload automations | `hass-cli service call automation.reload` |
| Trigger automation | `hass-cli service call automation.trigger --arguments entity_id=automation.name` |
| Test template | `curl -H "Authorization: Bearer $HASS_TOKEN" -d '{"template": "..."}' http://$HASS_SERVER/api/template` |
| SSH logs | `ssh -oVisualHostKey=no ha "ha core logs \| tail -50"` |
| Validate config | `ssh -oVisualHostKey=no ha "ha core check"` |
