# 07. Remote Access & Tools

**Home Assistant Manager - Remote CLI Access**

---

## Prefer hass-cli Over curl

**Always use hass-cli first.** Do NOT fall back to curl unless hass-cli is genuinely broken.

### Why hass-cli?

| Benefit | Explanation |
|---------|-------------|
| **Authentication** | Handles HASS_SERVER/HASS_TOKEN automatically |
| **Consistency** | Predictable output formatting |
| **Efficiency** | No env var debugging |
| **Features** | Covers most HA API operations |

### hass-cli Capabilities

```bash
# State queries
hass-cli state get sensor.entity_name              # Basic state
hass-cli -o yaml state get sensor.entity_name      # With attributes

# Service calls
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name

# Raw API access (when you need JSON)
hass-cli raw get /api/states/sensor.entity_name
hass-cli raw post /api/template --json '{"template": "{{ now() }}"}'
```

### If hass-cli Fails

1. Check `.env` sourced: `echo $HASS_TOKEN | head -c 20`
2. Try explicit sourcing: `eval "$(cat /path/to/.env)"`
3. Only then consider curl as last resort

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

### Quick Commands

```bash
# Check logs
ssh ha "ha core logs | tail -50"

# Validate configuration
ssh ha "ha core check"

# Restart (ASK FIRST!)
ssh ha "ha core restart"

# Check git status
ssh ha "cd /homeassistant && git status"

# Pull changes
ssh ha "cd /homeassistant && git pull"
```

### Docker Commands

```bash
# Check container status
ssh ha "docker ps --filter name=homeassistant"

# View container logs
ssh ha "docker logs homeassistant"
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Get entity state | `hass-cli state get entity.name` |
| Get with attributes | `hass-cli -o yaml state get entity.name` |
| List all states | `hass-cli state list` |
| Call service | `hass-cli service call domain.service --arguments key=value` |
| Reload automations | `hass-cli service call automation.reload` |
| Trigger automation | `hass-cli service call automation.trigger --arguments entity_id=automation.name` |
| Test template | `curl -H "Authorization: Bearer $HASS_TOKEN" -d '{"template": "..."}' http://$HASS_SERVER/api/template` |
| SSH logs | `ssh ha "ha core logs \| tail -50"` |
| Validate config | `ssh ha "ha core check"` |
