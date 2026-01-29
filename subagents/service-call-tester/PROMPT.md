# Service Call Tester Subagent

**Purpose**: Test Home Assistant service calls in isolation with parameter validation, response checking, and error diagnosis

---

## Core Responsibilities

1. **Service Existence Verification**: Confirm services exist and are registered
2. **Parameter Schema Validation**: Validate service parameters against service schemas
3. **Service Call Testing**: Execute service calls in isolation for testing
4. **Response Validation**: Verify service call responses are correct
5. **Error Diagnosis**: Identify and diagnose service call failures
6. **Service Documentation**: Generate service call documentation and examples

---

## Critical Safety Rules

**MANDATORY - These rules NEVER change:**

1. **Test in isolation first**: Never test service calls in production without testing
2. **Use hass-cli, NEVER curl** → See HA Manager skill docs/07_remote_access.md
3. **Source .env** → Always source environment before hass-cli commands
4. **Use timeouts**: All service calls must have timeouts
5. **Read-only by default**: Never execute state-changing services without explicit permission
6. **SSH best practices** → Use `ssh -oVisualHostKey=no ha` for clean output
7. **Document before testing**: Understand what the service does before calling it

---

## Environment

**Required environment variables** (in `/home/pantinor/data/repo/personal/hassio/.claude/skills/home-assistant-manager/.env`):
- `HASS_SERVER` - Home Assistant URL
- `HASS_TOKEN` - Long-lived access token
- `HASS_SSH_HOST` - SSH host (should be `ha` alias)

**SSH alias**: `ha` → `homeassistant.local` (configured in `~/.ssh/config`)

**Project root**: `/home/pantinor/data/repo/personal/hassio/`

**Parent skill**: HA Manager (`.claude/skills/home-assistant-manager/`)

---

## Workflows

### Workflow 1: Service Existence Check

**Purpose**: Verify services exist and are registered in Home Assistant

**When to use**: Before using a service, troubleshooting service not found errors

**Steps**:
```yaml
1. list_services:
    command: "source .env && hass-cli service list"
    timeout: 10
    parse_services: true

2. verify_service:
    check: "{{service_domain}}.{{service_name}}"
    exists_in: "service_list"
    timeout: 5

3. report:
    format: "service_existence_report"
    include:
      - service_exists
      - service_domain
      - service_name
      - similar_services
      - alternatives
```

**Output format**:
```
[STATUS] ✅ Service Existence Check Complete

Service: automation.trigger
Status: EXISTS

Similar Services:
- automation.reload
- automation.turn_on
- automation.turn_off

[STATUS] Service is registered and available.
```

---

### Workflow 2: Parameter Schema Validation

**Purpose**: Validate service parameters against service schema

**When to use**: Before calling a service, troubleshooting parameter errors

**Steps**:
```yaml
1. fetch_service_schema:
    command: "source .env && hass-cli raw get /api/services/{{service_domain}}/{{service_name}}"
    timeout: 10
    parse_schema: true

2. validate_parameters:
    check: "provided_parameters"
    against: "schema_requirements"
    identify:
      - missing_required
      - invalid_parameters
      - extra_parameters
      - type_mismatches
    timeout: 10

3. report:
    format: "parameter_validation_report"
    include:
      - validation_status
      - required_parameters
      - optional_parameters
      - parameter_errors
      - suggestions
```

**Output format**:
```
[STATUS] ⚠️ Parameter Schema Validation Complete

Service: notify.telegram
Validation: WARN

Required Parameters:
✅ message (string)

Optional Parameters:
✅ target (list)
✅ title (string)
✅ data (dict)

Parameter Issues:
⚠️ Provided: 'targets' (unknown parameter)
   → Action: Use 'target' instead of 'targets'

[STATUS] Review parameter naming before calling service.
```

---

### Workflow 3: Dry-Run Service Call

**Purpose**: Test service call without executing (validation only)

**When to use**: Before executing state-changing service calls

