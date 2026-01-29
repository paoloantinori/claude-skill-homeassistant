# Validation Patterns Library

**Purpose**: Known validation patterns for configuration errors with detection methods and fixes

---

## YAML Syntax Patterns

### Pattern 1: Indentation Errors

**Common errors**:
- Mixed tabs and spaces
- Inconsistent indentation levels
- Wrong indentation depth

**Detection**:
```python
import yaml
try:
    yaml.safe_load(open(file))
except yaml.YAMLError as e:
    if 'indentation' in str(e).lower():
        print(f"Indentation error: {e}")
```

**Example errors**:
```yaml
# WRONG: Mixed tabs and spaces
automation:
	trigger:
	platform: state  # Tab instead of spaces

# WRONG: Inconsistent indentation
automation:
  trigger:
    platform: state
      entity_id: sensor.test  # Wrong depth
```

**Fix**:
- Use 2 spaces for indentation
- Be consistent with indentation levels
- Use YAML linter or editor with YAML support
- Visual check: Align all keys at same indentation level

**Reference**: YAML specification, HA automation docs

---

### Pattern 2: Missing Colons

**Common errors**:
- Missing colon after key name
- Extra colon in value

**Detection**:
```yaml
# Missing colon
automation  # Should be "automation:"
  trigger:

# Extra colon
trigger::  # Should be "trigger:"
  platform: state
```

**Fix**:
- Every key must end with colon
- Values should not have colons (except in strings)
- Check line endings for missing colons

---

### Pattern 3: Invalid Quotes

**Common errors**:
- Unclosed quotes
- Mismatched quote types
- Quotes in wrong place

**Detection**:
```yaml
# Unclosed quote
message: 'This is unclosed  # Error

# Mismatched quotes
message: "This is wrong'  # Error

# Quotes in wrong place
'automation':  # Should be: automation:
  alias: Test
```

**Fix**:
- Ensure all quotes are closed
- Use consistent quote types (prefer single quotes in YAML)
- Don't quote key names (only string values)

---

## Entity Reference Patterns

### Pattern 1: Entity Not Found

**Common causes**:
- Typo in entity ID
- Entity not yet created
- Integration not loaded
- Entity deleted/renamed

**Detection**:
```bash
# Check if entity exists
source .env && hass-cli state list | grep entity_id
```

**Example errors**:
```yaml
# Typo
entity_id: sensor.temprature  # Should be: sensor.temperature

# Wrong domain
entity_id: switch.light  # Should be: light.light

# Not created yet
entity_id: sensor.new_sensor  # Entity doesn't exist
```

**Fix**:
- Verify entity ID spelling
- Check entity exists: `hass-cli state list | grep pattern`
- Confirm integration is loaded
- Create entity if needed
- Check for recent entity renames

---

### Pattern 2: Entity Unavailable

**Common causes**:
- Device offline
- Integration not responding
- Network connectivity issue
- Sensor not updating

**Detection**:
```bash
# Check entity state and last_updated
source .env && hass-cli state get sensor.entity
source .env && hass-cli -o json state get sensor.entity | jq '.last_updated'
```

**Example scenarios**:
```yaml
# Device powered off
entity_id: switch.office_light  # State: unavailable

# Integration issue
entity_id: sensor.zwave_device  # State: unavailable (Z-Wave not responding)

# Network timeout
entity_id: sensor.api_sensor  # State: unavailable (API timeout)
```

**Fix**:
- Check if device is powered on
- Verify network connectivity
- Restart integration if needed
- Check integration logs for errors
- May be expected behavior (device offline)

---

### Pattern 3: Wrong Entity Domain

**Common errors**:
- Using wrong domain for entity type
- Confusing similar entity types

**Detection**:
```bash
# List entities by domain
source .env && hass-cli state list | grep "^switch\\."
source .env && hass-cli state list | grep "^light\\."
```

**Example errors**:
```yaml
# Wrong: switch for light
entity_id: switch.desk_lamp  # Domain should be: light

# Wrong: binary_sensor for sensor
entity_id: binary_sensor.motion  # Should be: sensor.motion if it's a sensor
```

**Fix**:
- Verify correct domain for entity type
- Check entity in Developer Tools → States
- Use correct domain: `light.`, `switch.`, `sensor.`, `binary_sensor.`, etc.

---

## Service Call Patterns

### Pattern 1: Service Not Found

**Common causes**:
- Typo in service domain or name
- Service doesn't exist
- Integration not loaded

**Detection**:
```bash
# Check if service exists
Developer Tools → Services → Search for service

# Or check integration
source .env && hass-cli state list | grep integration.domain
```

