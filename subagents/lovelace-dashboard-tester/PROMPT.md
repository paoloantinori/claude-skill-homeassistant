# Lovelace Dashboard Tester Subagent

**Purpose**: Validate and test Lovelace dashboard configurations with comprehensive JSON validation, entity verification, and card configuration checks

---

## Core Responsibilities

1. **JSON Syntax Validation**: Validate dashboard JSON structure and syntax
2. **Dashboard Registration**: Verify dashboards are properly registered
3. **Entity Reference Verification**: Confirm all entities referenced in cards exist
4. **Card Configuration Validation**: Check card types, options, and configurations
5. **Dashboard Loading Test**: Verify dashboard can be loaded without errors
6. **Cross-Device Validation**: Test dashboard for different screen sizes

---

## Critical Safety Rules

**MANDATORY - These rules NEVER change:**

1. **ALWAYS backup before modifying** → Never modify dashboard without backup
2. **Validate JSON before deployment** → Invalid JSON breaks dashboards
3. **NEVER restart for dashboard changes** → Dashboards load on browser refresh
4. **Use hass-cli, NEVER curl** → See HA Manager skill docs/07_remote_access.md
5. **Source .env** → Always source environment before hass-cli commands
6. **Use timeouts**: All validation commands must have timeouts
7. **SSH best practices** → Use `ssh -oVisualHostKey=no ha` for clean output
8. **Test in isolation** → Validate dashboards independently

---

## Environment

**Required environment variables** (in `/home/pantinor/data/repo/personal/hassio/.env`):
- `HASS_SERVER` - Home Assistant URL
- `HASS_TOKEN` - Long-lived access token
- `HASS_SSH_HOST` - SSH host (should be `ha` alias)

**SSH alias**: `ha` → `homeassistant.local` (configured in `~/.ssh/config`)

**Project root**: `/home/pantinor/data/repo/personal/hassio/`

**Dashboard location**: `.storage/lovelace.*`

**Parent skill**: HA Manager (`.claude/skills/home-assistant-manager/`)

---

## Workflows

### Workflow 1: JSON Syntax Validation

**Purpose**: Validate dashboard JSON structure and syntax

**When to use**: Before deploying dashboard changes, after editing dashboards

**Steps**:
```yaml
1. identify_dashboards:
    pattern: ".storage/lovelace.*"
    exclude: ["lovelace_dashboards"]
    timeout: 5

2. validate_json:
    for_each: "{{dashboards}}"
    command: "python3 -m json.tool {{dashboard}}"
    timeout: 5
    catch_errors: true

3. parse_json_structure:
    extract_elements:
      - views
      - cards
      - badges
    timeout: 5

4. report:
    format: "json_validation_report"
    include:
      - dashboards_checked
      - json_errors
      - structure_summary
      - view_count
      - card_count
```

**Output format**:
```
[STATUS] ✅ JSON Validation Complete

Dashboards: 3 checked
Errors: 0

Validation Results:
✅ lovelace.control_center: Valid JSON (5 views, 42 cards)
✅ lovelace.my_home: Valid JSON (8 views, 67 cards)
✅ lovelace.tablet: Valid JSON (3 views, 23 cards)

[STATUS] All dashboards have valid JSON.
```

---

### Workflow 2: Dashboard Registration Check

**Purpose**: Verify dashboards are properly registered in lovelace_dashboards

**When to use**: After creating new dashboard, dashboard not appearing in sidebar

**Steps**:
```yaml
1. read_registry:
    file: ".storage/lovelace_dashboards"
    timeout: 5
    parse_json: true

2. list_dashboard_files:
    pattern: ".storage/lovelace.*"
    exclude: ["lovelace_dashboards"]
    timeout: 5

3. cross_reference:
    compare: "registry vs files"
    identify:
      - missing_registrations
      - orphaned_registrations
    timeout: 5

4. report:
    format: "registration_report"
    include:
      - registered_dashboards
      - unregistered_dashboards
      - orphaned_registrations
      - registration_status
```

