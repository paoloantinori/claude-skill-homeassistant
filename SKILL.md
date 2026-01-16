---
name: home-assistant-manager
description: Expert-level Home Assistant configuration management with efficient deployment workflows (git and rapid scp iteration), remote CLI access via SSH and hass-cli, automation verification protocols, log analysis, reload vs restart optimization, and comprehensive Lovelace dashboard management for tablet-optimized UIs. Includes template patterns, card types, debugging strategies, and real-world examples.
triggers:
  files:
    - "automations/**/*.yaml"
    - "automations/**/*.yml"
    - "scripts/**/*.yaml"
    - "scripts/**/*.yml"
    - "templates/**/*.yaml"
    - "templates/**/*.yml"
    - "pyscript/**/*.py"
    - "packages/**/*.yaml"
    - "packages/**/*.yml"
    - "configuration.yaml"
    - "**/lovelace/**/*.yaml"
    - "**/lovelace/**/*.yml"
    - "ui-lovelace.yaml"
  commands:
    - "scp *ha:/homeassistant/*"
    - "scp * ha:/homeassistant/*"
    - "ssh ha*"
    - "hass-cli*"
    - "curl *homeassistant*"
    - "curl *HASS_SERVER*"
    - "git pull*"
    - "git push*"
  keywords:
    - "home assistant"
    - "homeassistant"
    - "automation"
    - "lovelace"
    - "dashboard"
    - "deploy to ha"
    - "reload automation"
    - "reload script"
    - "reload template"
    - "pyscript"
    - "hass-cli"
---

# Home Assistant Manager

Expert-level Home Assistant configuration management with efficient workflows, remote CLI access, and verification protocols.

## Core Capabilities

- Remote Home Assistant instance management via SSH and hass-cli
- Smart deployment workflows (git-based and rapid iteration)
- Configuration validation and safety checks
- Automation testing and verification
- Log analysis and error detection
- Reload vs restart optimization
- Lovelace dashboard development and optimization
- Template syntax patterns and debugging
- Tablet-optimized UI design

## Prerequisites

Before starting, verify the environment has:
1. SSH access to Home Assistant instance (`ssh ha`)
2. `hass-cli` installed locally
3. Environment variables loaded (HASS_SERVER, HASS_TOKEN) - via `source .env`
4. Git repository connected to HA `/homeassistant` directory
5. Context7 MCP server with Home Assistant docs (optional)

**Note:** The `ha core` CLI commands are not available via the SSH add-on. Use `hass-cli` for service calls and API access instead.

## 🚨 CRITICAL GUARDRAILS - Reload vs Restart

**NEVER use `ha core restart` unless EXPLICITLY required by the change type.**

### When to RELOAD (fast, non-disruptive):

**⚠️ ALWAYS source .env first:** `source /home/pantinor/data/repo/personal/hassio/.env`

| Change Type | Reload Command |
|-------------|----------------|
| Automations | `source .env && hass-cli service call automation.reload` |
| Scripts | `source .env && hass-cli service call script.reload` |
| Templates | `source .env && hass-cli service call template.reload` |
| Scenes | `source .env && hass-cli service call scene.reload` |
| Groups | `source .env && hass-cli service call group.reload` |
| Themes | `source .env && hass-cli service call frontend.reload_themes` |

**Note:** Without sourcing `.env`, hass-cli will fail with 401 Unauthorized.

### When RESTART is actually required:
- New integrations in `configuration.yaml`
- Min/Max sensors and platform-based sensors
- Core configuration changes
- New packages added

### If hass-cli fails (401/connection error) - Use REST API fallback:
```bash
# ✅ CORRECT: Use REST API for reload (non-disruptive)
source /home/pantinor/data/repo/personal/hassio/.env && \
curl -s -X POST \
  -H "Authorization: Bearer ${HASS_TOKEN}" \
  -H "Content-Type: application/json" \
  "${HASS_SERVER}/api/services/automation/reload"

# ❌ WRONG: Do NOT fall back to ha core restart for simple reloads!
# ssh ha "ha core restart"  # NEVER do this for automations/scripts/templates
```

### Guardrail Checklist:
0. ✅ **Source .env first:** `source /home/pantinor/data/repo/personal/hassio/.env`
1. ✅ Identify what changed (automations? scripts? templates?)
2. ✅ Use the appropriate reload service call
3. ✅ If hass-cli fails → Check if .env was sourced, then use REST API
4. ❌ NEVER use `ha core restart` as a lazy fallback

## Quick Deployment (Claude Code)

Two methods available for deploying config changes from Claude Code:

### Method 1: SSH + tar (Direct, Always Works)
```bash
# Deploy all config files
tar czf - automations.yaml scripts.yaml templates/ | ssh ha "cd /homeassistant && sudo tar xzf -"

# Reload via hass-cli
export HASS_SERVER=http://homeassistant.lan:8123
export HASS_TOKEN=<token_from_.env>
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call template.reload
```

### Method 2: MCP Script (After Git SSH Setup)
Once git SSH is configured on HA, call via MCP:
```
script.deploy_from_github
```
This pulls from GitHub and reloads all YAML automatically.

### Environment Setup
Source credentials before using hass-cli:
```bash
export HASS_SERVER=http://homeassistant.lan:8123
export HASS_TOKEN=<from .env>
export HASS_SSH_USER=root
export HASS_SSH_HOST=homeassistant.lan
```

## Remote Access Patterns

### Using hass-cli (Local, via REST API)

All `hass-cli` commands use environment variables automatically:

```bash
# List entities
hass-cli state list

# Get specific state
hass-cli state get sensor.entity_name

# Call services
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
```

### Using SSH for File Operations

```bash
# Deploy files via SCP
scp automations.yaml ha:/homeassistant/

# Pull latest from git
ssh ha "cd /homeassistant && git pull"

# Check git status on HA
ssh ha "cd /homeassistant && git status"
```

**SSH Fingerprint Display:** When connecting via SSH, you may see a host key fingerprint displayed as ASCII art:
```
+--[ED25519 256]--+
|        .o..    |
|       .  o     |
...
+----[SHA256]-----+
```
This is **normal visual confirmation**, NOT a prompt to accept an unknown host. The connection proceeds automatically - no action required. This appears because `VisualHostKey yes` is enabled in the SSH config.

