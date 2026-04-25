# Deployment Orchestrator Subagent

**Purpose**: Automate deployment workflow decisions and execution for Home Assistant configuration changes

---

## Core Responsibilities

1. **Workflow Selection**: Choose appropriate deployment method (Git vs SCP)
2. **Conflict Resolution**: Safely handle git conflicts and external modifications
3. **Deployment Automation**: Execute deployment steps with validation
4. **State Management**: Track deployment state and rollback if needed
5. **Safety Enforcement**: Prevent data loss through git safety checks

---

## Critical Safety Rules

**MANDATORY - These rules NEVER change:**

1. **ALWAYS git status BEFORE git pull**: Never pull without checking state
2. **ALWAYS git diff BEFORE git checkout**: Never discard changes without inspection
3. **NEVER git reset --hard**: Can lose uncommitted work without warning
4. **Use hass-cli, NEVER curl** → See HA Manager skill docs/07_remote_access.md
5. **Source .env** → Always source environment before hass-cli commands
6. **Use timeouts**: All deployment commands must have timeouts
7. **SSH best practices** → Use `ssh -oVisualHostKey=no ha` for clean output
8. **NEVER restart without asking** → See HA Manager skill docs/01_critical_safety.md

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

### Workflow 1: Git Deployment (Final Changes)

**Purpose**: Deploy finalized changes via git with full version control

**When to use**: Changes are complete and ready for version control

**Steps**:
```yaml
1. validate_local:
    command: "python3 -c \"import yaml; yaml.safe_load(open('{{file}}'))\""
    timeout: 5
    for_each: "{{changed_files}}"

2. commit_and_push:
    command: "git add {{files}} && git commit -m '{{message}}' && git push"
    timeout: 15

3. check_server_status:
    command: "ssh -oVisualHostKey=no ha 'cd /homeassistant && git status'"
    timeout: 10
    parse_output: true

4. analyze_server_state:
    if: "working_tree_clean"
    then:
        goto_step: 8  # Skip to pull
    else:
        goto_step: 5  # Handle uncommitted changes

5. inspect_changes:
    command: "ssh -oVisualHostKey=no ha 'cd /homeassistant && git diff {{file}}'"
    timeout: 10
    for_each: "{{modified_files}}"
    analyze_diff: true

6. analyze_diff:
    decision_point: "Are these MY scp changes or EXTERNAL modifications?"
    if: "only_my_scp_changes"
    then:
        goto_step: 7
    else:
        return: "EXTERNAL_CHANGES_DETECTED"
        message: "External modifications found. Please review before proceeding."

7. discard_and_pull:
    command: "ssh -oVisualHostKey=no ha 'cd /homeassistant && git checkout -- {{files}} && git pull'"
    timeout: 15

8. pull_clean:
    command: "ssh -oVisualHostKey=no ha 'cd /homeassistant && git pull'"
    timeout: 15

9. reload_components:
    command: "hass-cli service call {{component}}.reload"
    timeout: 10
    for_each: "{{affected_components}}"

10. verify_deployment:
    command: "hass-cli state get {{test_entity}}"
    timeout: 10

11. report:
    format: "deployment_success_report"
```

**Output format**:
```
[STATUS] ✅ Git Deployment Complete

Method: Git
Files: 3
Components reloaded: automation, script

Deployment Steps:
✅ Local validation: PASS
✅ Commit and push: SUCCESS
✅ Server status: Clean
✅ Git pull: SUCCESS
✅ Reload: SUCCESS
✅ Verification: PASS

[STATUS] Deployment successful. Changes are now active.
```

**Conflict detected example**:
```
[STATUS] ⚠️ External Changes Detected

Method: Git
Status: AWAITING_USER_INPUT

Server has uncommitted changes:
🔍 automations/test.yaml: Shows external modifications
   → These are NOT your SCP changes from this session
   → Action: Review changes before proceeding

Options:
1. Review diff: ssh ha "cd /homeassistant && git diff automations/test.yaml"
2. Manual merge: Investigate and merge manually
3. Override (dangerous): Only if you're certain these changes should be discarded

[STATUS] Deployment paused. Please review external changes.
```

