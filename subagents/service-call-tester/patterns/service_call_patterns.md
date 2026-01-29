# Service Call Patterns Library

**Purpose**: Known service call patterns with detection methods, error diagnosis, and fixes

---

## Pattern 1: Service Not Found

**Common causes**:
- Typo in service domain or name
- Service not registered (integration not loaded)
- Incorrect service format
- Wrong service domain

**Detection**:
```bash
source .env && hass-cli service list | grep service_name
```

**Example errors**:
```yaml
# WRONG: Typo in service domain
service: notify.teegram  ← Should be notify.telegram

# WRONG: Service not loaded
service: notify.nonexistent_service  ← Integration not configured

# WRONG: Incorrect format
service: telegram.send_message  ← Should be notify.telegram
```

**Fix**:
- Verify service domain spelling
- Check integration is loaded and configured
- Use correct service format: `domain.service`
- List available services: `hass-cli service list`

**Reference**: HA Manager skill docs/06_common_mistakes.md

---

## Pattern 2: Invalid Parameters

**Common causes**:
- Missing required parameters
- Extra parameters not allowed
- Wrong parameter type
- Deprecated parameter names

**Detection**:
```bash
source .env && hass-cli service call service.domain --help
```

**Example errors**:
```yaml
# WRONG: Missing required parameter
service: light.turn_on
data: {}  ← Missing 'entity_id'

# WRONG: Extra parameter
service: notify.telegram
data:
  message: "Test"
  extra_key: "value"  ← Not allowed by schema

# WRONG: Wrong parameter type
service: input_number.set_value
data:
  value: "not_a_number"  ← Should be number, not string
```

**Fix**:
- Check service schema for required parameters
- Remove extra parameters
- Use correct parameter types
- Update deprecated parameters
- Use `--help` to see service schema

**Reference**: HA Manager skill docs/06_common_mistakes.md

---

## Pattern 3: Entity Not Found

**Common causes**:
- Entity ID typo
- Entity doesn't exist
- Entity unavailable (device offline)
- Wrong entity domain

**Detection**:
```bash
source .env && hass-cli state list | grep entity_id
```

**Example errors**:
```yaml
# WRONG: Entity typo
service: light.turn_on
data:
  entity_id: light.living_rom_lamp  ← Should be light.living_room_lamp

# WRONG: Entity doesn't exist
service: automation.trigger
data:
  entity_id: automation.nonexistent_automation

# WRONG: Wrong entity domain
service: light.turn_on
data:
  entity_id: switch.living_room  ← Wrong domain, should be light
```

**Fix**:
- Verify entity ID spelling
- Check entity exists: `hass-cli state list | grep pattern`
- Confirm entity is available
- Use correct entity domain

**Reference**: Config Validator subagent - Entity Reference Verification

---

## Pattern 4: Permission Denied

**Common causes**:
- Service requires admin privileges
- Entity is protected
- User lacks permission
- Authentication issues

**Detection**:
```bash
# Check service response for permission errors
source .env && hass-cli service call service.domain --arguments '{...}'
```

**Example errors**:
```yaml
# ERROR: Unauthorized
service: automation.delete
data:
  entity_id: automation.protected_automation
→ Error: Unauthorized - requires admin privileges

# ERROR: Forbidden
service: config_entries.delete
data:
  entry_id: "abc123"
→ Error: Forbidden - cannot delete active entry
```

**Fix**:
- Check if service requires admin access
- Verify user has necessary permissions
- Use admin account if required
- Check authentication token is valid

---

## Pattern 5: Service Timeout

**Common causes**:
- Device not responding
- Network timeout
- Service hanging
- Long-running command

**Detection**:
```bash
# Service call takes too long
timeout 15 hass-cli service call service.domain --arguments '{...}'
```

**Example errors**:
```yaml
# ERROR: Timeout
service: shell_command.execute
data:
  command: "long_running_command"
→ Error: Command timed out after 15 seconds

# ERROR: Device not responding
service: light.turn_on
data:
  entity_id: light.unresponsive_device
→ Error: Device not responding
```