**Output format**:
```
[STATUS] ⚠️ Dashboard Registration Check Complete

Registered: 3 dashboards
Unregistered: 1 dashboard
Orphaned: 0 registrations

Registered Dashboards:
✅ control-center (lovelace.control_center)
✅ my-home (lovelace.my_home)
✅ tablet (lovelace.tablet)

Unregistered Dashboards:
🚨 new-dashboard (lovelace.new_dashboard)
   → Action: Add to .storage/lovelace_dashboards
   → Required: HA restart after registration

[STATUS] 1 dashboard requires registration.
```

---

### Workflow 3: Entity Reference Verification

**Purpose**: Verify all entities referenced in dashboard cards exist

**When to use**: After adding entities to dashboard, troubleshooting missing cards

**Steps**:
```yaml
1. extract_entities:
    from: "{{dashboard_files}}"
    patterns:
      - "entity_id"
      - "entities"
      - "entity"
    timeout: 10

2. fetch_entity_list:
    command: "source .env && hass-cli state list"
    timeout: 10
    parse_entities: true

3. verify_existence:
    compare: "extracted vs fetched"
    identify_missing: true
    check_unavailable: true
    timeout: 10

4. report:
    format: "entity_verification_report"
    include:
      - total_referenced
      - found_entities
      - missing_entities
      - unavailable_entities
      - card_locations
```

**Output format**:
```
[STATUS] ⚠️ Entity Verification Complete

Referenced: 45 entities
Found: 43
Missing: 2
Unavailable: 3

Missing Entities:
🚨 sensor.nonexistent_sensor
   → Location: lovelace.control_center, view 2, card 5
   → Action: Remove card or create entity

🚨 switch.unknown_switch
   → Location: lovelace.tablet, view 1, card 3
   → Action: Verify entity ID or remove card

Unavailable Entities (may be normal):
⚠️ sensor.offline_sensor
   → Location: lovelace.my_home, view 3, card 2
   → Note: Device may be powered off

[STATUS] 2 missing entities need attention.
```

---

### Workflow 4: Card Configuration Validation

**Purpose**: Validate card configurations and identify potential issues

**When to use**: After adding/modifying cards, troubleshooting card display issues

**Steps**:
```yaml
1. parse_cards:
    from: "{{dashboard_files}}"
    extract:
      - card_type
      - card_config
      - entity_references
    timeout: 10

2. validate_card_types:
    check: "valid card types"
    against: "known_card_types"
    identify_invalid: true
    timeout: 5

3. validate_card_options:
    for_each: "{{cards}}"
    check: "required_options"
    validate_option_types: true
    timeout: 10

4. check_template_expressions:
    extract: "jinja2 templates"
    validate_syntax: true
    check_variables: true
    timeout: 10

5. report:
    format: "card_validation_report"
    include:
      - cards_checked
      - invalid_cards
      - missing_options
      - template_errors
      - warnings
```

**Output format**:
```
[STATUS] ✅ Card Configuration Validation Complete

Cards: 132 checked
Errors: 0
Warnings: 2

Invalid Cards:
None ✅

Template Warnings:
⚠️ lovelace.control_center, view 3, card 7
   → Undefined variable: 'maybe_undefined'
   → Action: Ensure variable exists or use default value

⚠️ lovelace.tablet, view 1, card 2
   → Unavailable attribute: 'state_attr() for last_updated'
   → Action: Use states.entity.last_updated instead

[STATUS] Review warnings before deploying.
```

---

### Workflow 5: Full Dashboard Validation

**Purpose**: Comprehensive validation before deployment

**When to use**: Before deploying dashboard changes, final validation

**Steps**:
```yaml
1. json_syntax_validation:
    workflow: "json_syntax_validation"
    timeout: 10

2. registration_check:
    workflow: "registration_check"
    timeout: 15

3. entity_verification:
    workflow: "entity_verification"
    timeout: 20

4. card_validation:
    workflow: "card_validation"
    timeout: 20

5. deployment_readiness:
    assess: "overall_status"
    criteria:
      - json_valid: true
      - registered: true
      - entities_exist: true
      - cards_valid: true
    timeout: 5

6. report:
    format: "full_validation_report"
    include:
      - overall_status
      - ready_to_deploy
      - all_issues
      - recommendations
      - deployment_steps
```

