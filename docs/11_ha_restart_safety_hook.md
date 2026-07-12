# HA Restart Safety Hook

## 🚨 AUTOMATIC RESTART PROTECTION

**Status**: ✅ Active and Enforced

This project has a **mandatory safety hook** that blocks Home Assistant restart commands unless explicitly approved by the user.

### How It Works

A `PreToolUse` hook in `.claude/settings.json` intercepts all Bash commands before execution. If a restart command is detected without the `--user-approved` flag, the hook blocks it with exit code 2.

### Protected Commands

The following commands are **automatically blocked** unless approved:

```bash
# BLOCKED (requires --user-approved)
hass-cli service call homeassistant.restart
ssh ha "ha core restart"
hass-cli service call homeassistant.restart
```

### How to Approve a Restart

**Option 1: Add the approval flag**
```bash
hass-cli service call homeassistant.restart -- --user-approved
```

**Option 2: Ask the user directly**
```
"May I restart Home Assistant?"
```
Once the user says "yes" or "y", add `-- --user-approved` to the command.

### Hook Configuration

**Location**: `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/block-ha-restart.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**Script**: `.claude/hooks/block-ha-restart.sh` (executable)

### Why This Exists

This hook enforces the **HA Manager skill's #1 critical rule**: NEVER RESTART WITHOUT ASKING.

**Problem solved**: Prevents accidental restarts during active sessions, ensuring user approval before disruptive operations.

### Testing the Hook

```bash
# Should be BLOCKED
$ hass-cli service call homeassistant.restart
> 🚫 BLOCKED: Home Assistant restart requires explicit user approval

# Should be ALLOWED (after user approval)
$ hass-cli service call homeassistant.restart -- --user-approved
> [Success]
```

### Troubleshooting

**Hook not working?**

1. Verify hook is registered:
   ```bash
   /hooks
   ```

2. Check file exists and is executable:
   ```bash
   ls -la .claude/hooks/block-ha-restart.sh
   # Should show: -rwxr-xr-x (executable)
   ```

3. Test the hook directly:
   ```bash
   echo '{"tool_input":{"command":"hass-cli restart"}}' | .claude/hooks/block-ha-restart.sh
   # Should exit with code 2 and show blocking message
   ```

### Disabling the Hook

⚠️ **WARNING**: Disabling this hook removes an important safety mechanism.

**To temporarily disable**: Rename the hook file:
```bash
mv .claude/settings.json .claude/settings.json.disabled
```

**To re-enable**: Rename it back:
```bash
mv .claude/settings.json.disabled .claude/settings.json
```

### Related Documentation

- **Main Skill**: `.claude/skills/home-assistant-manager/SKILL.md`
- **Critical Safety**: `docs/01_critical_safety.md`
- **Research**: `.claude/claudedocs/claude_code_hooks_research_20260201.md`

### Git Status

Both hook files are tracked in git:
- `.claude/settings.json` - Hook configuration
- `.claude/hooks/block-ha-restart.sh` - Blocking script

They are **NOT** in `.gitignore`, ensuring the safety mechanism is version-controlled and shared with the team.