**Fix**:
- Increase timeout for long-running services
- Check device/network connectivity
- Use background execution for long commands
- Restart device if unresponsive

---

## Pattern 6: Invalid Entity ID Format

**Common causes**:
- Missing domain prefix
- Wrong separator
- Invalid characters

**Detection**:
```bash
# Check entity ID format
echo "sensor.temperature" | grep -E '^[a-z_]+\.[a-z0-9_]+$'
```

**Example errors**:
```yaml
# WRONG: Missing domain
entity_id: temperature  ← Should be sensor.temperature

# WRONG: Wrong separator
entity_id: sensor-temperature  ← Should be sensor.temperature

# WRONG: Invalid characters
entity_id: sensor.Temperature  ← Should be lowercase
```

**Fix**:
- Use format: `domain.entity_id`
- Use dot (.) as separator
- Use lowercase letters, numbers, and underscores only
- No special characters except underscore

---

## Pattern 7: Template Errors in Parameters

**Common causes**:
- Invalid Jinja2 syntax
- Undefined variables in templates
- Wrong attribute access
- Template rendering errors

**Detection**:
```bash
# Test template in Developer Tools → Template
source .env && hass-cli raw post /api/template --json '{"template": "{{states('sensor.x')}}"}'
```

**Example errors**:
```jinja2
// WRONG: Unclosed bracket
{{ states('sensor.x') |

// WRONG: Undefined variable
{{ states.nonexistent_sensor }}

// WRONG: Wrong attribute access
{{ state_attr('sensor.x', 'last_updated') }}  ← Use states.sensor.x.last_updated
```

**Fix**:
- Close all brackets: `{{ ... }}`
- Verify variables exist
- Use correct attribute access methods
- Test templates in Developer Tools first

**Reference**: HA Manager skill docs/06_common_mistakes.md

---

## Pattern 8: Service Call Returns No Data

**Common causes**:
- Service doesn't return data
- Service executed but failed silently
- Service returned None/null
- Service completed but has no output

**Detection**:
```bash
# Execute service and check response
source .env && hass-cli service call service.domain --arguments '{...}' --output json
```

**Example scenarios**:
```yaml
# Service returns nothing
service: automation.trigger
data:
  entity_id: automation.test
→ Response: (no output, expected behavior)

# Service failed silently
service: notify.telegram
data:
  message: "Test"
→ Response: (no output, may indicate error)
→ Check logs for errors
```

**Fix**:
- Check if service is expected to return data
- Verify service executed successfully
- Check logs for errors
- Test service manually

---

## Quick Reference: Common Service Call Issues

| Issue | Detection | Fix |
|-------|-----------|-----|
| **Service not found** | `hass-cli service list` | Fix spelling, check integration |
| **Invalid parameters** | `hass-cli service call --help` | Check schema, fix parameters |
| **Entity not found** | `hass-cli state list \| grep entity` | Fix entity ID or remove |
| **Permission denied** | Check error message | Use admin account, check permissions |
| **Service timeout** | Timeout occurs | Check device, increase timeout |
| **Invalid entity ID format** | Check entity ID format | Use domain.entity format |
| **Template errors** | Test in Developer Tools | Fix Jinja2 syntax |
| **No data returned** | Check response | Check logs, verify service executed |

---

## Read-Only Services

Safe to test without state changes:

```yaml
# Home Assistant
- homeassistant.check_config
- homeassistant.reload_core_config
- homeassistant.reload_template_entity
- homeassistant.restart (ASK FIRST - state change)

# Automation
- automation.reload
- automation.trigger (may trigger actions, but doesn't change config)

# Script
- script.reload
- script.turn_on (executes script, may have side effects)

# Template
- homeassistant.reload_template_entity

# Logger
- logger.set_level

# Group
- group.reload

# Scene
- scene.reload

# Input Boolean/Number/Text/Datetime
- input_boolean.reload
- input_number.reload
- input_text.reload
- input_datetime.reload

# MQTT
- mqtt.reload
```