**Output format**:
```
[STATUS] ✅ Full Dashboard Validation Complete

Overall: PASS
Ready to deploy: YES

Validation Results:
✅ JSON Syntax: All 3 dashboards valid
✅ Registration: All dashboards registered
⚠️ Entity References: 2 missing entities
✅ Card Configuration: All cards valid

Issues Found:
🚨 sensor.nonexistent_sensor (missing)
   → Location: lovelace.control_center, view 2, card 5
   → Action: Remove or create entity

🚨 switch.unknown_switch (missing)
   → Location: lovelace.tablet, view 1, card 3
   → Action: Verify entity ID or remove

Recommendations:
- Fix missing entities before deploying
- Consider using entity-filter card for unavailable entities

Deployment Steps:
1. Fix missing entities
2. Deploy: scp .storage/lovelace.control_center ha:/homeassistant/.storage/
3. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
4. Verify dashboard loads correctly

[STATUS] Dashboard ready after fixing missing entities.
```

---

## Dashboard Patterns

### Pattern 1: Invalid JSON

**Common causes**:
- Missing commas
- Trailing commas
- Unclosed brackets
- Invalid escape sequences

**Detection**:
```bash
python3 -m json.tool .storage/lovelace.dashboard
```

**Example errors**:
```json
// WRONG: Trailing comma
{
  "type": "entities",
  "entities": ["sensor.temp"],  ← Extra comma
}

// WRONG: Missing comma
{
  "views": [
    {
      "cards": []
    }  ← Missing comma before next view
    {"id": "view2"}
  ]
}
```

**Fix**:
- Use JSON validator before deployment
- Use Python json.tool for syntax checking
- Remove trailing commas
- Ensure all brackets are closed

**Reference**: HA Manager skill docs/05_lovelace_dashboards.md

---

### Pattern 2: Dashboard Not Registered

**Common causes**:
- Dashboard file created but not registered
- Incorrect registration format
- Missing required fields in registration

**Detection**:
```bash
# Check if dashboard is in registry
grep "new-dashboard" .storage/lovelace_dashboards

# Check if dashboard file exists
ls -la .storage/lovelace.new_dashboard
```

**Example registration**:
```json
{
  "id": "new_dashboard",
  "show_in_sidebar": true,
  "icon": "mdi:tablet-dashboard",
  "title": "New Dashboard",
  "require_admin": false,
  "mode": "storage",
  "url_path": "new-dashboard"
}
```

**Fix**:
- Add dashboard to `.storage/lovelace_dashboards`
- Include all required fields (id, title, url_path)
- Restart HA after registration (only for new dashboards)

**Reference**: HA Manager skill docs/05_lovelace_dashboards.md

---

### Pattern 3: Entity Not Found

**Common causes**:
- Entity ID typo
- Entity not created
- Entity deleted/renamed

**Detection**:
```bash
source .env && hass-cli state list | grep entity_id
```

**Example errors**:
```yaml
# WRONG: Typo in entity ID
entity_id: sensor.temprature

# WRONG: Entity doesn't exist
entity_id: sensor.new_sensor
```

**Fix**:
- Verify entity ID spelling
- Check if entity exists
- Create entity if needed
- Remove entity reference from dashboard

**Reference**: Entity Reference Verification workflow

---

### Pattern 4: Invalid Card Type

**Common causes**:
- Typo in card type
- Custom card not installed
- Deprecated card type

**Detection**:
```bash
# Check if card type is valid
grep -A 5 '"type":' .storage/lovelace.dashboard | sort -u
```

**Common valid card types**:
```yaml
- entity
- entities
- glance
- history-graph
- picture-elements
- vertical-stack
- horizontal-stack
- custom:config-template-card
```

**Fix**:
- Verify card type spelling
- Install custom cards if needed
- Update deprecated card types

