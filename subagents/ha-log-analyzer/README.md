# HA Log Analyzer - Integration Guide

**Purpose**: Complete guide for using the HA Log Analyzer subagent

---

## Overview

The **HA Log Analyzer** is a specialized subagent that handles all Home Assistant log analysis tasks. It is automatically delegated to by the HA Manager skill when log-related operations are needed.

**Location**: `.claude/subagents/ha-log-analyzer/`

**Parent Skill**: HA Manager (`.claude/skills/home-assistant-manager/`)

---

## Auto-Delegation Triggers

The HA Manager skill automatically delegates to this subagent when:

### Keyword Triggers
- "check logs"
- "log errors"
- "analyze logs"
- "automation fired?"
- "did it work?"
- "startup issues"
- "monitor logs"
- "any errors in the logs?"

### Context Triggers
- After `hass-cli service call automation.reload`
- After `hass-cli service call script.reload`
- After `hass-cli service call template.reload`
- After `hass-cli service call automation.trigger`

### Explicit Requests
- "Check for errors in the logs"
- "Monitor logs for pattern X"
- "Did automation Y fire successfully?"
- "Is HA starting cleanly?"
- "What's in the logs?"

---

## Usage Examples

### Example 1: Post-Deployment Error Check

**Scenario**: You just deployed and reloaded automations

```bash
$ hass-cli service call automation.reload
# HA Manager skill automatically delegates to ha-log-analyzer
```

**Subagent output**:
```
[STATUS] ✅ Post-Deployment Log Check Complete

Errors: 0 | Warnings: 0 | Time: 14:32:18

✅ No errors detected in last 50 log lines.
```

---

### Example 2: Automation Execution Verification

**Scenario**: You manually triggered an automation and want to verify it executed

```bash
$ hass-cli service call automation.trigger --arguments entity_id=automation.notify_test
$ "Did it fire?"
# HA Manager skill delegates to ha-log-analyzer for execution trace
```

**Subagent output**:
```
[STATUS] ✅ Automation Execution Trace Complete

Automation: automation.notify_test
Duration: 4.2 seconds
Result: SUCCESS

Execution trace:
✅ 14:32:15: Triggered by: manual
✅ 14:32:16: Executing step 1: delay
✅ 14:32:18: Executing step 2: notify.telegram
✅ 14:32:19: Completed successfully
```

---

### Example 3: Startup Health Check

**Scenario**: You just restarted HA and want to verify clean startup

```bash
$ "Check if HA started cleanly"
# HA Manager skill delegates to ha-log-analyzer
```

**Subagent output**:
```
[STATUS] ✅ Startup Health Check Complete

HA Container: Up 5 minutes
Startup errors: 0
Unavailable entities: 2

Unavailable entities (may be normal):
  - sensor.offline_sensor_1
  - binary_sensor.offline_device

✅ Home Assistant started cleanly
⚠️ 2 entities unavailable (likely offline devices)
```

---

### Example 4: Real-Time Log Monitoring

**Scenario**: You're debugging and want to watch logs for a specific automation

```bash
$ "Monitor logs for automation.gps_update"
# HA Manager skill delegates to ha-log-analyzer
```

**Subagent output**:
```
[STATUS] 🔄 Real-Time Log Monitoring (auto-exit on 20 matches or 60s)

Monitoring for: automation.gps_update

✅ 14:32:15: Triggered automation.gps_update
✅ 14:32:16: Executing action device_tracker.update
✅ 14:32:17: Completed automation.gps_update

[STATUS] Monitoring complete: 3 matches, exited after 2 seconds
```

---

### Example 5: Error Diagnosis

**Scenario**: Post-deployment check found an error

```bash
$ hass-cli service call automation.reload
# HA Manager skill delegates to ha-log-analyzer
```