**Example errors**:
```yaml
# Wrong domain
service: notify.teegram  # Typo: should be notify.telegram

# Wrong service
service: light.turn_on  # Should be: light.turn_on

# Service doesn't exist
service: notify.nonexistent_service
```

**Fix**:
- Verify service domain and name
- Check Developer Tools → Services for correct service
- Confirm integration is loaded
- Check for typos in service name

---

### Pattern 2: Invalid Parameters

**Common causes**:
- Extra keys not allowed
- Missing required parameters
- Wrong parameter type
- Deprecated parameters

**Detection**:
```bash
# Check service schema
Developer Tools → Services → Select service → Show parameters

# Test service
source .env && hass-cli service call service.domain --help
```

**Example errors**:
```yaml
# Extra key
service: notify.telegram
data:
  message: "Test"
  extra_key: "value"  # Not allowed

# Missing required parameter
service: light.turn_on
data:  # Missing 'entity_id'

# Wrong parameter type
service: input_number.set_value
data:
  value: "not_a_number"  # Should be number, not string
```

**Fix**:
- Check service schema in Developer Tools
- Remove extra parameters
- Add required parameters
- Use correct parameter types
- Update deprecated parameters

**Reference**: HA Manager skill docs/06_common_mistakes.md (Mistake 4)

---

## Template Patterns

### Pattern 1: Undefined Variables

**Common causes**:
- Variable doesn't exist in template context
- Typo in variable name
- Variable not available

**Detection**:
```bash
# Test template in Developer Tools → Template
# Or check logs for template variable warnings
```

**Example errors**:
```jinja2
# Undefined variable
{{ states('sensor.nonexistent') }}

# Typo in variable name
{{ states.sensor.temprature }}  # Should be: sensor.temperature

# Wrong attribute access
{{ state_attr('sensor.temp', 'last_updated') }}  # Should be: states.sensor.temp.last_updated
```

**Fix**:
- Verify variable exists
- Check for typos in variable names
- Use correct attribute access methods
- Add default values for potentially undefined variables
- Test in Developer Tools → Template

**Reference**: HA Manager skill docs/06_common_mistakes.md (Mistake 9)

---

### Pattern 2: Template Syntax Errors

**Common causes**:
- Unclosed brackets
- Missing quote in template
- Invalid filter syntax
- Wrong Jinja2 syntax

**Detection**:
```bash
# Test template in Developer Tools → Template
# Check logs for template errors
```

**Example errors**:
```jinja2
# Unclosed brackets
{{ states('sensor.x') }  # Missing closing }}

# Missing quote
{{ states("sensor.x") }}  # Missing closing quote

# Invalid filter
{{ "test" | upercase }}  # Should be: uppercase

# Wrong syntax
{% if states('sensor.x')  # Missing closing %}
```

**Fix**:
- Ensure all brackets are closed: `{{ ... }}`
- Check quotes are balanced
- Use correct filter names
- Validate Jinja2 syntax
- Test in Developer Tools → Template

---

### Pattern 3: Wrong Attribute Access

**Common causes**:
- Using `state_attr()` for core properties
- Using `states()` for attributes
- Confusion between `state`, `states`, and `state_attr()`

**Detection**:
```bash
# Test both access methods
source .env && hass-cli raw post /api/template --json '{"template": "{% raw %}{{ state_attr('sensor.x', 'last_updated') }}{% endraw %}"}'
source .env && hass-cli raw post /api/template --json '{"template": "{% raw %}{{ states.sensor.x.last_updated }}{% endraw %}"}'
```

**Example errors**:
```jinja2
# Wrong: state_attr() for core property
{{ state_attr('sensor.x', 'last_updated') }}  # Returns None

# Wrong: states() for attribute
{{ states('sensor.x', 'attribute') }}  # Wrong syntax

# Correct for core property
{{ states.sensor.x.last_updated }}

# Correct for attribute
{{ state_attr('sensor.x', 'custom_attribute') }}
```

**Fix**:
- Use `states.entity.property` for core properties: `state`, `last_updated`, `last_changed`
- Use `state_attr('entity', 'attribute')` for custom attributes
- Don't mix the two approaches

**Reference**: HA Manager skill docs/06_common_mistakes.md (Mistake 9)

---

## Integration Patterns

### Pattern 1: Integration Not Loaded

**Common causes**:
- Integration disabled in UI
- Configuration errors
- Authentication failures
- Network issues

