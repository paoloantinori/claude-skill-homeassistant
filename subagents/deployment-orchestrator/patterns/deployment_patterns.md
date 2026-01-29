# Deployment Patterns Library

**Purpose**: Known deployment patterns with decision trees, safety checks, and error recovery

---

## Pattern 1: Git Status Before Pull

**Purpose**: Prevent git pull conflicts by checking server state first

**Critical Safety Pattern**: Always check server git status before pulling

**Detection**:
```bash
ssh ha "cd /homeassistant && git status"
```

**Analysis**:
- `working tree clean` → Safe to pull
- `uncommitted local changes` → Must inspect before pulling
- `Your branch is ahead of 'origin/master'` → Server has local commits

**Decision Tree**:
```
Check server git status
├─ working_tree_clean?
│  └─ YES → Proceed with git pull
└─ uncommitted changes?
   └─ YES → Run git diff to inspect changes
      ├─ Only your SCP changes? → Safe to discard and pull
      ├─ External modifications? → STOP, ask user
      └─ Mixed changes? → Manual merge needed
```

**Action**:
```bash
# Clean state
ssh ha "cd /homeassistant && git pull"

# Dirty state - must inspect first
ssh ha "cd /homeassistant && git diff file.yaml"
# Then decide based on diff analysis
```

**Reference**: HA Manager skill docs/02_deployment.md

---

## Pattern 2: Git Diff Before Checkout

**Purpose**: Prevent data loss by inspecting changes before discarding

**Critical Safety Pattern**: Never discard changes without inspection

**Detection**:
```bash
ssh ha "cd /homeassistant && git diff file.yaml"
```

**Analysis**:
- Only your SCP changes from this session? → Safe to discard
- Unknown/external modifications? → STOP, ask user
- Mixed changes (yours + external)? → Manual merge needed

**Decision Tree**:
```
Inspect git diff
├─ Recognize your changes?
│  ├─ YES → These are your SCP changes from this session
│  │  └─ Safe to discard: git checkout -- file.yaml
│  └─ NO → Unknown changes detected
│     └─ STOP: Ask user before discarding
└─ Mixed changes?
   └─ Both yours and external? → Manual merge required
```

**Evidence Analysis**:
- **Your SCP changes**: Recent timestamp (within last hour), matches your edits
- **External modifications**: Older timestamp, different style, unknown content
- **Mixed changes**: Some sections match your edits, others don't

**Action**:
```bash
# Safe to discard (only your changes)
ssh ha "cd /homeassistant && git checkout -- file.yaml && git pull"

# External changes detected - STOP
# Return error to user with diff excerpt
```

**Reference**: HA Manager skill docs/02_deployment.md

---

## Pattern 3: Component Reload Selection

**Purpose**: Choose correct reload based on file type

**Pattern**: Different file types require different reload commands

**Detection**:
```bash
# Identify file type
file_extension="${file##*.}"
file_dir=$(dirname "$file")
```

**Mapping**:
```yaml
File Type Patterns:
  automation files (*.yaml in automations/):
    → hass-cli service call automation.reload

  script files (*.yaml in scripts/):
    → hass-cli service call script.reload

  template entities (*.yaml in templates/):
    → hass-cli service call homeassistant.reload_template_entity

  configuration.yaml:
    → ASK USER about restart (CRITICAL: Never restart without asking)

  packages/*.yaml (may contain multiple types):
    → automation.reload + script.reload + template.reload
```

**Decision Tree**:
```
What file type changed?
├─ automation file?
│  └─ automation.reload
├─ script file?
│  └─ script.reload
├─ template entity?
│  └─ homeassistant.reload_template_entity
├─ configuration.yaml?
│  └─ ASK: "May I restart Home Assistant?"
└─ package file?
   └─ Reload all affected components
```

**Action**:
```bash
# Single component
hass-cli service call automation.reload

# Multiple components
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call homeassistant.reload_template_entity
```

**Reference**: HA Manager skill docs/01_critical_safety.md (Reload vs Restart)

---

## Pattern 4: Conflict Recovery

**Purpose**: Recover from git pull conflicts safely

**Scenario**: `git pull` fails with "local changes would be overwritten"

**Detection**:
```bash
ssh ha "cd /homeassistant && git pull"
# Error: Your local changes to the following files would be overwritten by merge:
```