**Note:** `ha core check/restart/logs` commands require Supervisor access (not available via SSH add-on). Use hass-cli instead:
```bash
# Reload automations (instead of restart)
hass-cli service call automation.reload

# Check for errors via API
hass-cli raw get /api/error/all
```

## Template Evaluation via REST API

Evaluate Jinja2 templates remotely using the `/api/template` endpoint. **Critical escaping rules apply.**

### Basic Template Evaluation
```bash
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states(\"sensor.temperature\") }}"}' \
  "$HASS_SERVER/api/template"
```

### ⚠️ JSON Escaping Rules (CRITICAL)

When embedding Jinja2 in JSON within bash:

| Character | Escape Method | Example |
|-----------|---------------|---------|
| Inner `"` | Use `\"` | `states(\"sensor.foo\")` |
| `$` in bash | Use single quotes for outer shell | `'{"template": "..."}'` |
| Emojis | **AVOID** - causes invalid JSON | Use text descriptions instead |
| Newlines | Use `\\n` or avoid | Single-line templates preferred |

### ✅ Correct Examples
```bash
# Simple state check
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states(\"cover.tapparella_nora\") }}"}' \
  "$HASS_SERVER/api/template"

# Multiple states with string concatenation
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "State: {{ states(\"sensor.a\") }}, Attr: {{ state_attr(\"sensor.a\", \"unit\") }}"}' \
  "$HASS_SERVER/api/template"

# Boolean logic
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ is_state(\"binary_sensor.foo\", \"on\") and is_state(\"binary_sensor.bar\", \"off\") }}"}' \
  "$HASS_SERVER/api/template"
```

### ❌ Common Mistakes
```bash
# WRONG: Emojis in template (invalid UTF-8/JSON)
-d '{"template": "Status: ✅ {{ states(\"sensor.foo\") }}"}'

# WRONG: Unescaped inner quotes
-d '{"template": "{{ states("sensor.foo") }}"}'

# WRONG: Double quotes for outer shell ($ expansion issues)
-d "{"template": "{{ states(\"sensor.foo\") }}"}"
```

### Alternative: Use hass-cli raw
For complex templates, use `hass-cli raw` with a JSON file:
```bash
# Create template file
echo '{"template": "{{ now() }}"}' > /tmp/tpl.json

# Execute
source .env && hass-cli raw post /api/template < /tmp/tpl.json
```

## Deployment Workflows

### Standard Git Workflow (Final Changes)

Use for changes you want in version control:

```bash
# 1. Make changes locally
# 2. Check validity
ssh ha "ha core check"

# 3. Commit and push
git add file.yaml
git commit -m "Description"
git push

# 4. CRITICAL: Pull to HA instance
ssh ha "cd /homeassistant && git pull"

# 5. Reload or restart
hass-cli service call automation.reload  # if reload sufficient
# OR
ssh ha "ha core restart"  # if restart needed

# 6. Verify
hass-cli state get sensor.new_entity
ssh ha "ha core logs | grep -i error | tail -20"
```

### Rapid Development Workflow (Testing/Iteration)

Use `scp` for quick testing before committing:

```bash
# 1. Make changes locally
# 2. Quick deploy
scp automations.yaml ha:/homeassistant/

# 3. Reload/restart
hass-cli service call automation.reload

# 4. Test and iterate (repeat 1-3 as needed)

# 5. Once finalized, commit and push to git
git add automations.yaml
git commit -m "Final tested changes"
git push

# 6. CRITICAL: Sync HA git state (reset scp'd files, then pull)
# First, discard local changes for the specific files we scp'd
ssh ha "cd /homeassistant && git checkout -- automations.yaml"
# Then pull (now clean, will succeed)
ssh ha "cd /homeassistant && git pull"
```

**Why `git checkout -- <files>` before `git pull`:**
After testing with `scp`, the HA instance has modified files. A regular `git pull` would fail with "uncommitted local changes" error. The safe approach:
1. `git checkout -- <files>` - reverts ONLY the specific files we scp'd to their last committed state
2. `git pull` - now succeeds since there are no conflicts

**Important:** Only checkout the files you explicitly scp'd. Do NOT use `git reset --hard` as it would discard ALL local modifications, including any unrelated changes on the server.

### CRITICAL: Never Use `git reset --hard` on HA Server

**FORBIDDEN command:**
```bash
# NEVER DO THIS - can lose uncommitted work on the server
ssh ha "cd /homeassistant && git reset --hard origin/master"
```

**Why this is dangerous:**
- The HA server may have uncommitted changes (manual edits, UI changes, other tools)
- `git reset --hard` discards ALL local modifications without warning
- There is no recovery from this operation

**Even after force-push, use this safe pattern instead:**
```bash
# 1. ALWAYS check for uncommitted changes first
ssh ha "cd /homeassistant && git status"

# 2. If only expected files are modified, checkout those specific files
ssh ha "cd /homeassistant && git checkout -- file1.yaml file2.yaml"

# 3. Then pull (or fetch + rebase for force-push scenarios)
ssh ha "cd /homeassistant && git fetch origin && git rebase origin/master"

# 4. If unexpected changes exist, ASK THE USER before proceeding
```

### 🚨 CRITICAL: INSPECT Before Discarding HA Server Changes

**NEVER run `git checkout --` on the HA server without FIRST inspecting the differences.**

When `git pull` fails with "uncommitted local changes":

```bash
# ✅ CORRECT WORKFLOW:
# Step 1: INSPECT what changed and WHY
ssh ha "cd /homeassistant && git diff automations.yaml"

# Step 2: ANALYZE the output
# - Are these MY scp-deployed changes from this session? → Safe to discard
# - Are these UNKNOWN changes from outside this session? → STOP, investigate

# Step 3: ONLY THEN decide
# If your own changes: git checkout -- file.yaml
# If unknown changes: Ask user, do NOT discard blindly

# ❌ FORBIDDEN: Blind discard without inspection
ssh ha "cd /homeassistant && git checkout -- file.yaml"  # NEVER without diff first!
```

**Why this matters:**
- The HA server may have legitimate changes from: UI edits, other tools, manual SSH sessions, or another developer
- Blindly discarding loses those changes with NO recovery
- This violates the "Evidence > assumptions" principle

