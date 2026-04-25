# Dashboard Patterns Library

**Purpose**: Known dashboard validation patterns with detection methods and fixes

---

## Pattern 1: Invalid JSON Syntax

**Common errors**:
- Missing commas between properties
- Trailing commas (after last property)
- Unclosed brackets or braces
- Invalid escape sequences in strings
- Unquoted property names
- Single quotes instead of double quotes

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
    }  ← Missing comma
    {"id": "view2"}
  ]
}

// WRONG: Single quotes
{
  'type': 'entities'  ← Should use double quotes
}

// WRONG: Unquoted property names
{
  type: "entities",  ← Property name should be quoted
}
```

**Fix**:
- Remove trailing commas
- Add commas between properties
- Close all brackets and braces
- Use double quotes for strings and property names
- Use valid escape sequences (\\ for backslash, \n for newline)

**Reference**: HA Manager skill docs/05_lovelace_dashboards.md

---

## Pattern 2: Dashboard Not Registered

**Common causes**:
- Dashboard file created but not added to registry
- Incorrect registration format
- Missing required fields in registration
- Duplicate registration IDs

**Detection**:
```bash
# Check if dashboard is in registry
grep "new_dashboard" .storage/lovelace_dashboards

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

**Common registration errors**:
```json
// WRONG: Missing required fields
{
  "id": "new_dashboard"
  // Missing: title, url_path
}

// WRONG: Duplicate ID
{
  "id": "my-home",  ← Already exists
  "title": "Another Dashboard"
}
```

**Fix**:
- Add dashboard to `.storage/lovelace_dashboards`
- Include all required fields: id, title, url_path
- Use unique ID for each dashboard
- Restart HA after registration (only for new dashboards)

**Reference**: HA Manager skill docs/05_lovelace_dashboards.md

---

## Pattern 3: Entity Not Found

**Common causes**:
- Typo in entity ID
- Entity not yet created
- Entity deleted or renamed
- Wrong entity domain
- Entity from unavailable integration

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

# WRONG: Wrong domain
entity_id: switch.light  ← Should be light.light

# WRONG: Entity from unavailable integration
entity_id: sensor.zwave_sensor  ← Z-Wave integration not loaded
```

**Fix**:
- Verify entity ID spelling
- Check entity exists: `hass-cli state list | grep pattern`
- Confirm integration is loaded
- Create entity if needed
- Remove entity reference from dashboard
- Use entity-filter card for unavailable entities

**Reference**: Entity Reference Verification workflow

---

## Pattern 4: Invalid Card Type

**Common causes**:
- Typo in card type
- Custom card not installed
- Using deprecated card type
- Case sensitivity issues

**Detection**:
```bash
# Extract card types from dashboard
grep -oP '"type":\s*"\K[^"]+' .storage/lovelace.dashboard | sort -u
```

**Common valid card types**:
```yaml
Standard cards:
  - entity
  - entities
  - glance
  - history-graph
  - picture-elements
  - picture-entity
  - picture-glance
  - state-switch
  - state-label
  - thermostat
  - vertical-stack
  - horizontal-stack
  - grid
  - markdown
  - sensor
  - gauge

Custom cards (require installation):
  - custom:config-template-card
  - custom:button-card
  - custom:mini-graph-card
  - custom:clock-weather-card
```

**Example errors**:
```yaml
# WRONG: Typo in card type
type: entitis  ← Should be "entities"

# WRONG: Deprecated card type
type: "custom:old-card"  ← Card no longer available