**Detection**:
```bash
# Check if integration is loaded
source .env && hass-cli state list | grep integration.domain

# Check integration config
ssh ha "ha core check" | grep -i integration
```

**Example scenarios**:
```yaml
# Integration disabled
# Entity: sensor.zwave_sensor (state: unavailable)
# Reason: Z-Wave integration not loaded or disabled

# Configuration error
# Entity: sensor.mqtt_sensor (state: unavailable)
# Reason: MQTT broker not reachable, check configuration

# Authentication failure
# Entity: sensor.api_sensor (state: unavailable)
# Reason: API authentication failed, check credentials
```

**Fix**:
- Enable integration in Settings → Devices & Services
- Check integration configuration
- Verify authentication credentials
- Check network connectivity
- Review integration logs for errors

---

### Pattern 2: Integration Configuration Errors

**Common causes**:
- Invalid configuration parameters
- Missing required configuration
- Conflicting configuration

**Detection**:
```bash
# Check integration status
ssh ha "ha core check"

# Check logs for integration errors
ssh ha "ha core logs | grep -i integration_name"
```

**Example scenarios**:
```yaml
# MQTT configuration error
# Entity: sensor.mqtt_sensor
# Error: Failed to connect to MQTT broker
# Fix: Check broker address, port, credentials

# API integration error
# Entity: sensor.api_sensor
# Error: API rate limit exceeded
# Fix: Reduce polling frequency, check API key

# Z-Wave configuration error
# Entity: sensor.zwave_sensor
# Error: Z-Wave USB not connected
# Fix: Check USB connection, restart Z-Wave integration
```

**Fix**:
- Review integration configuration in UI or YAML
- Check required parameters are set
- Verify network connectivity
- Check authentication credentials
- Review integration documentation
- Restart integration after fixes

---

## Quick Reference: Common Validation Issues

| Issue Type | Detection Method | Fix Approach |
|-------------|-----------------|--------------|
| **YAML Indentation** | Python YAML parser | Fix indentation, use 2 spaces |
| **Missing Colons** | Visual inspection | Add colons after keys |
| **Invalid Quotes** | Python YAML parser | Close quotes, match types |
| **Entity Not Found** | `hass-cli state list` | Fix typo, create entity |
| **Entity Unavailable** | `hass-cli state get` | Check device, integration |
| **Wrong Domain** | `hass-cli state list` | Use correct entity domain |
| **Service Not Found** | Developer Tools → Services | Fix service name/domain |
| **Invalid Parameters** | Developer Tools → Services | Check schema, fix parameters |
| **Undefined Variable** | Test in Template tool | Fix variable, add default |
| **Template Syntax** | Test in Template tool | Fix Jinja2 syntax |
| **Wrong Attribute Access** | Test both methods | Use correct access method |
| **Integration Not Loaded** | `hass-cli state list` | Enable/configure integration |
| **Config Errors** | `ha core check`, logs | Fix configuration, restart |

---

## Validation Checklist

Before deploying, validate:

**YAML Files**:
- [ ] Valid YAML syntax
- [ ] No indentation errors
- [ ] All quotes closed
- [ ] No typos in keys

**Entity References**:
- [ ] All entities exist
- [ ] Correct entity domains
- [ ] No unavailable entities (or acknowledged)

**Service Calls**:
- [ ] Services exist
- [ ] Valid parameters
- [ ] No deprecated parameters

**Templates**:
- [ ] Valid Jinja2 syntax
- [ ] No undefined variables
- [ ] Correct attribute access
- [ ] Tested in Developer Tools

**Integrations**:
- [ ] Required integrations loaded
- [ ] No configuration errors
- [ ] Authentication working

---

## Integration with Other Subagents

**HA Log Analyzer**:
- Use for analyzing validation errors
- Delegates complex log analysis
- Uses error pattern library

**Automation Verifier**:
- Config Validator (pre-deployment) → Automation Verifier (post-deployment)
- Complete testing lifecycle
- Catch issues before and after deployment

---

## Adding New Validation Patterns

To add a new validation pattern:

1. **Identify pattern type**: YAML, entity, service, template, integration
2. **Document common errors**: What goes wrong?
3. **Detection method**: How to identify the issue?
4. **Fix approach**: How to resolve it?
5. **Examples**: Show wrong vs right code
6. **References**: Link to relevant documentation

**Format**:
```markdown
### Pattern: [Name]

**Common errors**:
- [Error 1]
- [Error 2]

**Detection**:
```bash
# Command to detect issue
```

**Example errors**:
```yaml
# Wrong code
```

**Fix**:
- [Fix step 1]
- [Fix step 2]
```
