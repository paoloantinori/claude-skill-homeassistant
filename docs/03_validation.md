# 03. Validation & Safety Checks

**Home Assistant Manager - Pre-Deployment Validation**

---

## 🛡️ MANDATORY: Validate BEFORE Deploy

**CRITICAL RULE:** Always run `ha core check` BEFORE deploying changes, not after.

### Correct vs Incorrect Order

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

### Why This Matters

| Benefit | Explanation |
|---------|-------------|
| **Early detection** | Catches syntax errors before production |
| **Safety** | Avoids deploying broken config |
| **Efficiency** | Prevents unnecessary restart attempts |
| **Best practice** | Follows "evidence > assumptions" principle |

---

## Built-in Logger Filters (No Custom Components Needed)

Home Assistant has **native regex log filtering** - always use this instead of custom components for suppressing noisy log messages.

### Configuration

**Location:** `configuration.yaml` under `logger: filters:`

```yaml
logger:
  default: info
  filters:
    <logger_name>:
      - "^regex_pattern_to_filter"
```

### Example: Filter Ariston Cycle Messages

```yaml
logger:
  filters:
    homeassistant.components.sensor.recorder:
      - "^Detected new cycle for sensor\\.ariston_"
```

### Finding the Logger Name

Look at the log message format:
```
INFO (Recorder) [homeassistant.components.sensor.recorder] Detected new cycle...
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                 This is the logger name to use in filters
```

### Reload Behavior

**Logger filters require a RESTART to take effect.**

`homeassistant.reload_core_config` does NOT reload logger filters.

---

## Pre-Deployment Checklist

Before deploying any changes:

- [ ] Run `ssh ha "ha core check"` - no errors
- [ ] For templates: Test syntax locally if possible
- [ ] For automations: Verify triggers, conditions, actions
- [ ] For scripts: Check parameter passing
- [ ] For configuration.yaml: Validate integration syntax
- [ ] Plan reload vs restart (see docs/01_critical_safety.md)
- [ ] Have rollback plan (git revert or previous file version)

---

## Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `mapping values are not allowed here` | YAML indentation error | Check indentation with spaces |
| `could not find configuration` | Invalid integration/platform | Check integration name spelling |
| `undefined name 'xyz'` | Template variable not defined | Check variable exists in scope |
| `extra keys not allowed` | Invalid YAML key | Remove or rename key |

---

## Quick Reference

```bash
# Validate configuration
ssh ha "ha core check"

# Check specific file (if applicable)
ssh ha "ha core check --file configuration.yaml"

# View logs after deploy
ssh ha "ha core logs | tail -50"

# Check for errors
ssh ha "ha core logs | grep -i error | tail -20"
```