**Evidence > Assumptions**: Always verify the nature of conflicts before discarding.

**When to use scp:**
- 🚀 Rapid iteration and testing
- 🔄 Frequent small adjustments
- 🧪 Experimental changes
- 🎨 UI/Dashboard work

**When to use git:**
- ✅ Final tested changes
- 📦 Version control tracking
- 🔒 Important configs
- 👥 Changes to document

## Reload vs Restart Decision Making

**ALWAYS assess if reload is sufficient before requiring a full restart.**

### Can be reloaded (fast, preferred):
- ✅ Automations: `hass-cli service call automation.reload`
- ✅ Scripts: `hass-cli service call script.reload`
- ✅ Scenes: `hass-cli service call scene.reload`
- ✅ Template entities: `hass-cli service call template.reload`
- ✅ Groups: `hass-cli service call group.reload`
- ✅ Themes: `hass-cli service call frontend.reload_themes`

### Require full restart:
- ❌ Min/Max sensors and platform-based sensors
- ❌ New integrations in configuration.yaml
- ❌ Core configuration changes
- ❌ MQTT sensor/binary_sensor platforms

## Automation Locations

**Automations can exist in multiple locations:**

| Location | Description |
|----------|-------------|
| `automations.yaml` | Main automation file (HA default) |
| `automations/*/` | Split automations by category |
| `packages/*/` | HA packages bundling automations with related entities |

**Important:** When searching for or analyzing automations, always check ALL three locations. Packages can contain automations alongside input_booleans, sensors, scripts, and other related entities.

**Entity Registry:** The unique_id in the entity registry corresponds to the `id:` field in the automation YAML. If automations appear duplicated in the UI, check for:
- Mismatched `id:` vs `alias:` (ID should match the purpose)
- Orphaned registry entries from deleted automations
- Old numeric IDs that were migrated to descriptive IDs

### Modifying the Entity Registry

**CRITICAL:** The entity registry is cached in memory. Edits while HA is running will be overwritten on shutdown.

**Correct procedure:**
```bash
# 1. STOP HA first
ssh ha "ha core stop"
sleep 10

# 2. Edit the registry (example: remove orphaned entries)
ssh ha "python3 << 'EOF'
import json
with open('/homeassistant/.storage/core.entity_registry', 'r') as f:
    data = json.load(f)

# Remove specific entries
data['data']['entities'] = [
    e for e in data['data']['entities']
    if e.get('unique_id') not in ['id_to_remove']
]

with open('/homeassistant/.storage/core.entity_registry', 'w') as f:
    json.dump(data, f, indent=2)
EOF"

# 3. START HA - new entries will be created from YAML
ssh ha "ha core start"
```

**Common registry operations:**
- Remove orphaned entries (unique_id no longer in YAML)
- Fix entity_id mismatches (rename entity_id field)
- Clean up duplicate entries with `_2`, `_3` suffixes

## Automation Verification Workflow

**ALWAYS verify automations after deployment:**

### Step 1: Deploy
```bash
git add automations.yaml && git commit -m "..." && git push
ssh ha "cd /homeassistant && git pull"
```

### Step 2: Check Configuration
```bash
ssh ha "ha core check"
```

### Step 3: Reload
```bash
hass-cli service call automation.reload
```

### Step 4: Manually Trigger
```bash
hass-cli service call automation.trigger --arguments entity_id=automation.name
```

