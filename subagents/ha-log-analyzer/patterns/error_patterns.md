# Error Patterns Library

**Purpose**: Known Home Assistant error patterns with diagnosis and suggested actions

---

## Template Errors

### Pattern: Undefined Variable
**Log message**:
```
Template variable warning: 'undefined_var' is not defined
```

**Diagnosis**: Template references a variable that doesn't exist in template context

**Common causes**:
- Typo in variable name
- Variable not available in template scope
- Using wrong state attribute access method

**Suggested actions**:
1. Check template for typos in variable names
2. Verify variable is available in template context
3. For entity attributes, use `state_attr('entity', 'attr')` not `states.entity.attr`
4. Test template in Developer Tools → Template

**Reference**: HA Manager skill docs/06_common_mistakes.md (Mistake 9)

---

### Pattern: Last Updated Access Error
**Log message**:
```
TypeError: 'NoneType' object has no attribute 'timestamp'
```

**Diagnosis**: Using `state_attr()` to access core entity properties like `last_updated`

**Common causes**:
- `state_attr('entity', 'last_updated')` returns None
- `last_updated` is a core property, not an attribute

**Suggested actions**:
1. Use `states.entity.last_updated` instead of `state_attr('entity', 'last_updated')`
2. Other core properties: `last_changed`, `last_reported`, `state`
3. Test template: `source .env && hass-cli raw post /api/template --json '{"template": "{% set x = states.xxx.last_updated %}{{ x }}"}'`

**Reference**: HA Manager skill docs/06_common_mistakes.md (Mistake 9)

---

## Service Call Errors

### Pattern: Invalid Service Data
**Log message**:
```
Invalid data for call_service: @data['invalid_key']
Error loading Script because invalid service data
```

**Diagnosis**: Service call parameters don't match service schema

**Common causes**:
- Typos in parameter names
- Using old parameter names (HA version changed)
- Missing required parameters
- Extra keys not allowed by service schema

**Suggested actions**:
1. Check service schema: Developer Tools → Services
2. Verify parameter names match current HA version
3. Test service call manually before adding to automation
4. Use `hass-cli service call <service> --help` to check parameters

**Reference**: HA Manager skill docs/06_common_mistakes.md (Mistake 4)

---

### Pattern: Service Not Found
**Log message**:
```
Service not found: domain.nonexistent_service
```

**Diagnosis**: Attempting to call a service that doesn't exist

**Common causes**:
- Typo in service name
- Service doesn't exist in integration
- Integration not loaded

**Suggested actions**:
1. Verify service name: Developer Tools → Services
2. Check integration is loaded: `hass-cli state list | grep integration.<name>`
3. Check for typos in service domain or service name

---

## Automation Errors

### Pattern: Failed to Generate Automation
**Log message**:
```
Error doing work: Failed to generate automation
Error while setting up automation platform for automation
```

**Diagnosis**: YAML syntax error or invalid automation configuration

**Common causes**:
- YAML syntax error (indentation, quotes)
- Undefined entities referenced
- Invalid trigger/action syntax
- Template errors in automation

**Suggested actions**:
1. Check automation YAML syntax
2. Verify all referenced entities exist
3. Validate config: `ssh ha "ha core check"`
4. Check for typos in entity IDs
5. Test templates in Developer Tools

---

### Pattern: Trigger Not Firing
**Log message**:
```
(No error in logs, automation just doesn't trigger)
```

**Diagnosis**: Automation trigger conditions not being met

**Common causes**:
- Entity state never matches trigger condition
- Time/condition not met
- Automation disabled
- Mode set incorrectly (single, parallel, restart, queued)

**Suggested actions**:
1. Check automation is enabled: `hass-cli state get automation.<name>` (state should be 'on')
2. Check trigger entity state: `hass-cli state get <trigger_entity>`
3. Verify trigger conditions are realistic
4. Check automation mode setting
5. Manually trigger to test logic: `hass-cli service call automation.trigger --arguments entity_id=automation.<name>`

---

## Entity Errors

### Pattern: Entity Not Found
**Log message**:
```
Entity not found: sensor.unknown_sensor
```

**Diagnosis**: Referenced entity doesn't exist in Home Assistant

