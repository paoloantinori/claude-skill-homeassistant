# 08. Quick Reference Commands

**Home Assistant Manager - Command Cheat Sheet**

---

## 🚨 CRITICAL Pattern Notes

### 1. Use hass-cli, NEVER curl

**All Home Assistant API interactions MUST use hass-cli.**

```bash
# ✅ CORRECT - Simple, clear
hass-cli state get sensor.example
hass-cli service call automation.reload

# ❌ WRONG - Overly complex, don't use
curl -H "Authorization: Bearer $HASS_TOKEN" http://$HASS_SERVER/api/states/sensor.example
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" http://$HASS_SERVER/api/services/automation/reload
```

**See `docs/07_remote_access.md` for complete curl → hass-cli translation guide.**

### 2. SSH Clean Output

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
ssh -oVisualHostKey=no ha "cd /homeassistant && git status && git pull"

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
| Reload templates | `hass-cli service call template.reload` |
| Trigger automation | `hass-cli service call automation.trigger --arguments entity_id=automation.name` |
| Check entity state | `hass-cli state get entity.name` |
| View logs | `ssh -oVisualHostKey=no ha "ha core logs \| tail -50"` |
| Deploy via SCP | `scp file.yaml ha:/homeassistant/` |
| Deploy via Git | `ssh -oVisualHostKey=no ha "cd /homeassistant && git status && git pull"` |
| Restart HA | `ssh -oVisualHostKey=no ha "ha core restart"` (ASK FIRST!) |

---

## Reload Services by Entity Type

**IMPORTANT:** Each entity type has its own reload service. Do NOT use `homeassistant.reload_config_entry` for YAML-defined entities.

| Entity Type | Reload Service |
|-------------|----------------|
| Automations | `automation.reload` |
| Scripts | `script.reload` |
| Scenes | `scene.reload` |
| Input Booleans | `input_boolean.reload` |
| Input Numbers | `input_number.reload` |
| Input Selects | `input_select.reload` |
| Input Text | `input_text.reload` |
| Input Datetime | `input_datetime.reload` |
| Input Buttons | `input_button.reload` |
| Template Entities | `template.reload` |
| Groups | `group.reload` |
| Timers | `timer.reload` |
| Counters | `counter.reload` |
| Schedules | `schedule.reload` |
| Zones | `zone.reload` |
| Persons | `person.reload` |
| MQTT | `mqtt.reload` |

**Wrong (causes error):**
```bash
# ❌ This fails for YAML-defined entities
hass-cli service call homeassistant.reload_config_entry --arguments entity_id=input_boolean.example
# ValueError: There were no matching config entries to reload
```

**Correct:**
```bash
# ✅ Use the entity-specific reload service
hass-cli service call input_boolean.reload
```

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

---

## Ghost Entity Investigation (Spook Warnings)

When Spook Integration reports "unknown entities" in dashboards:

```bash
# Step 1: Verify entity exists on server (NOT local files)
source .env && hass-cli state list | grep entity_id

# Step 2: If exists, check if used in automations
grep -r "entity_id" automations/

# Step 3: Decision matrix:
# - Exists + used in automation → Keep dashboard reference (Spook may be wrong)
# - Not in hass-cli state list → Remove from dashboard (truly missing)
# - Defined in YAML but not loaded → May need restart
```

**Remember:**
- Trust `hass-cli state list` (server state) over local file searches
- `!include_dir_merge_named` loads from FOLDER, not single files
- Spook warnings are hints to investigate, not verdicts to delete

**Example:**
```bash
# Spook says: input_boolean.segnala_chiara_ripartita unknown

# Verify exists:
$ source .env && hass-cli state list | grep segnala_chiara
input_boolean.segnala_chiara_ripartita    on    # EXISTS!

# Check usage:
$ grep -r "segnala_chiara_ripartita" automations/
automations/location/location.yaml:    # Used by automation

# Conclusion: Keep dashboard reference, entity is functional
```