# WRONG: Case sensitivity
type: "Entities"  ← Should be lowercase "entities"
```

**Fix**:
- Verify card type spelling (use lowercase)
- Check HACS for custom card installation
- Update deprecated card types
- Use standard card types when possible

**Reference**: Card Configuration Validation workflow

---

## Pattern 5: Template Errors in Cards

**Common causes**:
- Invalid Jinja2 syntax
- Undefined variables
- Wrong attribute access
- Missing quotes in templates

**Detection**:
```bash
# Extract templates from dashboard
grep -oP '{{.*?}}' .storage/lovelace.dashboard
```

**Example errors**:
```jinja2
// WRONG: Unclosed bracket
{{ states('sensor.x') |

// WRONG: Undefined variable
{{ states.nonexistent_sensor }}

// WRONG: Wrong attribute access
{{ state_attr('sensor.x', 'last_updated') }}  ← Use states.sensor.x.last_updated

// WRONG: Missing quotes
{{ states(sensor.x) }}  ← Should be states('sensor.x')
```

**Fix**:
- Close all brackets: `{{ ... }}`
- Verify variables exist
- Use correct attribute access: `states.entity.property` or `state_attr('entity', 'attribute')`
- Add quotes around entity IDs: `states('sensor.x')`

**Reference**: HA Manager skill docs/06_common_mistakes.md

---

## Pattern 6: Missing Required Card Options

**Common causes**:
- Missing required option for card type
- Wrong option format
- Invalid option value

**Detection**:
```bash
# Check card configurations
python3 -c "
import json
data = json.load(open('.storage/lovelace.dashboard'))
for view in data.get('views', []):
    for card in view.get('cards', []):
        print(f\"Type: {card.get('type')}, Options: {list(card.keys())}\")
"
```

**Common required options**:
```yaml
entity card:
  - type (required)
  - entity (required)

entities card:
  - type (required)
  - entities (required)
  - title (optional)

glance card:
  - type (required)
  - entities (required)

history-graph card:
  - type (required)
  - entities (required)
  - hours_to_show (optional)
```

**Example errors**:
```yaml
# WRONG: Missing entity option
{
  "type": "entity"
  // Missing: "entity": "sensor.temperature"
}

# WRONG: Wrong option format
{
  "type": "entities",
  "entities": "sensor.temp"  ← Should be array: ["sensor.temp"]
}
```

**Fix**:
- Add all required options for card type
- Use correct option format (array vs string)
- Validate option values against card schema

**Reference**: Card Configuration Validation workflow

---

## Pattern 7: Dashboard Not Loading After Deployment

**Common causes**:
- Browser cache (old dashboard cached)
- Invalid JSON (dashboard failed to load)
- Missing custom cards (HACS not updated)
- Entity not loading (integration issues)

**Detection**:
```bash
# Check browser console for errors
# Open DevTools (F12) → Console tab

# Check HA logs for dashboard errors
ssh ha "ha core logs | grep -i dashboard | tail -20"
```

**Troubleshooting steps**:
```bash
# 1. Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
# 2. Check JSON syntax
python3 -m json.tool .storage/lovelace.dashboard
# 3. Check for custom card errors
ssh ha "ha core logs | grep -i custom"
# 4. Verify entities exist
source .env && hass-cli state list | grep -E "(sensor|entity)"
```

**Fix**:
- Hard refresh browser to clear cache
- Fix any JSON syntax errors
- Install missing custom cards via HACS
- Check entity availability

**Reference**: HA Manager skill docs/05_lovelace_dashboards.md

---

## Pattern 8: Custom Card Not Working

**Common causes**:
- Custom card not installed via HACS
- Wrong card syntax
- Custom card version incompatible
- Missing required resources

**Detection**:
```bash
# Check if custom card is installed
ls -la /homeassistant/www/community/<card-name>/

# Check HA logs for custom card errors
ssh ha "ha core logs | grep -i custom | tail -20"
```

**Common custom cards**:
```yaml
custom:config-template-card:
  - Install via HACS
  - Requires: variables, card config

custom:button-card:
  - Install via HACS
  - Requires: entity, icon, tap_action

custom:mini-graph-card:
  - Install via HACS
  - Requires: entities, hours_to_show
```

**Fix**:
- Install custom card via HACS
- Check custom card documentation for correct syntax
- Update custom card to latest version
- Clear browser cache after installation

**Reference**: Card Configuration Validation workflow

---

## Quick Reference: Common Dashboard Issues

| Issue | Detection | Fix |
|-------|-----------|-----|
| **Invalid JSON** | `python3 -m json.tool file` | Fix syntax errors |
| **Not registered** | Check `.storage/lovelace_dashboards` | Add registration, restart HA |
| **Entity not found** | `hass-cli state list \| grep entity` | Fix entity ID or remove |
| **Invalid card type** | Check card type spelling | Use valid card type |
| **Template errors** | Check Jinja2 syntax | Fix template syntax |
| **Missing options** | Check card schema | Add required options |
| **Not loading** | Hard refresh browser | Clear cache, check logs |
| **Custom card broken** | Check HACS installation | Install/update custom card |

---

## Validation Checklist

Before deploying dashboard changes:

**JSON Structure**:
- [ ] Valid JSON syntax
- [ ] No trailing commas
- [ ] All brackets closed
- [ ] Double quotes used correctly

**Registration**:
- [ ] Dashboard registered in lovelace_dashboards
- [ ] Unique ID used
- [ ] Required fields present (id, title, url_path)

**Entity References**:
- [ ] All entities exist
- [ ] Correct entity domains
- [ ] No unavailable entities (or acknowledged)

**Card Configuration**:
- [ ] Valid card types
- [ ] Required options present
- [ ] Templates syntax correct
- [ ] Custom cards installed

**Testing**:
- [ ] JSON validated
- [ ] Entities verified
- [ ] Browser refresh tested
- [ ] Dashboard loads correctly

---

## Integration with Other Subagents

**Config Validator**: Can validate YAML entities referenced in dashboards
- Config Validator validates YAML automations
- Lovelace Dashboard Tester validates JSON dashboards
- Cross-reference: Entities used in both YAML and JSON

**HA Log Analyzer**: Dashboard error diagnosis
- Lovelace Dashboard Tester validates dashboard
- HA Log Analyzer checks logs for dashboard load errors
- Post-deployment verification

**Deployment Orchestrator**: Dashboard deployment workflow
- Lovelace Dashboard Tester validates dashboard
- Deployment Orchestrator deploys dashboard via SCP
- Note: Dashboards don't require restart, just browser refresh

---

## Dashboard Deployment Workflow

```
1. Edit dashboard locally
   vim .storage/lovelace.dashboard

2. Validate JSON syntax
   python3 -m json.tool .storage/lovelace.dashboard

3. Validate entities
   source .env && hass-cli state list | grep entity

4. Deploy via SCP (rapid iteration)
   scp .storage/lovelace.dashboard ha:/homeassistant/.storage/

5. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
   # No HA restart needed!

6. Test and iterate (repeat 1-5)

7. Commit when stable
   git add .storage/lovelace.dashboard
   git commit -m "Update dashboard"
```

**Key advantage**: Dashboards don't require HA restart, just browser refresh!