**Subagent output**:
```
[STATUS] 🚨 Post-Deployment Log Check Complete

Errors: 1 | Warnings: 0 | Time: 14:32:18

🚨 ERROR: Failed to generate automation

   Location: automation.my_automation (line 45)
   Issue: Template variable error: 'undefined_var' is not defined

   → Action: Check automation.my_automation template for undefined variables
   → Test: ssh ha "ha core check"
   → Reference: HA Manager skill docs/06_common_mistakes.md
```

---

## Workflows

### Workflow 1: Post-Deployment Error Check

**Purpose**: Check for errors immediately after reload

**Timeout**: 10 seconds (quick check)

**Steps**:
1. Wait 2 seconds for reload to complete
2. Fetch last 50 log lines
3. Parse for errors and warnings
4. Return structured diagnosis

**Output**: `[STATUS]` with error/warning counts and suggested actions

---

### Workflow 2: Automation Execution Trace

**Purpose**: Verify automation executed successfully

**Timeout**: 30 seconds (automation should complete within this time)

**Steps**:
1. Get automation name from context
2. Monitor logs for automation execution
3. Parse execution trace (trigger → actions → completion)
4. Return structured trace with success/failure status

**Output**: `[STATUS]` with execution timeline and result

---

### Workflow 3: Startup Health Check

**Purpose**: Verify clean HA startup

**Timeout**: 15 seconds

**Steps**:
1. Check HA container status (docker ps)
2. Fetch last 100 log lines
3. Parse for startup errors
4. Check for unavailable entities
5. Return health summary

**Output**: `[STATUS]` with container uptime, error count, and unavailable entities

---

### Workflow 4: Real-Time Log Monitor

**Purpose**: Watch logs live for specific patterns

**Timeout**: 60 seconds (default), or until 20 matches

**Steps**:
1. Get search pattern from user
2. Monitor logs with timeout AND match limit
3. Parse matching log lines
4. Return matches with timestamps

**Output**: `[STATUS]` with match count and log excerpts

---

## Output Format Standards

All subagent outputs follow this structure:

```
[STATUS] [emoji] Brief Status Title

Key metrics or context

Body:
  ✅ Success indicators
  ⚠️ Warnings (with → Action recommendations)
  🚨 Errors (with → Action recommendations)

[STATUS] Next steps or closing statement
```

**Emojis**:
- ✅ Success / Clean
- ⚠️ Warning / Caution
- 🚨 Error / Critical
- 🔄 In Progress / Monitoring
- ℹ️ Info / Note

---

## Error Pattern Detection

The subagent maintains a library of known error patterns:

| Pattern | Diagnosis | Action |
|---------|-----------|--------|
| `Template variable warning` | Undefined variable in template | Check template for typos |
| `state_attr() returns None` | Wrong access method for core properties | Use `states.entity.property` |
| `Invalid data for call_service` | Service call parameters incorrect | Check service schema |
| `Failed to generate automation` | YAML syntax error | Run `ha core check` |
| `Entity not found` | Referenced entity doesn't exist | Verify entity ID |
| `No matching config entries to reload` | Wrong reload service | Use `<domain>.reload` |

**See also**: `.claude/subagents/ha-log-analyzer/patterns/error_patterns.md` for complete error pattern library

---

## Safety Rules

**MANDATORY rules enforced by subagent**:

1. **ALWAYS use timeouts**: Every `tail -f` wrapped with `timeout X` (max 120s)
2. **VisualHostKey=no**: All SSH commands use `ssh -oVisualHostKey=no ha`
3. **hass-cli preferred**: Use `hass-cli`, never curl
4. **Exit cleanly**: Never block waiting for user input
5. **Source .env**: Always source environment before hass-cli

**Inherited from HA Manager skill**:
- NEVER restart without asking
- Validate before deploy
- Prefer reload over restart
- Check logs within 30s after reload

---

## Direct Subagent Invocation

The subagent is normally invoked automatically by the HA Manager skill. However, you can invoke it directly if needed:

**Direct invocation** (advanced):
```bash
# Access subagent prompt directly
.claude/subagents/ha-log-analyzer/PROMPT.md

# Use for:
# - Custom log analysis scenarios
# - Extended monitoring beyond default timeouts
# - Testing subagent behavior
```

**Recommended**: Let HA Manager skill handle delegation automatically for consistency.

---

## Relocation Notes

**Current location**: `.claude/subagents/ha-log-analyzer/`

**Future location** (if skill-embedded subagents are supported):
`.claude/skills/home-assistant-manager/subagents/ha-log-analyzer/`

**Relocation steps**:
1. Move directory: `mv .claude/subagents/ha-log-analyzer .claude/skills/home-assistant-manager/subagents/`
2. Update trigger paths in HA Manager skill SKILL.md
3. Test subagent loading and execution
4. Update PROMPT.md with new location

**Rationale**: Tightly coupled to HA domain, better organization as part of skill

---

## Troubleshooting

### Subagent Not Activating

**Symptom**: Log analysis not triggering after reload

**Diagnosis**:
1. Check subagent files exist: `ls -la .claude/subagents/ha-log-analyzer/`
2. Verify PROMPT.md is readable
3. Check HA Manager skill SKILL.md has delegation section

**Fix**:
- Re-create subagent directory if missing
- Re-add delegation section to SKILL.md if removed

---

### Timeout Too Short

**Symptom**: Subagent exits before seeing error in logs

**Diagnosis**: Default timeout may be too short for slow operations

**Fix**:
- Post-deploy: 10s (usually sufficient)
- Automation trace: 30s (usually sufficient)
- Real-time monitor: Can specify custom timeout: `"monitor logs for X with timeout 120"`

---

### Missing Error Patterns

**Symptom**: Error in logs not recognized by subagent

**Diagnosis**: Error pattern not in library

**Fix**:
1. Add new error pattern to: `.claude/subagents/ha-log-analyzer/patterns/error_patterns.md`
2. Follow pattern template in that file
3. Include diagnosis, common causes, and suggested actions

---

## Related Documentation

- **HA Manager Skill**: `.claude/skills/home-assistant-manager/SKILL.md`
- **Critical Safety**: `.claude/skills/home-assistant-manager/docs/01_critical_safety.md`
- **Common Mistakes**: `.claude/skills/home-assistant-manager/docs/06_common_mistakes.md`
- **Automation Testing**: `.claude/skills/home-assistant-manager/docs/04_automation_testing.md`
- **Error Patterns**: `.claude/subagents/ha-log-analyzer/patterns/error_patterns.md`

---

## Development

### Adding New Workflows

To add a new workflow:

1. Create workflow file: `.claude/subagents/ha-log-analyzer/workflows/new_workflow.yaml`
2. Define steps with timeouts and filters
3. Add output template
4. Update PROMPT.md with workflow documentation
5. Test workflow with realistic scenarios

### Adding New Error Patterns

To add a new error pattern:

1. Edit: `.claude/subagents/ha-log-analyzer/patterns/error_patterns.md`
2. Follow template format:
   ```markdown
   ### Pattern: [Descriptive Name]
   **Log message**: `[actual log message]`
   **Diagnosis`: [what is the error?]
   **Common causes**: [list]
   **Suggested actions**: [numbered list]
   **Reference**: [link to docs]
   ```
3. Add to quick reference table
4. Test pattern detection with real log output

---

## Summary

**HA Log Analyzer** provides:
- ✅ Automated log analysis after deployments
- ✅ Automation execution verification
- ✅ Startup health checks
- ✅ Real-time log monitoring with auto-exit
- ✅ Known error pattern detection
- ✅ Actionable diagnosis and suggested fixes
- ✅ Timeout enforcement (never hangs)
- ✅ Structured output with clear status indicators

**Best used via**: HA Manager skill auto-delegation

**Direct access**: `.claude/subagents/ha-log-analyzer/PROMPT.md`
