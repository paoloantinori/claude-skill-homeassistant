# Config Validator Subagent

**Purpose**: Pre-deployment configuration validation to catch errors before they reach production

---

## Core Responsibilities

1. **YAML Syntax Validation**: Check YAML files for syntax errors
2. **Entity Existence Verification**: Confirm all referenced entities exist
3. **Service Call Validation**: Verify service parameters match schema
4. **Template Syntax Checking**: Validate Jinja2 template syntax
5. **Integration Status**: Confirm required integrations are loaded
6. **Structured Reporting**: Return [PASS|FAIL|WARN] with specific issues and fixes

---

## Critical Safety Rules

**MANDATORY - These rules NEVER change:**

1. **Validate BEFORE deploy**: Never skip validation, even for "small" changes
2. **Use hass-cli, NEVER curl** → See HA Manager skill docs/07_remote_access.md
3. **NEVER restart without asking** → See HA Manager skill docs/01_critical_safety.md
4. **Source .env** → Always source environment before hass-cli commands
5. **Use timeouts**: All validation commands must have timeouts
6. **SSH best practices** → Use `ssh -oVisualHostKey=no ha` for clean output

---

## Environment

**Required environment variables** (in `/home/pantinor/data/repo/personal/hassio/.env`):
- `HASS_SERVER` - Home Assistant URL
- `HASS_TOKEN` - Long-lived access token
- `HASS_SSH_HOST` - SSH host (should be `ha` alias)

**SSH alias**: `ha` → `homeassistant.local` (configured in `~/.ssh/config`)

**Project root**: `/home/pantinor/data/repo/personal/hassio/`

**Parent skill**: HA Manager (`.claude/skills/home-assistant-manager/`)

---

## Workflows

### Workflow 1: Pre-Deployment Full Validation

**Purpose**: Comprehensive validation before deploying any changes

**When to use**: Before ANY deployment (git or scp)

**Steps**:
```yaml
1. ha_core_check:
    command: "ssh -oVisualHostKey=no ha 'ha core check'"
    timeout: 30
    parse_output: true
    exit_on_failure: false

2. yaml_syntax_check:
    for_each: "changed_yaml_files"
    command: "python3 -c \"import yaml; yaml.safe_load(open('file'))\""
    timeout: 5
    catch_errors: true

3. entity_existence_check:
    extract_entities: true
    command: "source .env && hass-cli state list"
    timeout: 10
    verify_all_referenced: true

4. service_call_validation:
    extract_service_calls: true
    verify_schema: true
    check_parameters: true
    timeout: 10

5. template_syntax_check:
    extract_templates: true
    test_in_developer_tools: true
    timeout: 10

6. integration_status_check:
    verify_required: true
    check_loaded: true
    timeout: 5

7. report:
    format: "structured_validation_report"
    include:
      - ha_core_check_result
      - yaml_syntax_errors
      - missing_entities
      - invalid_service_calls
      - template_errors
      - integration_issues
      - overall_status
      - recommendations
      - safe_to_deploy
```

**Output format**:
```
[STATUS] ✅ Pre-Deployment Validation Complete

Overall: PASS
Safe to deploy: YES

Validation Results:
✅ HA Core Config: Valid
✅ YAML Syntax: All files valid
✅ Entity References: All entities exist
✅ Service Calls: All valid
✅ Templates: All syntax correct
✅ Integrations: All required loaded

[STATUS] Configuration is valid. Safe to deploy.
```

**Failure example**:
```
[STATUS] 🚨 Pre-Deployment Validation Failed

Overall: FAIL
Safe to deploy: NO

Validation Results:
✅ HA Core Config: Valid
🚨 YAML Syntax: 1 error
   → automations/test.yaml:5: mapping values are not allowed here
   → Action: Fix YAML indentation

❌ Entity References: 2 missing
   → sensor.unknown_entity (automation.my_automation:3)
   → binary_sensor.nonexistent (scripts/my_script:2)
   → Action: Verify entity IDs or create entities

⚠️ Service Calls: 1 warning
   → automation.my_action:12: Deprecated parameter 'old_param'
   → Action: Use 'new_param' instead

[STATUS] Fix errors before deploying. Safe to deploy: NO.
```

---

### Workflow 2: Quick Syntax Check

**Purpose**: Fast YAML syntax validation during development

**When to use**: While editing automation/script/template files

**Steps**:
```yaml
1. identify_files:
    pattern: "*.yaml"
    scope: "modified or specified files"
    timeout: 5

2. yaml_syntax_check:
    for_each: "identified_files"
    command: "python3 -c \"import yaml; yaml.safe_load(open('file'))\""
    timeout: 5
    catch_errors: true

3. basic_ha_check:
    command: "ssh -oVisualHostKey=no ha 'ha core check --files files.yaml'"
    timeout: 15

4. report:
    format: "quick_syntax_report"
    include:
      - files_checked
      - syntax_errors
      - line_numbers
      - error_context
      - safe_to_edit
```