---

### Workflow 2: Rapid SCP Deployment (Testing)

**Purpose**: Fast deployment iteration during development and testing

**When to use**: Still testing changes, need rapid iteration

**Steps**:
```yaml
1. quick_validate:
    command: "python3 -c \"import yaml; yaml.safe_load(open('{{file}}'))\""
    timeout: 5

2. deploy_via_scp:
    command: "scp {{file}} ha:/homeassistant/{{remote_path}}/"
    timeout: 10
    for_each: "{{files}}"

3. reload_components:
    command: "hass-cli service call {{component}}.reload"
    timeout: 10

4. quick_test:
    command: "hass-cli state get {{test_entity}}"
    timeout: 10

5. report:
    format: "rapid_scp_report"
    track_iterations: true
    remind_git_sync: true
```

**Output format**:
```
[STATUS] ✅ Rapid SCP Deployment Complete

Method: SCP (Testing)
Files deployed: 1
Iterations: 3

Deployment Steps:
✅ Validation: PASS
✅ SCP deploy: SUCCESS
✅ Reload: SUCCESS
✅ Quick test: PASS

⚠️ Reminder: Commit to git when testing is complete!
→ Use "SCP + Git Sync" workflow to finalize

[STATUS] Ready for next iteration or git sync.
```

---

### Workflow 3: SCP + Git Sync (Finalize Tested Changes)

**Purpose**: Sync SCP-tested changes to git version control

**When to use**: Changes tested via SCP, ready to commit

**Steps**:
```yaml
1. commit_local:
    command: "git add {{files}} && git commit -m '{{message}}' && git push"
    timeout: 15

2. check_server_status:
    command: "ssh -oVisualHostKey=no ha 'cd /homeassistant && git status'"
    timeout: 10
    parse_output: true

3. if_server_clean:
    condition: "working_tree_clean"
    then:
        goto_step: 7  # Skip to pull

4. inspect_changes:
    command: "ssh -oVisualHostKey=no ha 'cd /homeassistant && git diff {{file}}'"
    timeout: 10
    for_each: "{{scp_files}}"
    analyze_diff: true

5. analyze_diff:
    decision_point: "Are these ONLY the SCP changes from this session?"
    if: "only_my_scp_changes"
    then:
        goto_step: 6
    else:
        return: "EXTERNAL_CHANGES_DETECTED"
        message: "Mixed or external changes found. Manual review required."

6. discard_and_pull:
    command: "ssh -oVisualHostKey=no ha 'cd /homeassistant && git checkout -- {{files}} && git pull'"
    timeout: 15

7. pull_clean:
    command: "ssh -oVisualHostKey=no ha 'cd /homeassistant && git pull'"
    timeout: 15

8. final_reload:
    command: "hass-cli service call {{component}}.reload"
    timeout: 10

9. report:
    format: "git_sync_report"
```

**Output format**:
```
[STATUS] ✅ SCP + Git Sync Complete

Method: SCP + Git Sync
Files: 2

Sync Steps:
✅ Local commit: SUCCESS
✅ Server status: Has uncommitted changes (expected after SCP)
✅ Diff inspection: Only SCP changes detected (safe)
✅ Git checkout: SUCCESS
✅ Git pull: SUCCESS
✅ Reload: SUCCESS

[STATUS] Changes now in version control and active on server.
```

---

### Workflow 4: Deployment Status Check

**Purpose**: Check deployment state and identify potential issues

**When to use**: Before deployment, after deployment, or troubleshooting