**Recovery Steps**:
```bash
# Step 1: Check what's modified
ssh ha "cd /homeassistant && git status"

# Step 2: Inspect the changes
ssh ha "cd /homeassistant && git diff <file>"

# Step 3: Analyze diff
# - Only your SCP changes? → Safe to discard
# - External modifications? → Manual merge needed
# - Mixed changes? → Manual merge needed

# Step 4: If safe, checkout specific files, then pull
ssh ha "cd /homeassistant && git checkout -- <files> && git pull"
```

**One-Liner Recovery** (only if 100% certain):
```bash
# Use ONLY if you're certain these are your SCP changes
ssh ha "cd /homeassistant && git checkout -- file.yaml && git pull"
```

**Decision Tree**:
```
Git pull fails with conflict
├─ Inspect changes: git diff <file>
├─ Only your SCP changes?
│  └─ YES → checkout + pull (safe)
└─ External or mixed changes?
   └─ Manual merge required
      ├─ Ask user for guidance
      ├─ Do NOT auto-discard
      └─ Provide diff for review
```

**Action**:
- Always inspect before checkout
- Only checkout files you know are safe
- Never use `git reset --hard`

**Reference**: HA Manager skill docs/02_deployment.md

---

## Pattern 5: Rollback on Failure

**Purpose**: Rollback deployment if verification fails

**Scenario**: Deployment succeeded but verification failed

**Detection**:
```bash
# Verification step fails
hass-cli state get sensor.new_entity
# Error: Entity not found or state unexpected
```

**Rollback Options**:

**Option 1: Git Reset** (if using git workflow)
```bash
# Rollback to previous commit
ssh ha "cd /homeassistant && git reset --hard HEAD~1"
hass-cli service call automation.reload
```

**Option 2: SCP Previous Version** (if using SCP workflow)
```bash
# Revert to previous file version
scp previous_version.yaml ha:/homeassistant/path/
hass-cli service call automation.reload
```

**Option 3: Git Revert** (cleaner than reset)
```bash
# Revert last commit (preserves history)
ssh ha "cd /homeassistant && git revert HEAD"
hass-cli service call automation.reload
```

**Decision Tree**:
```
Verification fails
├─ What deployment method was used?
├─ Git workflow?
│  └─ Use git reset or git revert
├─ SCP workflow?
│  └─ SCP previous version
└─ Provide rollback logs
   └─ Include error details for diagnosis
```

**Action**:
- Automatic rollback if verification fails
- Alert user to investigate issue
- Provide rollback logs for diagnosis
- Do not proceed with further deployments

---

## Pattern 6: Deployment Method Selection

**Purpose**: Choose appropriate deployment method based on context

**Decision Tree**:
```
Ready to deploy?
├─ Still testing changes?
│  └─ YES → Use Rapid SCP workflow
│           - Fast iteration
│           - No version control yet
│           - Remind to commit when done
│
└─ Changes finalized?
   ├─ Already tested via SCP?
   │  └─ YES → Use SCP + Git Sync workflow
   │           - Commit tested changes
   │           - Sync to git
   │           - Clean server state
   │
   └─ First time deploying?
      └─ YES → Use Git workflow
                - Commit and push
                - Pull to server
                - Full version control
```

**Selection Criteria**:
```yaml
Use Rapid SCP when:
  - Still developing and testing
  - Need fast iteration
  - Changes not finalized
  - Don't care about version control yet

Use SCP + Git Sync when:
  - Changes tested via SCP
  - Ready to commit to version control
  - Server has SCP changes to sync
  - Want to clean server state

Use Git workflow when:
  - Changes are finalized
  - No prior SCP testing
  - Want full version control from start
  - Server state is clean
```

**Reference**: HA Manager skill docs/02_deployment.md

---

## Pattern 7: Safe File Path Handling

**Purpose**: Ensure files are deployed to correct locations

**Detection**:
```bash
# Check local file structure
local_file="automations/test/my_automation.yaml"
local_dir=$(dirname "$local_file")  # automations/test
remote_path="/homeassistant/$local_dir"
```

**Common Mistakes**:
```bash
# ❌ WRONG - deploys to wrong location
scp automations/test/my_automation.yaml ha:/homeassistant/
# Result: File at /homeassistant/my_automation.yaml (wrong location)

# ✅ CORRECT - preserves directory structure
scp automations/test/my_automation.yaml ha:/homeassistant/automations/test/
# Result: File at /homeassistant/automations/test/my_automation.yaml (correct)
```