**Why trigger manually?**
- Instant feedback (don't wait for scheduled triggers)
- Verify logic before production
- Catch errors immediately

### Step 5: Check Logs
```bash
sleep 3
ssh ha "ha core logs | grep -i 'automation_name' | tail -20"
```

**Success indicators:**
- `Initialized trigger AutomationName`
- `Running automation actions`
- `Executing step ...`
- No ERROR or WARNING messages

**Error indicators:**
- `Error executing script`
- `Invalid data for call_service`
- `TypeError`, `Template variable warning`

### Step 6: Verify Outcome

**For notifications:**
- Ask user if they received it
- Check logs for mobile_app messages

**For device control:**
```bash
hass-cli state get switch.device_name
```

**For sensors:**
```bash
hass-cli state get sensor.new_sensor
```

### Step 7: Fix and Re-test if Needed
If errors found:
1. Identify root cause from error messages
2. Fix the issue
3. Re-deploy (steps 1-2)
4. Re-verify (steps 3-6)

## Dashboard Management

### Dashboard Fundamentals

**What are Lovelace Dashboards?**
- JSON files in `.storage/` directory (e.g., `.storage/lovelace.control_center`)
- UI configuration for Home Assistant frontend
- Optimizable for different devices (mobile, tablet, wall panels)

**Critical Understanding:**
- Creating dashboard file is NOT enough - must register in `.storage/lovelace_dashboards`
- Dashboard changes don't require HA restart (just browser refresh)
- Use panel view for full-screen content (maps, cameras)
- Use sections view for organized multi-card layouts

### Dashboard Development Workflow

**Rapid Iteration with scp (Recommended for dashboards):**

```bash
# 1. Make changes locally
vim .storage/lovelace.control_center

# 2. Deploy immediately (no git commit yet)
scp .storage/lovelace.control_center ha:/homeassistant/.storage/

# 3. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
# No HA restart needed!

# 4. Iterate: Repeat 1-3 until perfect

# 5. Commit when stable
git add .storage/lovelace.control_center
git commit -m "Update dashboard layout"
git push
ssh ha "cd /homeassistant && git pull"
```

**Why scp for dashboards:**
- Instant feedback (no HA restart)
- Iterate quickly on visual changes
- Commit only stable versions

### Creating New Dashboard

**Complete workflow:**

```bash
# Step 1: Create dashboard file
cp .storage/lovelace.my_home .storage/lovelace.new_dashboard

# Step 2: Register in lovelace_dashboards
# Edit .storage/lovelace_dashboards to add:
{
  "id": "new_dashboard",
  "show_in_sidebar": true,
  "icon": "mdi:tablet-dashboard",
  "title": "New Dashboard",
  "require_admin": false,
  "mode": "storage",
  "url_path": "new-dashboard"
}

# Step 3: Deploy both files
scp .storage/lovelace.new_dashboard ha:/homeassistant/.storage/
scp .storage/lovelace_dashboards ha:/homeassistant/.storage/

# Step 4: Restart HA (required for registry changes)
ssh ha "ha core restart"
sleep 30

# Step 5: Verify appears in sidebar
```

**Update .gitignore to track:**
```gitignore
# Exclude .storage/ by default
.storage/

# Include dashboard files
!.storage/lovelace.new_dashboard
!.storage/lovelace_dashboards
```

### View Types Decision Matrix

**Use Panel View when:**
- Displaying full-screen map (vacuum, cameras)
- Single large card needs full width
- Want zero margins/padding
- Minimize scrolling

**Use Sections View when:**
- Organizing multiple cards
- Need responsive grid layout
- Building multi-section dashboards

**Layout Example:**
```json
// Panel view - full width, no margins
{
  "type": "panel",
  "title": "Vacuum Map",
  "path": "map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "entity": "vacuum.dusty"
    }
  ]
}

// Sections view - organized, has ~10% margins
{
  "type": "sections",
  "title": "Home",
  "sections": [
    {
      "type": "grid",
      "cards": [...]
    }
  ]
}
```

### Card Types Quick Reference

**Mushroom Cards (Modern, Touch-Optimized):**
```json
{
  "type": "custom:mushroom-light-card",
  "entity": "light.living_room",
  "use_light_color": true,
  "show_brightness_control": true,
  "collapsible_controls": true,
  "fill_container": true
}
```
- Best for tablets and touch screens
- Animated, colorful icons
- Built-in slider controls

**Mushroom Template Card (Dynamic Content):**
```json
{
  "type": "custom:mushroom-template-card",
  "primary": "All Doors",
  "secondary": "{% set sensors = ['binary_sensor.front_door'] %}\n{% set open = sensors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ sensors | length }} open",
  "icon": "mdi:door",
  "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
}
```
- Use Jinja2 templates for dynamic content
- Color-code status with icon_color
- Multi-line templates use `\n` in JSON

**Tile Card (Built-in, Modern):**
```json
{
  "type": "tile",
  "entity": "climate.thermostat",
  "features": [
    {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
    {"type": "target-temperature"}
  ]
}
```
- No custom cards required
- Built-in features for controls

### Common Template Patterns

**Counting Open Doors:**
```jinja2
{% set door_sensors = [
  'binary_sensor.front_door',
  'binary_sensor.back_door'
] %}
{% set open = door_sensors | select('is_state', 'on') | list | length %}
{{ open }} / {{ door_sensors | length }} open
```

**Color-Coded Days Until:**
```jinja2
{% set days = state_attr('sensor.bin_collection', 'daysTo') | int %}
{% if days <= 1 %}red
{% elif days <= 3 %}amber
{% elif days <= 7 %}yellow
{% else %}grey
{% endif %}
```

**Conditional Display:**
```jinja2
{% set bins = [] %}
{% if days and days | int <= 7 %}
  {% set bins = bins + ['Recycling'] %}
{% endif %}
{% if bins %}This week: {{ bins | join(', ') }}{% else %}None this week{% endif %}
```

**IMPORTANT:** Always use `| int` or `| float` to avoid type errors when comparing

### Tablet Optimization

**Screen-specific layouts:**
- 11-inch tablets: 3-4 columns
- Touch targets: minimum 44x44px
- Minimize scrolling: Use panel view for full-screen
- Visual feedback: Color-coded status (red/green/amber)

**Grid Layout for Tablets:**
```json
{
  "type": "grid",
  "columns": 3,
  "square": false,
  "cards": [
    {"type": "custom:mushroom-light-card", "entity": "light.living_room"},
    {"type": "custom:mushroom-light-card", "entity": "light.bedroom"}
  ]
}
```

### Common Dashboard Pitfalls

**Problem 1: Dashboard Not in Sidebar**
- **Cause:** File created but not registered
- **Fix:** Add to `.storage/lovelace_dashboards` and restart HA

**Problem 2: "Configuration Error" in Card**
- **Cause:** Custom card not installed, wrong syntax, template error
- **Fix:**
  - Check HACS for card installation
  - Check browser console (F12) for details
  - Test templates in Developer Tools → Template

**Problem 3: Auto-Entities Fails**
- **Cause:** `card_param` not supported by card type
- **Fix:** Use cards that accept `entities` parameter:
  - ✅ Works: `entities`, `vertical-stack`, `horizontal-stack`
  - ❌ Doesn't work: `grid`, `glance` (without specific syntax)

**Problem 4: Vacuum Map Has Margins/Scrolling**
- **Cause:** Using sections view (has margins)
- **Fix:** Use panel view for full-width, no scrolling

**Problem 5: Template Type Errors**
- **Error:** `TypeError: '<' not supported between instances of 'str' and 'int'`
- **Fix:** Use type filters: `states('sensor.days') | int < 7`

### Dashboard Debugging

**1. Browser Console (F12):**
- Check for red errors when loading dashboard
- Common: "Custom element doesn't exist" → Card not installed

**2. Validate JSON Syntax:**
```bash
python3 -m json.tool .storage/lovelace.control_center > /dev/null
```

**3. Test Templates:**
```
Home Assistant → Developer Tools → Template
Paste template to test before adding to dashboard
```

**4. Verify Entities:**
```bash
hass-cli state get binary_sensor.front_door
```

**5. Clear Browser Cache:**
- Hard refresh: Ctrl+F5 or Cmd+Shift+R
- Try incognito window

## Real-World Examples

### Quick Controls Dashboard Section
```json
{
  "type": "grid",
  "title": "Quick Controls",
  "cards": [
    {
      "type": "custom:mushroom-template-card",
      "primary": "All Doors",
      "secondary": "{% set doors = ['binary_sensor.front_door', 'binary_sensor.back_door'] %}\n{% set open = doors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ doors | length }} open",
      "icon": "mdi:door",
      "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
    },
    {
      "type": "tile",
      "entity": "climate.thermostat",
      "features": [
        {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
        {"type": "target-temperature"}
      ]
    }
  ]
}
```

### Individual Light Cards (Touch-Friendly)
```json
{
  "type": "grid",
  "title": "Lights",
  "columns": 3,
  "cards": [
    {
      "type": "custom:mushroom-light-card",
      "entity": "light.office_studio",
      "name": "Office",
      "use_light_color": true,
      "show_brightness_control": true,
      "collapsible_controls": true
    }
  ]
}
```

### Full-Screen Vacuum Map
```json
{
  "type": "panel",
  "title": "Vacuum",
  "path": "vacuum-map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "vacuum_platform": "Tasshack/dreame-vacuum",
      "entity": "vacuum.dusty"
    }
  ]
}
```

## Common Commands Quick Reference

```bash
# Configuration
ssh ha "ha core check"
ssh ha "ha core restart"

# Logs
ssh ha "ha core logs | tail -50"
ssh ha "ha core logs | grep -i error | tail -20"

# State/Services
hass-cli state list
hass-cli state get entity.name
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name

# Deployment
git add . && git commit -m "..." && git push
ssh ha "cd /homeassistant && git pull"
scp file.yaml ha:/homeassistant/

# Dashboard deployment
scp .storage/lovelace.my_dashboard ha:/homeassistant/.storage/
python3 -m json.tool .storage/lovelace.my_dashboard > /dev/null  # Validate JSON

# Quick test cycle
scp automations.yaml ha:/homeassistant/
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
ssh ha "ha core logs | grep -i 'automation' | tail -10"
```

## Best Practices Summary

1. **Always check configuration** before restart: `ha core check`
2. **Prefer reload over restart** when possible
3. **Test automations manually** after deployment
4. **Check logs** for errors after every change
5. **Use scp for rapid iteration**, git for final changes
6. **Verify outcomes** - don't assume it worked
7. **Use Context7** for current documentation
8. **Test templates in Dev Tools** before adding to dashboards
9. **Validate JSON syntax** before deploying dashboards
10. **Test on actual device** for tablet dashboards
11. **Color-code status** for visual feedback (red/green/amber)
12. **Commit only stable versions** - test with scp first

## Workflow Decision Tree

```
Configuration Change Needed
├─ Is this final/tested?
│  ├─ YES → Use git workflow
│  └─ NO → Use scp workflow
├─ Check configuration valid
├─ Deploy (git pull or scp)
├─ Needs restart?
│  ├─ YES → ha core restart
│  └─ NO → Use appropriate reload
├─ Verify in logs
└─ Test outcome

Dashboard Change Needed
├─ Make changes locally
├─ Deploy via scp for testing
├─ Refresh browser (Ctrl+F5)
├─ Test on target device
├─ Iterate until perfect
└─ Commit to git when stable
```

## Entity Registry Management

### 🚨 CRITICAL SAFETY RULE - ALWAYS BACKUP REGISTRY FIRST

**BEFORE making ANY modification to the entity registry, you MUST create a backup.**

The entity registry (`.storage/core.entity_registry`) is a critical Home Assistant database file. If corrupted, **ALL entity metadata is lost** (labels, icons, areas, customizations, disabled states, etc.).

**Mandatory backup procedure:**
```bash
# 1. ALWAYS backup BEFORE any registry operation
ssh ha "cp /config/.storage/core.entity_registry /config/.storage/core.entity_registry.backup_$(date +%Y%m%d_%H%M%S)"

# 2. Verify backup was created successfully
ssh ha "ls -lh /config/.storage/core.entity_registry.backup*" | tail -1

# 3. Only THEN proceed with registry modifications
```

**When this applies:**
- Enabling/disabling entities via API or registry editing
- Fixing duplicate `_2` entities
- Modifying unique_ids or entity_ids
- Running any script that touches the registry
- Manual JSON editing of the registry file
- Using REST API endpoints that modify entity registry

**Recovery if corrupted:**
```bash
# Restore from backup
ssh ha "cp /config/.storage/core.entity_registry.backup_YYYYMMDD_HHMMSS /config/.storage/core.entity_registry"
# Then restart HA
```

**Home Assistant maintains automatic backups:**
- `.storage/core.entity_registry.bak` - Most recent automatic backup
- Check with: `ssh ha "ls -lht /config/.storage/*.entity_registry*"`

**NEVER skip the backup step.** Registry corruption requires manual restoration and can cause significant downtime.

---

### Enabling/Disabling Entities Safely

**🚨 CRITICAL: The ONLY safe method to enable/disable entities is via the Web UI while HA is running.**

#### ✅ CORRECT Method: Web UI (Recommended)

```
1. Open: http://homeassistant.local:8123
2. Navigate: Settings → Devices & Services → Entities
3. Search for the entity (e.g., "telefono_chiara_is_charging")
4. Click on the disabled/enabled entity
5. Click "Enable" or "Disable" button
6. Wait a few seconds - no restart needed
```

**Why this is safe:**
- HA handles all registry updates in-memory
- No file corruption risk
- Changes take effect immediately
- No restart required
- HA validates the operation

#### ❌ DANGEROUS Methods That WILL Fail or Corrupt

**1. REST API Entity Registry Endpoints (DO NOT USE)**

These endpoints **DO NOT EXIST** or **DO NOT WORK** as expected:
```bash
# ❌ WRONG - These will return 404 or fail
curl -X POST "http://homeassistant.local:8123/api/config/entity_registry/ENTITY_ID"
curl -X POST "http://homeassistant.local:8123/api/config/entity_registry/update/ENTITY_ID"
```

**Reality:** Home Assistant's REST API does NOT support direct entity enable/disable operations. The entity registry is managed through WebSocket API (undocumented) or the UI only.

**2. Direct File Editing While HA is Running (EXTREMELY DANGEROUS)**

```bash
# ❌ WRONG - This WILL corrupt the registry
ssh ha "cat /config/.storage/core.entity_registry | jq '...' > /tmp/new.json"
scp /tmp/new.json ha:/config/.storage/core.entity_registry

# ❌ WRONG - SCP can create 0-byte files
scp local_registry.json ha:/config/.storage/core.entity_registry
```

**Why this fails:**
- HA keeps the registry **in memory** while running
- Any file changes are **overwritten on HA shutdown**
- SCP errors or pipe failures create **0-byte files** → complete corruption
- jq piping can fail silently and output nothing
- No atomic write protection

**3. Python Scripts on Running HA (WILL FAIL)**

```bash
# ❌ WRONG - Changes lost when HA shuts down
ssh ha "python3 /tmp/enable_entity.py"
```

**Why this fails:**
- HA loads registry into memory at startup
- File modifications don't affect running HA
- HA overwrites file from memory on shutdown
- Your changes are silently lost

#### ⚠️ Advanced Method: Registry Editing (ONLY When HA is Stopped)

**Use ONLY for:**
- Fixing corrupt registries
- Bulk operations on stopped systems
- Recovery scenarios

**Requirements:**
1. HA **MUST be completely stopped** (not just restarting)
2. Backup MUST be verified before editing
3. Use proper Python JSON handling (NOT jq/sed)
4. Verify file size after writing
5. Reboot to restart HA

**Correct procedure:**
```bash
# 1. BACKUP FIRST (verify size)
ssh ha "cp /config/.storage/core.entity_registry /config/.storage/core.entity_registry.backup_$(date +%Y%m%d_%H%M%S)"
ssh ha "ls -lh /config/.storage/core.entity_registry.backup*" | tail -1
# VERIFY: File size should be ~4MB, NOT 0 bytes

# 2. STOP HA COMPLETELY
source .env && hass-cli service call homeassistant.stop
sleep 30

# 3. Verify HA is stopped
# Check that API is unreachable or use system check

# 4. Download registry to local machine
scp ha:/config/.storage/core.entity_registry /tmp/registry_local.json

# VERIFY: Check file size locally
ls -lh /tmp/registry_local.json
# MUST be ~4MB, NOT 0 bytes - if 0, SCP failed, restore backup immediately

# 5. Edit locally with Python (NEVER jq/sed)
python3 /tmp/edit_registry.py  # Proper JSON handling

# 6. VERIFY edited file before uploading
ls -lh /tmp/registry_edited.json
# MUST be reasonable size, NOT 0 bytes

# 7. Upload edited file
scp /tmp/registry_edited.json ha:/config/.storage/core.entity_registry

# 8. VERIFY uploaded file
ssh ha "ls -lh /config/.storage/core.entity_registry"
# If 0 bytes: RESTORE BACKUP IMMEDIATELY
# ssh ha "cp /config/.storage/core.entity_registry.backup_YYYYMMDD_HHMMSS /config/.storage/core.entity_registry"

# 9. Reboot system (can't start HA via SSH add-on)
ssh ha "sudo reboot"
```

#### Common Mistakes and Their Consequences

| Mistake | Consequence | Recovery |
|---------|-------------|----------|
| Edit registry while HA running | Changes silently lost on shutdown | Re-edit with HA stopped |
| SCP without size verification | 0-byte file = total corruption | Restore from backup immediately |
| Use jq/sed piping | Empty output = total corruption | Restore from backup immediately |
| No backup before editing | Unrecoverable data loss | None - all metadata lost |
| REST API enable/disable | 404 error or no effect | Use Web UI instead |
| Restart instead of stop | Registry rewritten from memory | Changes lost, must stop HA |

#### Verification Checklist

Before proceeding with ANY registry operation:

```bash
# ✅ 1. Backup exists and is valid
ssh ha "ls -lh /config/.storage/core.entity_registry.backup_*" | tail -1
# Must show file size ~4MB

# ✅ 2. HA is actually stopped (for advanced editing only)
curl -f http://homeassistant.local:8123/api/ || echo "HA is stopped"

# ✅ 3. After any file operation, verify size
ssh ha "ls -lh /config/.storage/core.entity_registry"
# Must be ~4MB, NOT 0 bytes

# ✅ 4. If 0 bytes detected, restore IMMEDIATELY
ssh ha "cp /config/.storage/core.entity_registry.bak /config/.storage/core.entity_registry"
```

#### Summary: Decision Tree

```
Need to enable/disable an entity?
├─ HA is running? → YES → Use Web UI (ONLY safe method)
├─ HA is running? → NO  → Can you start HA?
   ├─ YES → Start HA, use Web UI
   └─ NO  → Advanced registry editing (follow full procedure above)

Need to bulk edit entities?
├─ < 10 entities → Use Web UI (tedious but safest)
└─ > 10 entities → Stop HA, edit registry with Python, verify at each step
```

**Default recommendation: ALWAYS use the Web UI unless absolutely impossible.**

---

### Understanding Automation IDs vs Entity IDs

**Critical distinction:**
- **YAML `id` field** → becomes `unique_id` in entity registry (internal identifier)
- **YAML `alias` field** → becomes `entity_id` (e.g., `automation.kitchen_thermostat_schedule`)

**WARNING: Changing automation IDs causes problems!**
When you change an automation's `id` field:
1. HA sees it as a completely NEW automation
2. Creates a new entity registry entry
3. Since the `alias` generates the same `entity_id`, HA adds `_2` suffix
4. Old metadata (area, icon, labels) is orphaned on the old entry

### Labels, Icons, and Areas are UI-Only

**These CANNOT be set via YAML:**
- Labels
- Icons (for automations)
- Area assignments

**They are stored in:** `.storage/core.entity_registry`

**To set them:**
1. Via HA UI: Settings → Automations → Select → 3-dot menu → Edit metadata
2. Via WebSocket API (undocumented): `config/entity_registry/update`

**The MCP server does NOT support setting labels/icons** - it only provides device control.

### Fixing Duplicate `_2` Automation Entries

If you changed automation IDs and have duplicates:

**The Fix Process:**
```bash
# 1. Stop HA (NOT restart - must stop completely)
curl -X POST "http://homeassistant.local:8123/api/services/homeassistant/stop" \
  -H "Authorization: Bearer $HASS_TOKEN"

# 2. Wait for HA to stop
sleep 15

# 3. Run fix script (updates unique_ids, removes duplicates)
# See /tmp/ha_fix_registry_final.py or create similar

# 4. Reboot system (since we can't start HA via SSH add-on)
ssh ha "sudo reboot"
```

**Fix Script Logic:**
```python
# For each _2 entry:
#   1. Find matching non-_2 entry (has metadata)
#   2. Update non-_2 entry's unique_id to match new YAML id
#   3. Delete the _2 entry
# Result: Clean entity_ids with preserved metadata
```

**Key insight:** Registry changes must be made while HA is STOPPED. HA overwrites registry from memory on shutdown.

### Entity Registry Structure

```json
{
  "entity_id": "automation.kitchen_thermostat_schedule",
  "unique_id": "climate_kitchen_thermostat_schedule",  // <-- matches YAML id
  "area_id": "kitchen",
  "icon": "mdi:home-thermometer-outline",
  "labels": ["thermostat"],
  "platform": "automation"
}
```

### Best Practices for Automation IDs

1. **Pick descriptive IDs from the start** - avoid changing them later
2. **Use consistent naming convention:** `domain_room_action` (e.g., `climate_kitchen_thermostat_schedule`)
3. **If you must change IDs:** Be prepared to run the registry fix process
4. **Document your ID scheme** to maintain consistency

## Automation Metadata Tools

Scripts in `scripts/` directory for managing automation labels, icons, and areas programmatically.

### Prerequisites

```bash
pip install websockets pyyaml
```

### Tool 1: Registry Backup (`ha_backup_registry.py`)

Create timestamped backups of the entity registry before making changes.

```bash
# Create backup
python3 scripts/ha_backup_registry.py backup

# List existing backups
python3 scripts/ha_backup_registry.py list

# Restore from backup (requires HA stopped)
python3 scripts/ha_backup_registry.py restore 20260107_120000

# Clean old backups (keep last 5)
python3 scripts/ha_backup_registry.py clean --keep 5
```

Backups stored in: `scripts/backups/entity_registry.<timestamp>.json`

### Tool 2: Entity Metadata (`ha_entity_metadata.py`)

Bulk assign labels, icons, and areas via WebSocket API.

```bash
# ALWAYS START WITH STATS - shows what's missing
python3 scripts/ha_entity_metadata.py stats

# Export ALL automations (including those without metadata)
python3 scripts/ha_entity_metadata.py export --all > all_automations.yaml

# Export only automations that already have metadata
python3 scripts/ha_entity_metadata.py export > metadata.yaml

# Apply metadata from config file
python3 scripts/ha_entity_metadata.py apply metadata.yaml

# Preview changes without applying
python3 scripts/ha_entity_metadata.py apply metadata.yaml --dry-run

# Set single automation
python3 scripts/ha_entity_metadata.py set automation.kitchen_thermostat \
    --icon mdi:thermometer --area kitchen --labels thermostat,climate

# Label management
python3 scripts/ha_entity_metadata.py labels list
python3 scripts/ha_entity_metadata.py labels create climate --icon mdi:thermometer --color blue
python3 scripts/ha_entity_metadata.py labels delete climate
python3 scripts/ha_entity_metadata.py labels suggest climate --pattern "automation.*thermostat*"
```

**IMPORTANT:** Always run `stats` first to see total automation count and coverage!

**Config file format (`automation_metadata.yaml`):**
```yaml
automations:
  automation.kitchen_thermostat_schedule:
    icon: mdi:home-thermometer-outline
    area_id: kitchen
    labels:
      - climate
      - scheduled
```

**Important:** Labels must exist before assignment. Create them first or use the Claude-assisted workflow.

### Tool 3: ID Migration (`ha_migrate_automation_ids.py`)

Safely migrate automation IDs while preserving metadata.

```bash
# Generate migration plan from current state
python3 scripts/ha_migrate_automation_ids.py generate > migration.yaml

# Preview what will change
python3 scripts/ha_migrate_automation_ids.py preview migration.yaml

# Execute full migration (stops HA, updates registry, reboots)
python3 scripts/ha_migrate_automation_ids.py execute migration.yaml

# Fix registry after YAML already updated (removes _2 duplicates)
python3 scripts/ha_migrate_automation_ids.py fix-registry
```

**Migration workflow:**
1. Update YAML `id` fields with new descriptive IDs
2. Generate or edit migration.yaml
3. Run `execute` - tool handles stop/migrate/reboot

### Tool 4: Entity Exposure (`ha_expose_entities.py`)

Manage which entities are exposed to the conversation agent (AI assistant).

```bash
# Expose entities to conversation agent
python3 scripts/ha_expose_entities.py expose sensor.flex_d_status sensor.nas_status

# Unexpose entities
python3 scripts/ha_expose_entities.py unexpose sensor.old_sensor

# List all currently exposed entities
python3 scripts/ha_expose_entities.py list

# Check if specific entities are exposed
python3 scripts/ha_expose_entities.py check sensor.flex_d_status
```

**Use cases:**
- Expose new summary sensors to AI assistant
- Bulk expose/unexpose entities
- Audit what the AI can see

### Label Management Workflow (Claude-Assisted)

Labels require thoughtful planning. Use this workflow:

1. **Check current coverage (CRITICAL FIRST STEP):**
   ```bash
   python3 scripts/ha_entity_metadata.py stats
   ```

2. **List existing labels:**
   ```bash
   python3 scripts/ha_entity_metadata.py labels list
   ```

3. **Export ALL automations for analysis:**
   ```bash
   python3 scripts/ha_entity_metadata.py export --all > all_automations.yaml
   ```

4. **Plan label taxonomy** (Claude can help analyze automations and suggest labels)

5. **Create labels:**
   ```bash
   python3 scripts/ha_entity_metadata.py labels create climate --icon mdi:thermometer
   python3 scripts/ha_entity_metadata.py labels create scheduled --icon mdi:clock
   ```

6. **Apply labels to automations:**
   ```bash
   python3 scripts/ha_entity_metadata.py apply metadata.yaml
   ```

7. **Verify coverage:**
   ```bash
   python3 scripts/ha_entity_metadata.py stats
   ```

**Suggested label taxonomy:**

| Label         | Icon                | Purpose                     |
|---------------|---------------------|-----------------------------|
| climate       | mdi:thermometer     | Heating/cooling automations |
| lighting      | mdi:lightbulb       | Light control automations   |
| vacuum        | mdi:robot-vacuum    | Robot vacuum automations    |
| media         | mdi:television      | Media player automations    |
| notifications | mdi:bell            | Alert automations           |
| scheduled     | mdi:clock           | Time-triggered automations  |
| presence      | mdi:account         | Occupancy-based automations |
| safety        | mdi:shield          | Critical/safety automations |

### Common Mistakes to Avoid

1. **Not running `stats` first** - The `export` command without `--all` only shows automations that ALREADY have metadata. Always run `stats` to see the true count.

2. **Assuming export shows everything** - Use `export --all` to see ALL automations including those without any metadata assigned.

3. **Not verifying after bulk updates** - Always run `stats` after applying changes to confirm coverage.

4. **Forgetting labels must exist first** - Labels must be created before they can be assigned to automations.

5. **Changes are immediate via WebSocket** - No git push or HA restart needed. Changes apply instantly to HA's entity registry. Just refresh browser to see them.

## AI Assistant Integration

### Understanding HA Conversation Agent Limitations

**Critical insight:** The HA Conversation agent (OpenAI integration) only exposes entity **state** to the AI, NOT attributes. This means:
- ✅ AI sees: `sensor.nas_status` state = "Storage 93% full"
- ❌ AI cannot see: attributes like `cpu_percent`, `memory_percent`, `summary`

**Implication:** Rich attribute data is invisible to voice/chat assistants. Design sensors accordingly.

### AI-Optimized Sensor Pattern

Pack all key metrics into the **state** string (max 255 chars) instead of attributes:

```yaml
# BAD: Metrics in attributes (AI can't see these)
- name: "Device Status"
  state: "Healthy"
  attributes:
    cpu: "{{ states('sensor.cpu') }}"
    memory: "{{ states('sensor.memory') }}"

# GOOD: All metrics in state (AI can parse this)
- name: "Device Status"
  state: >-
    Device — Status: {{ status }}{% if issues %} ({{ issues | join(', ') }}){% endif %} ·
    CPU {{ cpu }}% · Mem {{ mem }}% · Temp {{ temp }}°C
```

**Format guidelines:**
- Start with device name and explicit status verdict: `Healthy`, `Warning`, `Critical`
- Include reason in parentheses: `Warning (Storage high)`
- Use `·` or `|` as separators (speakable)
- Label metrics clearly: "Storage 93% **used**" not just "93%"
- Keep under 200 chars for readability

**Example - NAS Status Sensor:**
```
Soundwave NAS — Status: Warning (Storage high) · Storage 93% used · CPU 5% · Mem 30% · System 40°C · Drives OK (37–38°C) · Security OK
```

### Exposing Entities to Conversation Agent

**Two different systems - don't confuse them:**

| File | Purpose |
|------|---------|
| `.storage/homeassistant.exposed_entities` | Alexa/Google Home exposure |
| `.storage/core.entity_registry` → `options.conversation.should_expose` | **Conversation agent (OpenAI)** |

**To expose an entity to the AI assistant via WebSocket:**

```python
import asyncio
import json
import websockets

async def expose_entity(entity_id):
    uri = f"ws://{HASS_HOST}:8123/api/websocket"
    async with websockets.connect(uri) as ws:
        # Auth
        await ws.recv()  # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": HASS_TOKEN}))
        await ws.recv()  # auth_ok

        # Expose to conversation agent
        await ws.send(json.dumps({
            "id": 1,
            "type": "homeassistant/expose_entity",
            "assistants": ["conversation"],
            "entity_ids": [entity_id],
            "should_expose": True
        }))
        result = await ws.recv()
        return json.loads(result).get('success')

asyncio.run(expose_entity("sensor.nas_status"))
```

**Note:** Changes take effect immediately - no restart needed.

### Testing Conversation Agent

Test AI assistant responses via curl:

```bash
# Ask the assistant a question
curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  "$HASS_SERVER/api/conversation/process" \
  -d '{"agent_id":"conversation.your_agent", "text":"How is the NAS doing?"}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['response']['speech']['plain']['speech'])"
```

**Find your agent_id:**
```bash
hass-cli state list | grep conversation
# Example: conversation.anna
```

### Synology DSM Status Reference

When creating sensors for Synology NAS, handle all possible states:

**Volume Status:**
| Status | Severity | Meaning |
|--------|----------|---------|
| `normal` | OK | Volume healthy |
| `attention` | Warning | Needs attention (e.g., >90% full) |
| `degraded` | Critical | RAID degraded (drive failed, array functional) |
| `crashed` | Critical | RAID failed (data at risk) |
| `repairing` | Info | RAID rebuilding |

**Drive Status:**
| Status | Severity | Meaning |
|--------|----------|---------|
| `normal` / `healthy` | OK | Drive healthy |
| `warning` | Warning | Issues detected, bad sectors |
| `critical` | High | Critical issues |
| `failing` | Critical | Severe issues, integrity not guaranteed |
| `crashed` | Critical | Drive removed from pool |

**Security Status (binary_sensor):**
- `off` = Security OK
- `on` = Security Alert

## Android TTS Notifications

### Correct Service Call Format

When sending TTS notifications to Android phones via the Companion App, **all these fields are required**:

```yaml
action: notify.mobile_app_telefono_paolo
data:
  message: TTS
  data:
    ttl: 0
    priority: high
    media_stream: alarm_stream_max
    tts_text: "Your message here"
```

**Critical fields:**
- `ttl: 0` - Prevents notification delay/suppression in doze mode
- `priority: high` - Ensures immediate delivery
- `media_stream: alarm_stream_max` - Plays at maximum volume on alarm stream
- `tts_text` - The actual text to speak (NOT `message` or `title`)

**Common mistakes:**
- ❌ Missing `ttl: 0` and `priority: high` → notification may be delayed or silent
- ❌ Using `message:` for the spoken text → must use `tts_text:` inside nested `data:`
- ❌ Wrong indentation → YAML parsing errors

### Pronunciation Workarounds

Android TTS does **NOT** support SSML tags. For proper name pronunciation issues:

| Problem | Solution | Example |
|---------|----------|---------|
| Name spelled letter-by-letter | Add/double vowels | "Ada" → "Aada" |
| Acronym-like words | Use lowercase or accents | "ADA" → "Àda" |
| Foreign words mispronounced | Phonetic spelling | Use intuitive spellings |

**Note:** The TTS engine is controlled by Android device settings (Settings → Accessibility → Text-to-speech), not by Home Assistant.

---

This skill encapsulates efficient Home Assistant management workflows developed through iterative optimization and real-world dashboard development. Apply these patterns to any Home Assistant instance for reliable, fast, and safe configuration management.