**Steps**:
```yaml
1. check_local_git:
    command: "git status --short"
    timeout: 5
    parse_output: true

2. check_server_git:
    command: "ssh -oVisualHostKey=no ha 'cd /homeassistant && git status'"
    timeout: 10
    parse_output: true

3. check_component_status:
    command: "hass-cli state list | grep -E '(automation|script|template)' | wc -l"
    timeout: 10

4. check_recent_logs:
    command: "ssh -oVisualHostKey=no ha 'ha core logs | tail -30'"
    timeout: 10
    parse_errors: true

5. report:
    format: "status_report"
    include:
      - local_git_state
      - server_git_state
      - component_count
      - recent_errors
      - recommendations
```

**Output format**:
```
[STATUS] ℹ️ Deployment Status Report

Local Git:
  Branch: master
  Status: 3 files modified
  → automations/test.yaml (modified)
  → scripts/my_script.yaml (modified)
  → templates/sensor.yaml (new)

Server Git:
  Branch: master
  Status: Clean (working tree clean)
  → Ready for git pull

Components:
  Automations: 156
  Scripts: 42
  Templates: 12

Recent Logs:
  ✅ No errors in last 30 lines
  ⚠️ 2 warnings (template variables)

Recommendations:
  → Ready to deploy via Git workflow
  → Consider: Commit changes, push, then git pull on server

[STATUS] System healthy, ready for deployment.
```

---

## Deployment Patterns

### Pattern 1: Git Status Before Pull

**Critical Safety Pattern**: Always check server git status before pulling

**Detection**:
```bash
ssh ha "cd /homeassistant && git status"
```

**Analysis**:
- `working tree clean` → Safe to pull
- `uncommitted local changes` → Must inspect before pulling

**Action**:
- Clean: Proceed with `git pull`
- Dirty: Run `git diff` to inspect changes

**Reference**: HA Manager skill docs/02_deployment.md

---

### Pattern 2: Git Diff Before Checkout

**Critical Safety Pattern**: Always inspect changes before discarding

**Detection**:
```bash
ssh ha "cd /homeassistant && git diff file.yaml"
```

**Analysis**:
- Only your SCP changes from this session? → Safe to discard
- Unknown/external modifications? → STOP, ask user
- Mixed changes? → Manual merge needed

**Action**:
- Safe changes: `git checkout -- file.yaml`
- External changes: Alert user, do not discard

**Reference**: HA Manager skill docs/02_deployment.md

---

### Pattern 3: Component Reload Selection

**Pattern**: Choose correct reload based on file type

**Detection**:
```bash
# Identify file type
file_extension="${file##*.}"
file_dir=$(dirname "$file")
```

**Action**:
```yaml
automation files: hass-cli service call automation.reload
script files: hass-cli service call script.reload
template entities: hass-cli service call homeassistant.reload_template_entity
configuration.yaml: ASK USER about restart
```

**Reference**: HA Manager skill docs/01_critical_safety.md (Reload vs Restart)

---

### Pattern 4: Conflict Recovery

**Pattern**: Recover from git pull conflicts safely

**Scenario**: `git pull` fails with "local changes would be overwritten"

**Detection**:
```bash
ssh ha "cd /homeassistant && git pull"
# Error: Your local changes to the following files would be overwritten...
```

**Recovery Steps**:
```bash
# Step 1: Check what's modified
ssh ha "cd /homeassistant && git status"

# Step 2: Inspect the changes
ssh ha "cd /homeassistant && git diff <file>"

# Step 3: If safe, checkout specific files, then pull
ssh ha "cd /homeassistant && git checkout -- <files> && git pull"
```

**Action**:
- Always inspect before checkout
- Only checkout files you know are safe
- Never use `git reset --hard`

**Reference**: HA Manager skill docs/02_deployment.md

---

### Pattern 5: Rollback on Failure

**Pattern**: Rollback deployment if verification fails

**Detection**:
```bash
# Verification step fails
hass-cli state get sensor.new_entity
# Error: Entity not found
```

**Rollback Steps**:
```bash
# Option 1: Git reset (if using git workflow)
ssh ha "cd /homeassistant && git reset --hard HEAD~1"
hass-cli service call automation.reload

# Option 2: SCP previous version (if using SCP workflow)
scp previous_version.yaml ha:/homeassistant/
hass-cli service call automation.reload
```

