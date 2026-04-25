# Verification Patterns Library

**Purpose**: Known verification patterns for different automation types with diagnosis and suggested actions

---

## Notification Verification

### Pattern: Telegram Notification

**Expected outcome**: Telegram message sent successfully

**Verification steps**:
```bash
# 1. Check logs for Telegram notification
ssh -oVisualHostKey=no ha "ha core logs | tail -50" | grep -E "telegram|Telegram"

# 2. Verify notification sensor
source .env && hass-cli state get sensor.last_notification
```

**Success indicators**:
- `📱 Telegram Notification: Sent → "message text"`
- `📱 Telegram message sent with ID 12345`
- Notification sensor updated with recent timestamp

**Failure indicators**:
- `Error sending Telegram message`
- `Telegram API error`
- No log entry for notification

**Common failures**:
1. **Telegram bot not responding**
   → Action: Check Telegram bot token
   → Action: Verify bot is running
   → Test: Send test message via Telegram

2. **Chat ID incorrect**
   → Action: Verify chat ID in configuration
   → Test: Check `!secret telegram_chat_id` value

3. **Message format error**
   → Action: Check message template for syntax errors
   → Reference: HA Manager skill docs/06_common_mistakes.md

---

### Pattern: Alexa Announcement

**Expected outcome**: Alexa announcement played on devices

**Verification steps**:
```bash
# Check logs for Alexa announcement
ssh -oVisualHostKey=no ha "ha core logs | tail -50" | grep -E "Alexa|alexa|announcement"
```

**Success indicators**:
- `🔊 Alexa Announcement: Sent to 3 devices`
- `🔊 Alexa Response: User confirmed`
- Announcement text visible in logs

**Failure indicators**:
- `Error sending Alexa announcement`
- `Alexa devices not responding`
- No log entry for announcement

**Common failures**:
1. **Alexa devices unavailable**
   → Action: Check Alexa devices are online
   → Action: Verify HA Alexa integration

2. **Announcement format error**
   → Action: Check announcement template
   → Action: Verify text is within Alexa limits

3. **TTS error**
   → Action: Check text-to-speech configuration
   → Reference: Alexa integration documentation

---

## State Change Verification

### Pattern: Switch/Entity Toggle

**Expected outcome**: Entity state changed from off to on (or on to off)

**Verification steps**:
```bash
# Get current state
source .env && hass-cli state get switch.my_switch

# Expected: state changed from 'off' to 'on'
# or: state changed from 'on' to 'off'
```

**Success indicators**:
- State matches expected value
- State changed within expected timeframe
- No errors in logs

**Failure indicators**:
- State unchanged
- State incorrect
- Timeout waiting for state change

**Common failures**:
1. **Entity not responding**
   → Action: Check device is powered on
   → Action: Verify entity is available
   → Test: Control entity manually via UI

2. **Timeout waiting for change**
   → Action: Check automation delay/timeout settings
   → Action: Verify network connectivity to device

3. **Wrong state**
   → Action: Check automation logic for errors
   → Action: Verify entity ID is correct

---

### Pattern: Sensor Value Update

**Expected outcome**: Sensor value updated to expected value

**Verification steps**:
```bash
# Get sensor state
source .env && hass-cli state get sensor.my_sensor

# Check last_updated
source .env && hass-cli -o json state get sensor.my_sensor | jq '.last_updated'
```

**Success indicators**:
- Sensor state matches expected value
- `last_updated` is recent (within automation execution time)
- No stale sensor warnings

**Failure indicators**:
- Sensor value unchanged
- Sensor value incorrect
- Sensor is unavailable or unknown

**Common failures**:
1. **Sensor not updating**
   → Action: Check sensor integration
   → Action: Verify sensor source is working
   → Test: Trigger sensor update manually

2. **Stale sensor data**
   → Action: Check sensor `last_updated` timestamp
   → Action: Force sensor update: `hass-cli service call homeassistant.update_entity`

3. **Wrong value**
   → Action: Check automation logic
   → Action: Verify sensor template/conditions

---

## Script Execution Verification

### Pattern: Script Completed Successfully

**Expected outcome**: Script executed without errors, expected side effects occurred

**Verification steps**:
```bash
# Check logs for script execution
ssh -oVisualHostKey=no ha "ha core logs | tail -30" | grep -E "script.my_script|Error"

# Verify script state
source .env && hass-cli state get script.my_script
```

