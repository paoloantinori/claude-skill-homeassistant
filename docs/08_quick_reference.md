# 08. Quick Reference Commands

**Home Assistant Manager - Command Cheat Sheet**

---

## SSH Pattern Note

**All SSH commands should use `-oVisualHostKey=no` for clean output.**

```bash
# ✅ CORRECT - Clean output
ssh -oVisualHostKey=no ha "ha core check"

# ❌ AVOIDS - Shows visual fingerprint
ssh ha "ha core check"  # Shows fingerprint art
```

**Best Practice:** Add `VisualHostKey no` to `~/.ssh/config` for permanent clean output.

---

## Configuration

```bash
ssh -oVisualHostKey=no ha "ha core check"              # Validate configuration
ssh -oVisualHostKey=no ha "ha core restart"            # Restart HA (ASK FIRST!)
```

## Logs

```bash
ssh -oVisualHostKey=no ha "ha core logs | tail -50"                         # Last 50 lines
ssh -oVisualHostKey=no ha "ha core logs | grep -i error | tail -20"        # Last 20 errors
ssh -oVisualHostKey=no ha "ha core logs | grep -i 'automation' | tail -10" # Automation logs
```

## State & Services

```bash
hass-cli state list                                          # List all entities
hass-cli state get entity.name                               # Get entity state
hass-cli service call automation.reload                      # Reload automations
hass-cli service call automation.trigger --arguments entity_id=automation.name  # Trigger
```

## Deployment

```bash
# Git workflow
git add . && git commit -m "..." && git push
ssh -oVisualHostKey=no ha "cd /homeassistant && git pull"

# SCP workflow (testing)
scp file.yaml ha:/homeassistant/

# Dashboard deployment
scp .storage/lovelace.my_dashboard ha:/homeassistant/.storage/
python3 -m json.tool .storage/lovelace.my_dashboard > /dev/null  # Validate JSON
```

## Quick Test Cycle

```bash
# Full automation test cycle
scp automations.yaml ha:/homeassistant/
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
ssh -oVisualHostKey=no ha "ha core logs | grep -i 'automation' | tail -10"
```

## Common Patterns

| Task | Command |
|------|---------|
| Validate config | `ssh -oVisualHostKey=no ha "ha core check"` |
| Reload automations | `hass-cli service call automation.reload` |
| Reload scripts | `hass-cli service call script.reload` |
| Reload templates | `hass-cli service call homeassistant.reload_template_entity` |
| Trigger automation | `hass-cli service call automation.trigger --arguments entity_id=automation.name` |
| Check entity state | `hass-cli state get entity.name` |
| View logs | `ssh -oVisualHostKey=no ha "ha core logs \| tail -50"` |
| Deploy via SCP | `scp file.yaml ha:/homeassistant/` |
| Deploy via Git | `ssh -oVisualHostKey=no ha "cd /homeassistant && git pull"` |
| Restart HA | `ssh -oVisualHostKey=no ha "ha core restart"` (ASK FIRST!) |

---

## Reload vs Restart Quick Reference

| Operation | Reload? | Restart? |
|-----------|---------|----------|
| Edit automation/script/template | ✅ Yes | ❌ No |
| Add new automation/script | ✅ Yes | ❌ No |
| Add template entity | ❌ No | ✅ Yes |
| Add HACS integration | ❌ No | ✅ Yes |
| Edit configuration.yaml | ⚠️ Maybe | ⚠️ Maybe |
| Add new platform | ❌ No | ✅ Yes |

**When in doubt:** Check `docs/01_critical_safety.md` for full decision tree.
