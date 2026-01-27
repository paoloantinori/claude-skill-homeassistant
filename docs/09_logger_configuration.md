# 09. Logger Configuration

**Home Assistant Manager - Logger Level Adjustments**

---

## Overview

Home Assistant's logging system is configured in `configuration.yaml` under the `logger:` section. Adjusting logger levels is a common maintenance task to reduce log noise or debug specific components.

**⚠️ IMPORTANT:** Logger changes in `configuration.yaml` require a **restart** to take effect. There is no reload option for logger configuration.

---

## Quick Reference: Logger Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| `debug` | Troubleshooting specific component | `custom_components.smartir.climate: debug` |
| `info` | Normal operation (default) | `homeassistant.components.automation: info` |
| `warning` | Reduce noise from chatty components | `homeassistant.helpers.script: warning` |
| `error` | Only show errors | `homeassistant.components.climate: error` |
| `critical` | Severe issues only | Rarely used |

---

## Standard Workflow: Change Logger Level

**Use this pattern when adjusting any logger level:**

```bash
# 1. Locate the logger in configuration.yaml
grep -n "homeassistant.helpers.script" configuration.yaml
# or search by component name
grep -n "logger:" -A 50 configuration.yaml | grep "component_name"

# 2. Edit the logger level locally
# Change: homeassistant.helpers.script: info
# To:      homeassistant.helpers.script: warning

# 3. Deploy via scp (rapid testing)
scp configuration.yaml ha:/homeassistant/

# 4. ⚠️ CRITICAL: Logger changes require RESTART
# Ask user: "Logger changes require restart. May I restart Home Assistant?"
# Wait for explicit confirmation, then:
ssh ha "ha core restart"

# 5. After restart, verify logging changed
ssh ha "ha core logs | tail -50"
# Should see reduced/increased log output for the component

# 6. Once verified, commit to git
git add configuration.yaml
git commit -m "chore: Reduce logging for homeassistant.helpers.script to warning"
git push
```

---

## Common Logger Adjustments

### Reduce Script Execution Logs

**Problem:** Scripts log every step execution, creating noise

**Solution:**
```yaml
logger:
  logs:
    homeassistant.helpers.script: warning
    homeassistant.components.script: warning
```

### Reduce Automation Step Logs

**Problem:** Automations log trigger/condition/action steps verbosely

**Solution:**
```yaml
logger:
  logs:
    homeassistant.components.automation: warning
```

### Debug Specific Custom Component

**Problem:** Custom component not working, need more detail

**Solution:**
```yaml
logger:
  logs:
    custom_components.my_component: debug
```

### Reduce Bluetooth Scanner Noise

**Problem:** Bluetooth scanner spam about "gone quiet"

**Solution:**
```yaml
logger:
  logs:
    habluetooth.scanner: warning
```

---

## Finding the Right Logger Name

**Method 1: Search existing logs**
```bash
ssh ha "ha core logs | grep 'noisy message' | head -5"
# Look for logger name in brackets: [homeassistant.helpers.script.intent_script_caldaia]
```

**Method 2: Search configuration.yaml**
```bash
grep -n "logger:" -A 100 configuration.yaml | grep "partial_name"
```

**Method 3: Check HA documentation**
- Component docs often specify logger names
- Format: `homeassistant.components.<component_type>.<component_name>`
- Custom components: `custom_components.<integration_name>`

---

## Logger Hierarchy

Understanding logger hierarchy helps target the right level:

```
homeassistant (root)
├── homeassistant.components (all core components)
│   ├── homeassistant.components.automation
│   ├── homeassistant.components.script
│   └── homeassistant.components.sensor
├── homeassistant.helpers (internal helpers)
│   ├── homeassistant.helpers.script
│   ├── homeassistant.helpers.template
│   └── homeassistant.helpers.intent
└── custom_components (all custom integrations)
    ├── custom_components.hacs
    └── custom_components.places
```

**Rule of thumb:** Use the most specific logger that covers your use case.

---

## Decision Tree: Which Logger Level?

```
Why are you changing this?
├─ Troubleshooting a bug
│  └─ Set to: debug
│     Remember to revert after fixing!
│
├─ Logs too verbose/noisy
│  └─ Set to: warning
│     Keeps errors and warnings, hides info/debug
│
└─ Only care about errors
   └─ Set to: error
      Shows only errors and critical issues
```

---

## Quick Command Reference

| Task | Command |
|------|---------|
| Find logger in config | `grep -n "logger:" -A 50 configuration.yaml \| grep pattern` |
| Find logger name in logs | `ssh ha "ha core logs \| grep -E '\[.*\]' \| head -10"` |
| Deploy config change | `scp configuration.yaml ha:/homeassistant/` |
| Verify after restart | `ssh ha "ha core logs \| tail -50"` |
| Check current logger level | `ssh ha "ha core options \| grep -A 20 logger"` |

---

## Common Pitfalls

| Mistake | Consequence | Solution |
|---------|-------------|----------|
| Forgot to restart | Changes don't take effect | Logger changes require restart |
| Set too broad (debug on all) | Performance impact, huge logs | Be specific with logger names |
| Forgot to revert debug | Logs stay verbose forever | Set reminder to revert after troubleshooting |
| Wrong logger name | Change has no effect | Verify logger name in actual log output |

---

## Examples from This Project

Current logger configuration (as of latest commit):

```yaml
logger:
  default: info
  logs:
    # Noise reduction
    homeassistant.components.automation: warning
    homeassistant.components.script: warning
    homeassistant.helpers.script: warning

    # Debug specific components
    custom_components.smartir.climate: debug
    homeassistant.components.dialogflow: debug

    # Error-only for chatty components
    homeassistant.components.climate: error
    androidtv.adb_manager.adb_manager_async: error
```

---

## Pattern: One-Line Logger Change

**When you know exactly what to change:**

```bash
# 1. Find and edit in one pass
sed -i 's/homeassistant\.helpers\.script: info/homeassistant.helpers.script: warning/' configuration.yaml

# 2. Deploy
scp configuration.yaml ha:/homeassistant/

# 3. Restart (ASK FIRST!)
# "Logger changes require restart. May I restart?"

# 4. Verify
ssh ha "ha core logs | tail -20"

# 5. Commit
git add configuration.yaml
git commit -m "chore: Reduce script logging to warning"
git push
```

---

## Remember: Always Ask Before Restart

Logger changes require a Home Assistant restart. **Always ask:**

> "Logger changes in configuration.yaml require a restart to take effect. May I restart Home Assistant?"

**Wait for explicit "yes" or "go ahead" before restarting.**