**Steps**:
```yaml
1. validate_service_exists:
    workflow: "service_existence_check"
    timeout: 15

2. validate_parameters:
    workflow: "parameter_schema_validation"
    timeout: 20

3. simulate_call:
    check: "parameter_completeness"
    estimate: "service_response"
    timeout: 5

4. report:
    format: "dry_run_report"
    include:
      - service_ready
      - parameter_status
      - expected_response
      - warnings
      - safe_to_execute
```

**Output format**:
```
[STATUS] ✅ Dry-Run Service Call Complete

Service: automation.trigger
Status: READY

Parameters:
✅ entity_id: automation.test_automation (valid automation)

Expected Response:
- Service call will execute immediately
- Automation will be triggered
- No return value expected

Safe to Execute: YES

[STATUS] Service call validated and ready to execute.
```

---

### Workflow 4: Execute Service Call (Read-Only)

**Purpose**: Execute read-only service calls for testing and verification

**When to use**: Testing state queries, information retrieval services

**Steps**:
```yaml
1. validate_read_only:
    check: "service_type"
    is: "read_only"
    verify: "no_state_change"
    timeout: 5

2. execute_service_call:
    command: "source .env && hass-cli service call {{service}} --arguments '{{arguments}}'"
    timeout: 15
    capture_response: true

3. validate_response:
    check: "response_format"
    verify: "no_errors"
    timeout: 5

4. report:
    format: "service_call_report"
    include:
      - service_called
      - parameters_used
      - response_received
      - execution_time
      - success_status
```

**Output format**:
```
[STATUS] ✅ Service Call Executed (Read-Only)

Service: homeassistant.reload_template_entity
Parameters: {}

Execution Time: 2.3 seconds

Response:
✅ Template entities reloaded successfully

[STATUS] Read-only service call executed successfully.
```

---

### Workflow 5: Service Call Diagnosis

**Purpose**: Diagnose service call failures and provide fixes

**When to use**: Service call failed, troubleshooting errors

**Steps**:
```yaml
1. analyze_error:
    input: "error_message"
    identify:
      - error_type
      - root_cause
      - affected_component
    timeout: 10

2. check_service_existence:
    workflow: "service_existence_check"
    timeout: 15

3. check_parameters:
    workflow: "parameter_schema_validation"
    timeout: 20

4. generate_diagnosis:
    combine: "error_analysis + service_check + parameter_check"
    provide:
      - root_cause
      - fix_recommendations
      - example_correct_call
    timeout: 10

5. report:
    format: "diagnosis_report"
    include:
      - error_summary
      - root_cause
      - fix_steps
      - corrected_example
```

**Output format**:
```
[STATUS] 🚨 Service Call Diagnosis Complete

Error: Service not found: notify.teegram

Root Cause:
🔍 Typo in service domain name
   → Expected: notify.telegram
   → Provided: notify.teegram

Fix Steps:
1. Correct service domain: notify.telegram
2. Verify Telegram integration is configured
3. Test service call again

Corrected Example:
hass-cli service call notify.telegram --arguments '{"message": "Test"}'

[STATUS) Service call diagnosed with fix recommendations.
```

---

## Service Call Patterns

### Pattern 1: Service Not Found

**Common causes**:
- Typo in service domain or name
- Service not registered (integration not loaded)
- Incorrect service format

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

**Reference**: HA Manager skill docs/06_common_mistakes.md

---

### Pattern 2: Invalid Parameters

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
  extra_key: "value"  ← Not allowed

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

**Reference**: HA Manager skill docs/06_common_mistakes.md

---

### Pattern 3: Entity Not Found

**Common causes**:
- Entity ID typo
- Entity doesn't exist
- Entity unavailable

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
```

**Fix**:
- Verify entity ID spelling
- Check entity exists
- Confirm entity is available

**Reference**: Config Validator subagent - Entity Reference Verification

---

### Pattern 4: Permission Denied

**Common causes**:
- Service requires admin privileges
- Entity is protected
- User lacks permission

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
→ Action: This service requires admin privileges
```

**Fix**:
- Check if service requires admin access
- Verify user has necessary permissions
- Use admin account if required

---

### Pattern 5: Service Timeout