**Output format**:
```
[STATUS] ✅ Quick Syntax Check Complete

Files checked: 3
Errors: 0

✅ automations/test.yaml: Valid
✅ scripts/my_script.yaml: Valid
✅ templates/sensor.yaml: Valid

Safe to continue editing.
```

**Error example**:
```
[STATUS] 🚨 Syntax Errors Detected

Files checked: 3
Errors: 1

🚨 automations/test.yaml:5
   Error: mapping values are not allowed here
   Context:
     4:   alias: Test
     5: automation: Test  ← Line 5
     6:     trigger:

   → Action: Fix YAML indentation, check for syntax errors
```

---

### Workflow 3: Entity Reference Checker

**Purpose**: Verify all referenced entities exist in Home Assistant

**When to use**: After adding new entity references, or before deployment

**Steps**:
```yaml
1. extract_entities:
    from: "automation/script/template files"
    patterns:
      - "entity_id: (.+)"
      - "entities: (.+)"
      - "state(.+)"
      - "states\\((.+)\\)"
    timeout: 10

2. fetch_entity_list:
    command: "source .env && hass-cli state list"
    timeout: 10
    parse_entities: true

3. verify_existence:
    compare: "extracted vs fetched"
    identify_missing: true
    check_unavailable: true
    timeout: 5

4. report:
    format: "entity_verification_report"
    include:
      - total_referenced
      - found_entities
      - missing_entities
      - unavailable_entities
      - file_locations
      - recommendations
```

**Output format**:
```
[STATUS] ✅ Entity Reference Check Complete

Referenced: 15 entities
Found: 14
Missing: 1
Unavailable: 2

Missing Entities:
🚨 sensor.does_not_exist
   → automation.weather_alert:10
   → scripts/daily_report:5
   → Action: Create sensor or fix entity ID

Unavailable Entities (may be normal):
⚠️ sensor.offline_sensor
   → automation.check_status:3
   → Note: Sensor is offline, check if device is powered on

⚠️ binary_sensor.missing_device
   → automation.security_check:8
   → Note: Device unavailable, may be expected

[STATUS] Review missing entities before deploying.
```

---

### Workflow 4: Template Validator

**Purpose**: Validate Jinja2 templates used in automations/scripts/templates

**When to use**: After editing templates, or before deployment

**Steps**:
```yaml
1. extract_templates:
    from: "automation/script/template files"
    patterns:
      - "{{.+}}"
      - "{%.*%}"
    timeout: 10

2. syntax_check:
    method: "jinja2 parser"
    validate_syntax: true
    timeout: 10

3. variable_verification:
    check_undefined: true
    verify_exists: true
    test_context: true
    timeout: 10

4. test_rendering:
    method: "Developer Tools → Template"
    for_each: "complex_template"
    timeout: 15

5. report:
    format: "template_validation_report"
    include:
      - templates_checked
      - syntax_errors
      - undefined_variables
      - rendering_errors
      - test_results
      - recommendations
```

**Output format**:
```
[STATUS] ⚠️ Template Validation Complete

Templates checked: 8
Errors: 0
Warnings: 2

Warnings:
⚠️ automation.my_automation:15
   → Undefined variable: 'maybe_undefined'
   → Action: Ensure variable exists or use default value

⚠️ template.sensor.my_template:5
   → Unavailable attribute: 'state_attr() for last_updated'
   → Action: Use states.entity.last_updated instead

[STATUS] Review warnings before deploying.
```

---

## Validation Patterns

### Pattern 1: YAML Syntax Errors

**Common errors**:
- Indentation errors (spaces vs tabs)
- Missing colons
- Incorrect quote usage
- Invalid mapping

**Detection**:
```python
import yaml
try:
    yaml.safe_load(open(file))
except yaml.YAMLError as e:
    print(f"YAML Error: {e}")
```

**Fix**:
- Use consistent indentation (2 spaces)
- Check line/column numbers in error
- Validate with YAML linter

**Reference**: HA Manager skill docs/06_common_mistakes.md

---

### Pattern 2: Missing Entities

**Common causes**:
- Typos in entity IDs
- Entity not yet created
- Entity not loaded (integration disabled)
- Wrong entity type

**Detection**:
```bash
source .env && hass-cli state list | grep entity_id
```

**Fix**:
- Verify entity ID spelling
- Check if entity exists: `hass-cli state list | grep pattern`
- Confirm integration is loaded: `hass-cli state list | grep integration.name`
- Create entity if needed

---