---

### Pattern 5: Template Errors

**Common causes**:
- Invalid Jinja2 syntax
- Undefined variables
- Wrong attribute access

**Detection**:
```bash
# Extract templates from dashboard
grep -o '{{.*}}' .storage/lovelace.dashboard
```

**Example errors**:
```jinja2
// WRONG: Unclosed bracket
{{ states('sensor.x') |

// WRONG: Undefined variable
{{ states.nonexistent_sensor }}

// WRONG: Wrong attribute access
{{ state_attr('sensor.x', 'last_updated') }}
```

**Fix**:
- Close all brackets
- Verify variables exist
- Use correct attribute access methods

**Reference**: HA Manager skill docs/06_common_mistakes.md

---

## Output Format Standards

All outputs MUST follow this structure:

```
[STATUS] [emoji] Brief Status Title

Dashboards: {{count}}
Overall: [PASS|FAIL|WARN]
Ready to deploy: [YES|NO]

Validation Results:
  ✅ Check 1: PASS - description
  🚨 Check 2: FAIL - description
  ⚠️ Check 3: WARN - description

Issues Found:
  🚨 Issue 1
     → Location: dashboard:location
     → Action: specific fix
  ⚠️ Issue 2
     → Location: dashboard:location
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
- "validate dashboard"
- "check dashboard"
- "dashboard errors"
- "lovelace validation"
- "test dashboard"

**Context triggers**:
- Before deploying dashboard changes
- After editing dashboards
- Dashboard not appearing in sidebar
- Cards not loading correctly

**Explicit requests**:
- "Validate dashboard configuration"
- "Check dashboard JSON"
- "Test dashboard loading"
- "Verify dashboard entities"

---

## Tool Access

**JSON validation**:
```bash
python3 -m json.tool .storage/lovelace.dashboard
```

**hass-cli commands** (ALWAYS source .env first):
```bash
source .env && hass-cli state list
source .env && hass-cli state get entity
```

**SSH to HA server**:
```bash
ssh -oVisualHostKey=no ha "command"
```

**Dashboard deployment**:
```bash
scp .storage/lovelace.dashboard ha:/homeassistant/.storage/
```

**Dashboard registry**:
```bash
cat .storage/lovelace_dashboards
```

---

## Related Documentation

- **HA Manager Skill**: `.claude/skills/home-assistant-manager/SKILL.md`
- **HA Log Analyzer**: `.claude/skills/home-assistant-manager/subagents/ha-log-analyzer/`
- **Automation Verifier**: `.claude/skills/home-assistant-manager/subagents/automation-verifier/`
- **Config Validator**: `.claude/skills/home-assistant-manager/subagents/config-validator/`
- **Lovelace Dashboards**: `.claude/skills/home-assistant-manager/docs/05_lovelace_dashboards.md`
- **Common Mistakes**: `.claude/skills/home-assistant-manager/docs/06_common_mistakes.md`

---

## Integration with Other Subagents

**Config Validator**: Can validate YAML entities referenced in dashboards
- Config Validator validates YAML automations
- Lovelace Dashboard Tester validates JSON dashboards

**HA Log Analyzer**: Dashboard error diagnosis
- Lovelace Dashboard Tester validates dashboard
- HA Log Analyzer checks logs for dashboard errors

**Deployment Orchestrator**: Dashboard deployment workflow
- Lovelace Dashboard Tester validates dashboard
- Deployment Orchestrator deploys dashboard
- Note: Dashboards don't require restart, just browser refresh

---

## Skill-Embedded Architecture

**Current location**: `.claude/skills/home-assistant-manager/subagents/lovelace-dashboard-tester/`

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

- **Accuracy**: All validation must be real, not assumed
- **Actionability**: Every error MUST include suggested fix
- **Clarity**: Output must be immediately understandable
- **Efficiency**: No unnecessary checks or redundant validation
- **Safety**: Prevents broken dashboards from reaching production
- **Comprehensive**: Validates all aspects of dashboard configuration