**Common causes**:
- Typo in entity ID
- Entity not yet created (integration hasn't loaded)
- Entity was deleted or renamed

**Suggested actions**:
1. Check for typos in entity ID
2. Verify entity exists: `hass-cli state list | grep sensor.unknown_sensor`
3. Check if integration is loaded: `hass-cli state list | grep integration.<name>`
4. May need to wait for integration to initialize

---

### Pattern: Entity Not Ready
**Log message**:
```
Entity sensor.xyz is not ready yet
```

**Diagnosis**: Entity referenced before it's fully initialized

**Common causes**:
- Template sensor referencing entity not yet loaded
- Automation triggering before integration initializes
- Race condition during HA startup

**Suggested actions**:
1. Add `{{ states.sensor.xyz.state not in ['unknown', 'unavailable'] }}` condition
2. Use `wait_template` to wait for entity to be ready
3. Add delay automation trigger to allow startup to complete

---

## Reload Errors

### Pattern: No Matching Config Entries
**Log message**:
```
ValueError: There were no matching config entries to reload
```

**Diagnosis**: Using wrong reload service for entity type

**Common causes**:
- Using `homeassistant.reload_config_entry` for YAML-defined entities
- YAML entities have their own `<domain>.reload` service

**Suggested actions**:
1. For YAML entities (input_boolean, template sensors, etc.): Use `<domain>.reload`
2. Examples:
   - `input_boolean.reload`
   - `template.reload`
   - `group.reload`
   - `mqtt.reload`
3. For UI-configured integrations: `homeassistant.reload_config_entry`

**Reference**: HA Manager skill docs/06_common_mistakes.md (Mistake 12)

---

## Integration Errors

### Pattern: Integration Setup Failed
**Log message**:
```
Error during setup of component integration_name
Error setting up entry integration_name for integration_name
```

**Diagnosis**: Integration failed to initialize

**Common causes**:
- Incorrect configuration (YAML or UI)
- Missing dependencies
- Network connectivity issues
- Authentication/credential errors
- API unavailable (cloud service down)

**Suggested actions**:
1. Check integration configuration in UI or YAML
2. Verify credentials are correct
3. Check network connectivity to integration service
4. Check if cloud service API is operational
5. Review integration documentation for any HA version compatibility issues
6. Check logs for specific error details

---

### Pattern: Integration Not Ready
**Log message**:
```
Integration integration_name not ready yet
```

**Diagnosis**: Integration still initializing

**Common causes**:
- Integration takes time to initialize (normal)
- Network delay
- Service slow to respond

**Suggested actions**:
1. Wait a few minutes for integration to fully initialize
2. Check integration status: `hass-cli state list | grep integration.<name>`
3. If persistent, check network connectivity and service status

---

## Log Analysis Patterns

### Pattern: No Logs After Reload
**Symptom**: After `hass-cli service call automation.reload`, logs show no reload activity

**Diagnosis**: Reload may have failed silently

**Common causes**:
- HA config check failed (but didn't prevent reload)
- Reload service not responding
- Looking at wrong logs

**Suggested actions**:
1. Check logs from before reload command
2. Try reload again
3. Check if automation actually reloaded: `hass-cli state get automation.<name>`
4. If persistent, consider restart (ASK FIRST!)

---

### Pattern: Same Error Repeating
**Symptom**: Same error message repeats in logs every few seconds

**Diagnosis**: Automation or template in error loop

**Common causes**:
- Automation with bad trigger that keeps firing
- Template sensor with error that re-evaluates periodically
- Service call in loop that keeps failing

**Suggested actions**:
1. Identify which automation/template is causing the loop
2. Disable the automation: `hass-cli service call automation.turn_off --arguments entity_id=automation.<name>`
3. Fix the error
4. Re-enable: `hass-cli service call automation.turn_on --arguments entity_id=automation.<name>`

---

## Generic Error Handling

### Pattern: Generic Error Without Context
**Log message**:
```
Error
Unknown error
```

**Diagnosis**: Insufficient error information in logs

**Suggested actions**:
1. Increase log level for specific component:
   ```yaml
   logger:
     default: info
     logs:
       homeassistant.components.automation: debug
       homeassistant.components.script: debug
   ```
2. Restart HA to apply log level changes (ASK FIRST!)
3. Reproduce the error
4. Check logs again with debug output
5. Check HA community forums for similar errors

**Reference**: HA Manager skill docs/09_logger_configuration.md

---

## Quick Reference: Common Error Fixes

| Error | Quick Fix |
|-------|-----------|
| `Template variable warning` | Check template for undefined variables |
| `state_attr() returns None` | Use `states.entity.property` for core properties |
| `Invalid data for call_service` | Check service schema in Developer Tools |
| `Failed to generate automation` | Run `ssh ha "ha core check"` and fix YAML syntax |
| `Entity not found` | Check for typos, verify entity exists |
| `No matching config entries to reload` | Use `<domain>.reload` for YAML entities |
| `Integration setup failed` | Check config, credentials, network connectivity |
| `Same error repeating` | Disable problematic automation, fix error |

---

## Adding New Patterns

To add a new error pattern to this library:

1. **Identify the pattern**: Log message + diagnosis
2. **Document common causes**: Why does this error occur?
3. **Suggest actions**: What should user do to fix it?
4. **Add references**: Link to HA Manager skill docs or other resources
5. **Update quick reference table**: Add to summary table

Format:
```markdown
### Pattern: [Descriptive Name]
**Log message**:
```
[Actual log message]
```

**Diagnosis**: [What is the error?]

**Common causes**:
- [Cause 1]
- [Cause 2]

**Suggested actions**:
1. [Action 1]
2. [Action 2]

**Reference**: [Link to relevant documentation]
```