**State-changing services** (require explicit permission):
- `light.turn_on`
- `light.turn_off`
- `switch.turn_on`
- `switch.turn_off`
- `automation.delete`
- `script.delete`
- `homeassistant.restart`

---

## Service Call Testing Best Practices

### Before Testing

1. **Verify Service Exists**
   ```bash
   hass-cli service list | grep service_name
   ```

2. **Check Service Schema**
   ```bash
   hass-cli service call service.domain --help
   ```

3. **Validate Parameters**
   - Check required parameters
   - Verify parameter types
   - Check for deprecated parameters

### During Testing

4. **Use Dry-Run First**
   - Validate without executing
   - Check risk assessment
   - Review warnings

5. **Start with Read-Only**
   - Test read-only services first
   - Verify they work as expected
   - Then test state-changing services

6. **Check Responses**
   - Verify service executed successfully
   - Check for errors in response
   - Review logs if service failed

### After Testing

7. **Verify State Changes**
   - Check entity states changed as expected
   - Verify automation executed
   - Confirm side effects

8. **Review Logs**
   - Check for errors or warnings
   - Verify service execution
   - Look for unexpected behavior

---

## Integration with Other Subagents

**Config Validator**: Validates service calls in YAML configurations
- Config Validator checks service calls in automations/scripts
- Service Call Tester tests service calls in isolation

**Automation Verifier**: Tests service calls within automations
- Automation Verifier tests complete automation execution
- Service Call Tester tests individual service calls

**HA Log Analyzer**: Service call error diagnosis
- Service Call Tester diagnoses service call failures
- HA Log Analyzer checks logs for service errors

**Deployment Orchestrator**: Service call testing during deployment
- Deployment Orchestrator deploys changes
- Service Call Tester validates service calls before execution

---

## Service Call Examples

### Notification Service

```yaml
# Valid call
service: notify.telegram
data:
  message: "Test notification"
  target: ["-123456789"]
  title: "Test Title"

# Common error
service: notify.telegram
data:
  message: "Test"
  targets: ["-123456789"]  ← Wrong: should be 'target'
```

### Light Service

```yaml
# Valid call
service: light.turn_on
data:
  entity_id: light.living_room
  brightness_pct: 100

# Common error
service: light.turn_on
data:
  entity_id: light.living_room
  brightness: 255  ← Wrong: should be brightness_pct
```

### Automation Service

```yaml
# Valid call
service: automation.trigger
data:
  entity_id: automation.test_automation
  skip_condition: true

# Common error
service: automation.trigger
data:
  entity_id: "automation.test"  ← Wrong: should be automation.test_automation
```

### Template Service

```yaml
# Valid call
service: homeassistant.reload_template_entity
data: {}  ← No parameters required

# Common error
service: homeassistant.reload_template_entity
data:
  entity_id: sensor.template_sensor  ← Wrong: no parameters needed
```

---

## Troubleshooting Checklist

When service call fails:

1. **Check Service Exists**
   [ ] Service is registered: `hass-cli service list | grep service`

2. **Check Parameters**
   [ ] Required parameters provided
   [ ] Parameter types correct
   [ ] No extra parameters

3. **Check Entity**
   [ ] Entity exists: `hass-cli state list | grep entity`
   [ ] Entity is available
   [ ] Entity ID format correct

4. **Check Permissions**
   [ ] User has necessary permissions
   [ ] Service doesn't require admin
   [ ] Authentication token valid

5. **Check Logs**
   [ ] Review HA logs: `ha core logs | tail -50`
   [ ] Check for service errors
   [ ] Look for specific error messages

6. **Test Manually**
   [ ] Test service in Developer Tools
   [ ] Verify service works as expected
   [ ] Compare with working calls

---

## Service Call Safety Rules

1. **Test in isolation first**
2. **Use dry-run for state-changing services**
3. **Start with read-only services**
4. **Always validate parameters**
5. **Check entity exists before referencing**
6. **Review risk assessment before executing**
7. **Verify permissions before calling**
8. **Check logs after execution**