**Pattern**:
```bash
# Extract relative path from project root
file="automations/test/my_automation.yaml"
remote_dir=$(dirname "$file")  # automations/test
filename=$(basename "$file")   # my_automation.yaml

# Deploy to correct location
scp "$file" "ha:/homeassistant/$remote_dir/$filename"
```

**Action**:
- Always preserve directory structure
- Use relative paths from project root
- Verify deployment location after SCP

---

## Pattern 8: Batch Deployment Optimization

**Purpose**: Deploy multiple files efficiently

**Pattern**: Batch operations for multiple files

**Sequential vs Batch**:
```bash
# ❌ SLOW - Sequential operations
scp file1.yaml ha:/homeassistant/automations/
# wait...
scp file2.yaml ha:/homeassistant/scripts/
# wait...
scp file3.yaml ha:/homeassistant/templates/
# wait...
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call homeassistant.reload_template_entity

# ✅ FASTER - Batch operations
scp file1.yaml ha:/homeassistant/automations/ &
scp file2.yaml ha:/homeassistant/scripts/ &
scp file3.yaml ha:/homeassistant/templates/ &
wait  # All SCP operations in parallel
hass-cli service call automation.reload
hass-cli service call script.reload
hass-cli service call homeassistant.reload_template_entity
```

**Batch Best Practices**:
```yaml
1. Group files by component:
   - All automation files → Deploy together
   - All script files → Deploy together
   - All template files → Deploy together

2. Batch SCP operations:
   - Use background processes (&)
   - Wait for all to complete
   - Reload once per component

3. Minimize reloads:
   - Reload automation once (not per file)
   - Reload script once (not per file)
   - Reload template once (not per file)
```

**Action**:
- Group files by component type
- Batch SCP operations with parallel execution
- Minimize reload operations
- Reload once per component (not per file)

---

## Quick Reference: Deployment Decision Tree

```
Deployment needed?
├─ Still testing?
│  └─ YES → Rapid SCP workflow
│           - scp → reload → test → repeat
│           - Remind: Commit when done
│
└─ Finalized changes?
   ├─ Tested via SCP already?
   │  └─ YES → SCP + Git Sync workflow
   │           - commit → push → status → diff → checkout → pull → reload
   │
   └─ First time deploying?
      └─ YES → Git workflow
                - commit → push → status → (dirty?) → diff → checkout → pull → reload
```

---

## Integration with Other Subagents

**Config Validator**:
- Deployment Orchestrator calls Config Validator before deployment
- Config Validator validates YAML, entities, services, templates
- Only deploys if validation passes

**Automation Verifier**:
- Deployment Orchestrator deploys changes
- Automation Verifier verifies deployment worked
- End-to-end testing of deployed automations

**HA Log Analyzer**:
- Deployment Orchestrator deploys changes
- HA Log Analyzer checks logs for errors
- Post-deployment health check

**Complete lifecycle**:
```
Config Validator (validate)
    ↓ (PASS)
Deployment Orchestrator (deploy)
    ↓ (SUCCESS)
Automation Verifier (verify)
    ↓ (PASS)
HA Log Analyzer (check logs)
```

---

## Error Recovery Quick Reference

| Error | Detection | Recovery |
|-------|-----------|----------|
| **Git pull conflict** | "local changes would be overwritten" | git diff → (if safe) git checkout → git pull |
| **External changes detected** | git diff shows unknown changes | STOP and ask user, do not discard |
| **Verification failed** | Entity not found or wrong state | Rollback (git reset or SCP previous) |
| **SCP connection failed** | "ssh: connection refused" | Check SSH connectivity, verify ha alias |
| **Reload failed** | "Service not found" | Check component name, use correct reload command |
| **YAML validation failed** | Python YAML error | Fix syntax errors before deployment |

---

## Safety Checklist

Before ANY deployment:
- [ ] Git status checked on server
- [ ] Git diff inspected (if server has changes)
- [ ] YAML syntax validated locally
- [ ] Component reload commands identified
- [ ] Verification entities selected
- [ ] Rollback plan prepared

After deployment:
- [ ] Verification passed
- [ ] Logs checked for errors
- [ ] Component reloaded successfully
- [ ] Entity states correct
- [ ] Rollback available if needed
