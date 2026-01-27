# 04. Automation Testing & Verification

**Home Assistant Manager - Testing Workflow**

---

## ALWAYS Verify Automations After Deployment

**Testing workflow for automation changes:**

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
- ✅ Instant feedback (don't wait for scheduled triggers)
- ✅ Verify logic before production
- ✅ Catch errors immediately

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

---

## Quick Test Cycle

```bash
# Full cycle in one block
scp automations.yaml ha:/homeassistant/
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
sleep 3
ssh ha "ha core logs | grep -i 'automation' | tail -10"
```

---

## Testing Checklist

- [ ] Configuration validates (`ha core check`)
- [ ] Automation reloads successfully
- [ ] Manual trigger works
- [ ] Logs show execution (no errors)
- [ ] Expected outcome verified
- [ ] User confirms (if notification)