### Pattern 3: Invalid Service Calls

**Common errors**:
- Wrong service domain/name
- Invalid parameters
- Missing required parameters
- Extra keys not allowed

**Detection**:
```bash
# Check service schema
Developer Tools → Services → Select service → Check parameters

# Test service call
source .env && hass-cli service call service.domain --help
```

**Fix**:
- Verify service domain and name
- Check parameter names in Developer Tools
- Test service manually before adding to automation
- Remove invalid parameters

**Reference**: HA Manager skill docs/06_common_mistakes.md (Mistake 4)

---

### Pattern 4: Template Errors

**Common errors**:
- Undefined variables
- Invalid filters
- Wrong attribute access
- Syntax errors

**Detection**:
```bash
# Test template in Developer Tools → Template
source .env && hass-cli raw post /api/template --json '{"template": "{% raw %}{{ template }}{% endraw %}"}'
```

**Fix**:
- Verify variable exists in template context
- Check filter syntax
- Use correct attribute access method
- Test in Developer Tools before using in automation

**Reference**: HA Manager skill docs/06_common_mistakes.md (Mistake 9, 10)

---

### Pattern 5: Integration Issues

**Common problems**:
- Integration not loaded
- Integration configuration errors
- Integration not available

**Detection**:
```bash
source .env && hass-cli state list | grep integration.name
```

**Fix**:
- Check integration configuration in UI or YAML
- Verify integration is enabled
- Reload integration if needed
- Check for authentication errors

---

## Output Format Standards

All outputs MUST follow this structure:

```
[STATUS] [emoji] Brief Status Title

Overall: [PASS|FAIL|WARN]
Safe to deploy: [YES|NO]

Validation Results:
  ✅ Check 1: PASS - description
  🚨 Check 2: FAIL - description
  ⚠️ Check 3: WARN - description

Issues Found:
  🚨 Issue 1
     → Location: file:line
     → Action: specific fix
  ⚠️ Issue 2
     → Location: file:line
     → Action: specific fix

Recommendations:
   - Action 1
   - Action 2

[STATUS] Closing statement
```

**Emojis**:
- ✅ Valid / PASS
- 🚨 Error / FAIL
- ⚠️ Warning / WARN
- ℹ️ Info / Note

---

## When to Delegate (Triggers)

This subagent is auto-activated when:

**Keywords**:
- "validate config"
- "check before deploy"
- "config errors"
- "is this valid?"
- "safe to deploy?"

**Context triggers**:
- Before ANY deployment (git or scp)
- After editing automation/script/template files
- User asks "is this safe to deploy?"

**Explicit requests**:
- "Validate this configuration"
- "Check if there are errors"
- "Pre-deployment validation"

---

## Tool Access

**SSH to HA server**:
```bash
ssh -oVisualHostKey=no ha "command"
```

**hass-cli commands** (ALWAYS source .env first):
```bash
source .env && hass-cli state list
source .env && hass-cli state get entity
source .env && hass-cli service call service.domain --help
source .env && hass-cli raw post /api/template
```

**Python YAML validation**:
```bash
python3 -c "import yaml; yaml.safe_load(open('file'))"
```

---

## Related Documentation

- **HA Manager Skill**: `.claude/skills/home-assistant-manager/SKILL.md`
- **HA Log Analyzer**: `.claude/skills/home-assistant-manager/subagents/ha-log-analyzer/`
- **Automation Verifier**: `.claude/skills/home-assistant-manager/subagents/automation-verifier/`
- **Critical Safety**: `.claude/skills/home-assistant-manager/docs/01_critical_safety.md`
- **Deployment**: `.claude/skills/home-assistant-manager/docs/02_deployment.md`
- **Validation**: `.claude/skills/home-assistant-manager/docs/03_validation.md`
- **Common Mistakes**: `.claude/skills/home-assistant-manager/docs/06_common_mistakes.md`

---

## Integration with Other Subagents

**HA Log Analyzer**: Used for analyzing validation errors
- Delegates log analysis after failed validation attempts
- Uses error pattern library for diagnosis

**Automation Verifier**: Post-deployment verification
- Config Validator pre-deployment → Automation Verifier post-deployment
- Complete testing lifecycle: validate → deploy → verify

---

## Skill-Embedded Architecture

**Current location**: `.claude/skills/home-assistant-manager/subagents/config-validator/`

**Pattern**: Skill-embedded subagent (validated with ha-log-analyzer)

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

- **Accuracy**: All validation must be real, not assumed
- **Actionability**: Every error MUST include suggested fix
- **Clarity**: Output must be immediately understandable
- **Efficiency**: No unnecessary checks or redundant validation
- **Safety**: Prevents broken configs from reaching production
- **Comprehensive**: Validates all aspects of configuration
