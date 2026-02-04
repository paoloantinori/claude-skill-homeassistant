# 10. File Organization & Include Patterns

**Home Assistant Manager - File Organization Guide**

## 🚨 CRITICAL RULE: ALWAYS Check configuration.yaml First

**BEFORE creating or deploying ANY file, you MUST:**

1. Read the relevant section of `configuration.yaml`
2. Identify the include type for that component
3. Create/deploy to the CORRECT location

**Consequences of getting it wrong:**
- Changes not active (HA loads from different location)
- Requires HA restart to fix (NOT reload!)
- Wasted time debugging why "nothing happened"

---

## Include Types Reference

| Include Type | Syntax | File Location | Example |
|-------------|--------|---------------|---------|
| **Single file** | `!include filename.yaml` | `filename.yaml` (root) | `automation: !include automations.yaml` |
| **Directory merge** | `!include_dir_merge_named dirname` | `dirname/entity.yaml` | `input_boolean: !include_dir_merge_named input_boolean` |
| **Directory list** | `!include_dir_list dirname` | `dirname/entity.yaml` | `automation: !include_dir_list automations` |
| **Directory merge list** | `!include_dir_merge_list dirname` | `dirname/entity.yaml` | `sensor: !include_dir_merge_list sensors` |

---

## Common Patterns (This User's Configuration)

### Helper Entities (Use DIRECTORIES)

```yaml
# From configuration.yaml:
input_boolean: !include_dir_merge_named input_boolean
input_datetime: !include_dir_merge_named input_datetime
input_number: !include_dir_merge_named input_number
input_select: !include_dir_merge_named input_select
input_text: !include_dir_merge_named input_text
```

**✅ CORRECT deployment:**
```bash
# Deploy to directory
scp input_boolean/my_helper.yaml ha:/homeassistant/input_boolean/
hass-cli service call input_boolean.reload
```

**❌ WRONG deployment:**
```bash
# Deploy to single file (changes NOT active!)
scp input_boolean.yaml ha:/homeassistant/
# Requires RESTART to fix
```

### Automation & Scripts (Use BOTH)

```yaml
# From configuration.yaml:
automation single: !include automations.yaml
automation: !include_dir_merge_list automations
script single: !include scripts.yaml
script: !include_dir_merge_named scripts
```

**Pattern:** Single file for main definition, directories for organized files.

### Templates (Use DIRECTORY LIST)

```yaml
# From configuration.yaml:
template: !include_dir_merge_list templates
```

**✅ CORRECT:** `templates/my_template.yaml`
**❌ WRONG:** `templates.yaml`

---

## Pre-Deployment Checklist

**Before deploying ANY file:**

```bash
# Step 1: Check configuration.yaml
grep -A 2 "input_boolean:" configuration.yaml

# Step 2: Identify include type
# Output: "input_boolean: !include_dir_merge_named input_boolean"
# Action: Deploy to input_boolean/ directory

# Step 3: Deploy to correct location
scp input_boolean/new_entity.yaml ha:/homeassistant/input_boolean/

# Step 4: Reload (NOT restart!)
hass-cli service call input_boolean.reload
```

---

## How to Check Include Type

**Method 1: Grep for component**
```bash
grep -A 2 "input_boolean:" configuration.yaml
```

**Method 2: Read configuration.yaml**
- Search for the component name
- Check the `!include` directive
- Use the reference table above

**Method 3: Check existing files**
```bash
ls input_boolean/  # Directory exists → use directory
ls input_boolean.yaml  # File exists → use single file
```

---

## Examples: input_boolean Organization

### User's Actual Setup

**configuration.yaml:**
```yaml
input_boolean: !include_dir_merge_named input_boolean
```

**Directory structure:**
```
hassio/
├── configuration.yaml          # Defines: !include_dir_merge_named input_boolean
├── input_boolean/              # ← HA loads from HERE
│   ├── paolo_staleness_latch.yaml
│   ├── test_bayes.yaml
│   └── other_helpers.yaml
└── input_boolean.yaml          # ← NOT used by HA (would require restart)
```

### Creating New input_boolean

**✅ CORRECT workflow:**
```bash
# 1. Check configuration.yaml first
grep "input_boolean:" configuration.yaml
# Output: !include_dir_merge_named input_boolean

# 2. Create file in directory
cat > input_boolean/new_helper.yaml << 'EOF'
new_helper:
  name: "New Helper"
  icon: mdi:helper
EOF

# 3. Deploy to directory
scp input_boolean/new_helper.yaml ha:/homeassistant/input_boolean/

# 4. Reload (NOT restart!)
hass-cli service call input_boolean.reload
```

**❌ WRONG workflow:**
```bash
# 1. Assumes single file without checking
cat > input_boolean.yaml << 'EOF'
new_helper:
  name: "New Helper"
EOF

# 2. Deploys to wrong location
scp input_boolean.yaml ha:/homeassistant/

# 3. Changes NOT active - HA loads from input_boolean/ directory
# 4. Requires HA RESTART to fix (bad!)
```

---

## Quick Decision Tree

```
Need to create helper entity?
├─ YES → Check configuration.yaml FIRST
│         ├─ !include_dir_merge_named X → Create X/entity.yaml
│         ├─ !include_dir_list X → Create X/entity.yaml
│         └─ !include X.yaml → Create X.yaml
└─ NO → Proceed with task
```

---

## Key Takeaways

1. **ALWAYS check configuration.yaml first** - never assume
2. **Directory vs single file matters** - HA only loads from one location
3. **Wrong location = silent failure** - Changes not active, no error message
4. **Fix requires RESTART** - Reload won't help after wrong deployment
5. **This user uses directories** - input_boolean/, input_number/, etc.