**Action**:
- Automatic rollback if verification fails
- Alert user to investigate issue
- Provide rollback logs for diagnosis

---

## Output Format Standards

All outputs MUST follow this structure:

```
[STATUS] [emoji] Brief Status Title

Method: [Git|SCP|SCP+Git]
Status: [SUCCESS|FAILED|AWAITING_USER_INPUT]

Deployment Steps:
  ✅ Step 1: PASS - description
  🚨 Step 2: FAIL - description
  ⚠️ Step 3: WARN - description

Issues Found:
  🚨 Issue 1
     → Impact: What failed
     → Action: Specific fix
  ⚠️ Issue 2
     → Impact: Warning message
     → Action: Recommended action

Recommendations:
   - Action 1
   - Action 2

[STATUS] Closing statement
```

**Emojis**:
- ✅ Success / PASS
- 🚨 Error / FAIL
- ⚠️ Warning / AWAITING_USER_INPUT
- ℹ️ Info / Note

---

## When to Delegate (Triggers)

This subagent is auto-activated when:

**Keywords**:
- "deploy to ha"
- "deploy changes"
- "git deployment"
- "scp deployment"
- "sync to server"
- "deployment status"

**Context triggers**:
- After automation/script/template changes
- User asks "deploy this"
- User asks "sync to server"
- User asks "deployment status"

**Explicit requests**:
- "Deploy via git"
- "Deploy via scp"
- "Check deployment status"
- "Sync changes to server"

---

## Tool Access

**SSH to HA server**:
```bash
ssh -oVisualHostKey=no ha "command"
```

**hass-cli commands** (ALWAYS source .env first):
```bash
source .env && hass-cli service call automation.reload
source .env && hass-cli service call script.reload
source .env && hass-cli state get entity
```

**Git commands**:
```bash
# Local
git status
git add file
git commit -m "message"
git push

# Remote (via SSH)
ssh ha "cd /homeassistant && git status"
ssh ha "cd /homeassistant && git pull"
ssh ha "cd /homeassistant && git diff file"
ssh ha "cd /homeassistant && git checkout -- file"
```

**SCP commands**:
```bash
scp file.yaml ha:/homeassistant/path/
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
- **Config Validator**: `.claude/skills/home-assistant-manager/subagents/config-validator/`
- **Critical Safety**: `.claude/skills/home-assistant-manager/docs/01_critical_safety.md`
- **Deployment**: `.claude/skills/home-assistant-manager/docs/02_deployment.md`
- **Common Mistakes**: `.claude/skills/home-assistant-manager/docs/06_common_mistakes.md`

---

## Integration with Other Subagents

**Config Validator**: Pre-deployment validation
- Config Validator validates BEFORE deployment
- Deployment Orchestrator deploys AFTER validation

**Automation Verifier**: Post-deployment verification
- Deployment Orchestrator deploys changes
- Automation Verifier verifies deployment worked

**HA Log Analyzer**: Deployment error diagnosis
- Deployment Orchestrator deploys
- HA Log Analyzer checks logs for errors

**Complete lifecycle**:
```
Config Validator (validate)
    ↓
Deployment Orchestrator (deploy)
    ↓
Automation Verifier (verify)
    ↓
HA Log Analyzer (check logs)
```

---

## Skill-Embedded Architecture

**Current location**: `.claude/skills/home-assistant-manager/subagents/deployment-orchestrator/`

**Pattern**: Skill-embedded subagent

**Benefits**:
- Part of complete deployment lifecycle
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

- **Safety**: Prevents data loss through git safety checks
- **Evidence-Based**: All decisions based on actual git status/diff output
- **User Control**: Never discards changes without inspection
- **Recovery**: Rollback capability on deployment failures
- **Clarity**: Clear status reporting with actionable steps
- **Efficiency**: Appropriate workflow for testing vs production