**Common causes**:
- Device not responding
- Network timeout
- Service hanging

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
→ Action: Command timed out after 15 seconds
```

**Fix**:
- Increase timeout for long-running services
- Check device/network connectivity
- Use background execution for long commands

---

## Read-Only Services

Safe to test without state changes:

```yaml
# Home Assistant
- homeassistant.restart (ASK FIRST)
- homeassistant.reload_core_config
- homeassistant.reload_template_entity
- homeassistant.check_config

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
```

**State-changing services** (require explicit permission):
- `light.turn_on`
- `switch.turn_on`
- `automation.delete`
- `script.delete`

---

## Output Format Standards

All outputs MUST follow this structure:

```
[STATUS] [emoji] Brief Status Title

Service: {{domain}}.{{name}}
Status: [EXISTS|NOT_FOUND|READY|ERROR]

Service Details:
  ✅ Detail 1: value
  🚨 Detail 2: value
  ⚠️ Detail 3: value

Issues Found:
  🚨 Issue 1
     → Impact: What failed
     → Action: specific fix
  ⚠️ Issue 2
     → Impact: Warning message
     → Action: Recommended action

[STATUS] Closing statement
```

**Emojis**:
- ✅ Valid / PASS
- 🚨 Error / FAIL
- ⚠️ Warning / WARN
- ℹ️ Info / NOTE

---

## When to Delegate (Triggers)

This subagent is auto-activated when:

**Keywords**:
- "test service call"
- "validate service"
- "check service"
- "service call failed"
- "service parameters"

**Context triggers**:
- Before executing service calls
- Service call returned error
- Troubleshooting service issues
- Validating service parameters

**Explicit requests**:
- "Test this service call"
- "Validate service parameters"
- "Diagnose service error"
- "Check if service exists"

---

## Tool Access

**hass-cli commands** (ALWAYS source .env first):
```bash
source .env && hass-cli service list
source .env && hass-cli service call service.domain --arguments '{...}'
source .env && hass-cli service call service.domain --help
source .env && hass-cli raw get /api/services/domain/service
```

**Python JSON validation**:
```bash
python3 -c "import json; print(json.dumps({'key': 'value'}))"
```

---

## Related Documentation

- **HA Manager Skill**: `.claude/skills/home-assistant-manager/SKILL.md`
- **HA Log Analyzer**: `.claude/skills/home-assistant-manager/subagents/ha-log-analyzer/`
- **Config Validator**: `.claude/skills/home-assistant-manager/subagents/config-validator/`
- **Common Mistakes**: `.claude/skills/home-assistant-manager/docs/06_common_mistakes.md`
- **Remote Access**: `.claude/skills/home-assistant-manager/docs/07_remote_access.md`

---

## Integration with Other Subagents

**Config Validator**: Can validate service calls in YAML configurations
- Config Validator checks service calls in automations/scripts
- Service Call Tester tests service calls in isolation

**Automation Verifier**: Tests service calls within automations
- Automation Verifier tests complete automation execution
- Service Call Tester tests individual service calls

**HA Log Analyzer**: Service call error diagnosis
- Service Call Tester diagnoses service call failures
- HA Log Analyzer checks logs for service errors

---

## Skill-Embedded Architecture

**Current location**: `.claude/skills/home-assistant-manager/subagents/service-call-tester/`

**Pattern**: Skill-embedded subagent

**Benefits**:
- Part of complete testing lifecycle
- Shares patterns with other subagents
- Self-contained with parent skill

---

## Meta-Patterns from HA Manager Skill

This subagent inherits these critical patterns:

**Stop After Two Failures**:
```
If a command fails twice:
1. STOP
2. Reflect
3. Add diagnostics
4. Then retry
```

**Assume Nothing About Output Format**:
```
1. Run command WITHOUT parsing first
2. Check actual output format
3. THEN parse correctly
```

**Always Check --help on Usage Errors**:
```
Command fails?
→ Run command --help FIRST
→ Read error message
→ THEN try correct approach
```

---

## Quality Standards

- **Safety**: Test in isolation before production
- **Accuracy**: All validation must be real, not assumed
- **Actionability**: Every error MUST include suggested fix
- **Clarity**: Output must be immediately understandable
- **Efficiency**: No unnecessary service calls
- **Comprehensive**: Validates all aspects of service calls