**Success indicators**:
- Script state shows `on` (running) or completed
- No error messages in logs
- Expected side effects occurred (state changes, notifications, etc.)

**Failure indicators**:
- Script failed to start
- Script execution error
- Script stuck in running state

**Common failures**:
1. **Script not found**
   → Action: Verify script exists
   → Action: Check script YAML filename matches entity ID

2. **Script execution error**
   → Action: Check script YAML syntax
   → Action: Verify script sequence/actions
   → Reference: HA documentation for scripts

3. **Script timeout**
   → Action: Check script timeout setting
   → Action: Verify script doesn't have infinite loops

---

## Conditional Logic Verification

### Pattern: Condition Evaluated Correctly

**Expected outcome**: Automation condition matched expected outcome

**Verification steps**:
```bash
# Check logs for condition evaluation
ssh -oVisualHostKey=no ha "ha core logs | tail -50" | grep -E "condition|Condition"

# Verify trigger state
source .env && hass-cli state get entity.used_in_condition
```

**Success indicators**:
- Condition evaluated as expected
- Automation triggered (or didn't trigger) as expected
- No condition errors in logs

**Failure indicators**:
- Condition evaluated incorrectly
- Automation didn't trigger when expected
- Automation triggered when it shouldn't have

**Common failures**:
1. **Condition logic error**
   → Action: Review condition template/logic
   → Action: Test condition in Developer Tools

2. **Entity state wrong**
   → Action: Check entity state used in condition
   → Action: Verify entity is updating correctly

3. **Template condition error**
   → Action: Test template in Developer Tools → Template
   → Action: Check for undefined variables in template

---

## Action Verification

### Pattern: Service Call Executed

**Expected outcome**: Service call completed successfully

**Verification steps**:
```bash
# Check logs for service call
ssh -oVisualHostKey=no ha "ha core logs | tail -30" | grep -E "call_service|service call"
```

**Success indicators**:
- Service call executed without errors
- Expected side effects occurred
- Service response visible in logs (if applicable)

**Failure indicators**:
- Service call failed
- Service not found
- Invalid service data

**Common failures**:
1. **Service not found**
   → Action: Verify service domain and name
   → Action: Check integration is loaded
   → Reference: Developer Tools → Services

2. **Invalid service data**
   → Action: Check service parameters
   → Action: Test service in Developer Tools
   → Reference: HA Manager skill docs/06_common_mistakes.md (Mistake 4)

3. **Service execution error**
   → Action: Check device/service is available
   → Action: Review error message in logs

---

## Integration with HA Log Analyzer

This subagent can delegate to HA Log Analyzer for log analysis:

**During verification**:
```
1. Trigger automation
2. Delegate to ha-log-analyzer: "Trace automation execution"
3. Use log analyzer output for verification
```

**Benefits**:
- Leverages ha-log-analyzer's pattern detection
- Consistent log analysis across workflows
- Reuses error pattern library

---

## Quick Reference: Verification Methods

| Automation Type | Verification Method | Success Indicator |
|-----------------|---------------------|-------------------|
| **Telegram** | Check logs for "Telegram Notification: Sent" | Log entry + ID |
| **Alexa** | Check logs for "Alexa Announcement: Sent" | Log entry + device count |
| **Switch toggle** | `hass-cli state get switch.xyz` | State changed |
| **Sensor update** | `hass-cli state get sensor.xyz` + check `last_updated` | Value + recent timestamp |
| **Script** | Check logs + `hass-cli state get script.xyz` | No errors + completed |
| **Service call** | Check logs for service execution | No errors + side effects |
| **Condition** | Check logs for condition evaluation | Expected outcome |

---

## Adding New Verification Patterns

To add a new verification pattern:

1. **Identify automation type**: What is being verified?
2. **Define expected outcome**: What should happen?
3. **List verification steps**: How to check?
4. **Document success indicators**: What does success look like?
5. **Document failure indicators**: What does failure look like?
6. **List common failures**: Typical issues and fixes

**Format**:
```markdown
### Pattern: [Name]

**Expected outcome**: [What should happen]

**Verification steps**:
```bash
# Commands to verify
```

**Success indicators**:
- [Indicator 1]
- [Indicator 2]

**Failure indicators**:
- [Indicator 1]
- [Indicator 2]

**Common failures**:
1. **[Failure name]**
   → Action: [Fix]
```
