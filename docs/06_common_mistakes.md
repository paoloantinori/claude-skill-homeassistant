# 06. Common Mistake Patterns & Prevention

**Home Assistant Manager - Error Patterns & Solutions**

---

## Mistake 1: Git Pull Without Inspection

**Symptom:** "Your local changes would be overwritten by merge"

**❌ WRONG:**
```bash
# Immediate checkout without inspection
ssh ha "cd /homeassistant && git checkout ."
```

**✅ CORRECT:**
```bash
# Inspect → Categorize → Decide
ssh ha "cd /homeassistant && git diff <file>"
# Analyze: Are these MY changes from this session?
# Only then: checkout if safe
```

**Prevention:** Always run `git status` before attempting `git pull`

---

## Mistake 2: SCP Then Git Pull Conflicts

**Symptom:** Git pull fails with "Your local changes would be overwritten by merge"

**What happened:**
1. Deployed via scp for testing
2. Later committed and pushed changes
3. Git pull on server conflicts with scp-modified files

**❌ WRONG (forgot to checkout first):**
```bash
# Deployed via scp earlier
scp file.yaml ha:/homeassistant/

# Later, after committing to git...
ssh ha "cd /homeassistant && git pull"
# Error: Your local changes to the following files would be overwritten...
```

**✅ CORRECT (checkout before pull):**
```bash
# Deployed via scp earlier
scp file.yaml ha:/homeassistant/

# Later, after committing to git...
ssh ha "cd /homeassistant && git checkout -- file.yaml && git pull"
```

**One-liner pattern:**
```bash
# Combined checkout + pull (when you KNOW the files are safe to discard)
ssh ha "cd /homeassistant && git checkout -- file.yaml file2.yaml && git pull"
```

**Recovery pattern (when git pull already failed):**
```bash
# git pull just failed with "local changes would be overwritten"
# Recovery: checkout the conflicted files, then retry pull
ssh ha "cd /homeassistant && git checkout -- file.yaml && git pull"
```

**Prevention:**
- Document which files were deployed via scp (they need checkout before pull)
- OR use the "SCP + Git Pull Workflow" from `docs/02_deployment.md`
- Track: `scp deploy → commit → checkout → pull → reload`

---

## Mistake 3: Using Wrong Paths

**Symptom:** File operations fail or files created in wrong location

**Common errors:**
- Claude docs in `~/.claude/` instead of project `.claude/`
- SSH to `root@homeassistant.local` instead of `ha:` alias
- Target `/config/` instead of `/homeassistant/`

**Prevention:** Use correct path references:
- Project: `/home/pantinor/data/repo/personal/hassio/`
- Server: `ha:/homeassistant/` (via SSH alias)
- Claude docs: Project `.claude/`, NOT `~/.claude/`

---

## Mistake 4: Service Call Parameters Not Verified

**Symptom:** Service call fails with "Extra keys not allowed" or "Required key missing"

**What happened:**
- Used service parameters based on old documentation
- HA version changed service schema
- Parameters removed or added

**Prevention:**
- ALWAYS verify in Developer Tools → Services before deploying
- Check release notes for service schema changes
- Test service call manually before adding to automation

---

## Mistake 5: Reload Instead of Restart (or vice versa)

**Symptom:** Changes not applied despite "successful" reload

**Common errors:**
- Using `automation.reload` for integration config changes (needs restart)
- Using full restart for simple automation edits (reload sufficient)

**Prevention:** Use reload decision tree (see `docs/01_critical_safety.md`)

---

## Mistake 6: Filtering SSH Output with grep

**Symptom:** Commands cluttered with visual fingerprint ASCII art

**What happened:**
- SSH displays visual host key fingerprint on every connection
- Added `grep -v "Host key\|ED25519\|+--\||\|--\|SHA256"` to filter it out
- Inefficient and makes commands harder to read

**❌ WRONG:**
```bash
ssh ha "ha core logs | tail -50" 2>/dev/null | grep -v "Host key\|ED25519\|+--\||\|--\|SHA256"
```

**✅ CORRECT:**
```bash
ssh -oVisualHostKey=no ha "ha core logs | tail -50"
```

**Best Practice:** Configure permanently in `~/.ssh/config`:

```bash
Host ha
    HostName homeassistant.local
    User root
    VisualHostKey no
```

Then `ssh ha` never shows fingerprint, no grep needed.

**Prevention:**
- Use `-oVisualHostKey=no` for all SSH commands in automations/scripts
- Add `VisualHostKey no` to SSH config for manual commands
- Never use grep to filter SSH output

---

## Mistake 7: Using curl Instead of hass-cli

**Symptom:** Commands are overly long, hard to read, and require manual authentication headers

**What happened:**
- Defaulted to curl patterns from prior experience
- Didn't realize hass-cli covers all Home Assistant API operations
- Wanted "raw JSON" and didn't know about `hass-cli -o json`

**❌ WRONG:**
```bash
# Overly complex, error-prone
curl -s -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  http://$HASS_SERVER/api/states/binary_sensor.example

curl -s -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  http://$HASS_SERVER/api/services/homeassistant/reload_core_config

curl -s -d '{"template": "{{ now() }}"}' \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  http://$HASS_SERVER/api/template
```

**✅ CORRECT:**
```bash
# Simple, clear, self-documenting
hass-cli state get binary_sensor.example

hass-cli service call homeassistant.reload_core_config

hass-cli raw post /api/template --json '{"template": "{{ now() }}"}'
```

**Common curl → hass-cli translations:**

| Task | ❌ curl (WRONG) | ✅ hass-cli (CORRECT) |
|------|----------------|----------------------|
| Get state | `curl -H "Authorization: Bearer $TOKEN" $SERVER/api/states/sensor.x` | `hass-cli state get sensor.x` |
| Get JSON | `curl ... \| jq '.state'` | `hass-cli -o json state get sensor.x` |
| List entities | `curl ... /api/states` | `hass-cli state list` |
| Reload automations | `curl -X POST ... /api/services/automation/reload` | `hass-cli service call automation.reload` |
| Reload core config | `curl -X POST ... /api/services/homeassistant/reload_core_config` | `hass-cli service call homeassistant.reload_core_config` |
| Trigger automation | `curl -X POST -d '{"entity_id": "..."}' ...` | `hass-cli service call automation.trigger --arguments entity_id=automation.name` |
| Test template | `curl -d '{"template": "..."}' ... /api/template` | `hass-cli raw post /api/template --json '{"template": "..."}'` |

**When curl IS acceptable (rare):**
- hass-cli has a confirmed bug blocking your use case
- Accessing a non-Home Assistant API
- Integration testing with specific HTTP requirements

**Prevention:**
- Memorize: hass-cli is MANDATORY for all HA API interactions
- Learn `hass-cli -o json` for JSON output (no curl needed)
- Learn `hass-cli raw` for direct API access (no curl needed)
- See `docs/07_remote_access.md` for complete translation guide

**Troubleshooting before using curl:**
1. Verify `.env` is sourced: `echo $HASS_TOKEN | head -c 20`
2. Test basic query: `hass-cli state get sensor.example`
3. Check output format: `hass-cli -o json state get sensor.example`
4. Only consider curl if hass-cli is genuinely broken

---

## Mistake 8: Stuck in Restart Verification Loop

**Symptom:** After restart, keep retrying failed HTTP checks while ignoring direct evidence

**What happened:**
1. Sent restart command successfully
2. Checked with `curl $HASS_SERVER/api/` → got HTTP 000 (connection refused)
3. Kept retrying the same curl command multiple times
4. User had to inform that server was back
5. SSH `docker ps` showed container was "Up 7 minutes" the whole time

**Root cause:** Trusted indirect HTTP check over direct container status evidence

**✅ CORRECT:**
```bash
# Trust direct evidence, pivot to verify fix
ssh ha "docker ps --filter name=homeassistant"
# If shows "Up X minutes", server IS running - move on

# Then verify the actual change took effect
source .env && hass-cli state get binary_sensor.example
```

**❌ WRONG:**
```bash
# Loop retrying failing HTTP checks
curl $HASS_SERVER/api/  # Fails with HTTP 000
curl $HASS_SERVER/api/  # Try again... why?
curl $HASS_SERVER/api/  # And again...
```

**Prevention:**
- Trust `docker ps` output - if container is "Up X minutes", HA is running
- Don't troubleshoot curl failures - goal is to verify the fix, not debug curl
- Move on to verify the actual change using hass-cli or other reliable methods
- If curl fails, try alternative verification methods

**Key principle:** Direct evidence (`docker ps`) > Indirect HTTP checks. When one diagnostic fails, pivot to another approach rather than retrying the same failing command.

---

## Mistake 9: Forgetting to Source .env Before hass-cli

**Symptom:** `401 Unauthorized` error from hass-cli

**What happened:**
- Ran `hass-cli` command without sourcing `.env` first
- HASS_TOKEN environment variable not set
- hass-cli cannot authenticate to Home Assistant

**❌ WRONG:**
```bash
# Forgot to source .env
hass-cli state get sensor.example
# Error: HomeAssistantCliError: Error calling service: 401 - 401: Unauthorized
```

**✅ CORRECT:**
```bash
# Source .env first
source .env && hass-cli state get sensor.example
```

**Or source once, then multiple commands:**
```bash
source .env
hass-cli state get sensor.example
hass-cli service call automation.reload
```

**Prevention:**
- Make `source .env` the first step in any hass-cli workflow
- Check if env is loaded: `echo $HASS_TOKEN | head -c 20` (should show token start)
- All examples in skill docs show `source .env && hass-cli` pattern

**Troubleshooting:**
```bash
# Verify .env is sourced
echo $HASS_TOKEN | head -c 20

# If empty, source it
source /home/pantinor/data/repo/personal/hassio/.env
```

---

## Mistake 9: Using `state_attr()` for `last_updated` in Templates

**Symptom:** Staleness checks always return `True` or `999`, template evaluates entity as stale even when fresh

**❌ WRONG:**
```yaml
# In template sensors
{% set last_upd = state_attr('device_tracker.phone', 'last_updated') %}
{% set stale = (now() - last_upd).total_seconds() > 300 if last_upd else true %}
# Problem: last_upd is always None! state_attr() can't access core entity properties
```

**✅ CORRECT:**
```yaml
# Use states.xxx.last_updated instead
{% set last_upd = states.device_tracker.phone.last_updated %}
{% set stale = (now() - last_upd).total_seconds() > 300 if last_upd else true %}
```

**Why:** `last_updated`, `last_changed`, `last_reported` are core entity properties, not attributes. Access via `states.entity.property` not `state_attr('entity', 'property')`.

**Prevention:**
- Test template evaluation: `curl -X POST -H "Authorization: Bearer $TOKEN" $HASS/api/template -d '{"template": "{% set x = states.xxx.last_updated %}{{ x }}"}'`
- If `last_upd` prints `None`, switch to `states.xxx.last_updated`

---

## Mistake 10: Using `state_attr()` in Telegram Message Templates

**Symptom:** YAML parsing error: "can't find end of the entity starting at byte offset X"

**❌ WRONG:**
```yaml
- action: telegram_bot.send_message
  data:
    target:
      - !secret telegram_chat_id
    message: |
      GPS Updated: {{ state_attr('device_tracker.phone', 'last_updated') }}
# Problem: Nested quotes in template break YAML parsing
```

**✅ CORRECT:**
```yaml
# Option 1: Remove complex expressions from messages
- action: telegram_bot.send_message
  data:
    target:
      - !secret telegram_chat_id
    message: |
      GPS Updated: Check logs for details

# Option 2: Calculate in variable, use simple reference
- action: system_log.write
  data:
    message: "GPS: {{ state_attr(...) }}"
- action: telegram_bot.send_message
  data:
    target:
      - !secret telegram_chat_id
    message: |
      GPS status updated
```

**Prevention:**
- Keep telegram message templates simple
- Use `system_log.write` for complex debug output
- Avoid nested quotes in YAML multi-line strings

---

## Mistake 11: Forgetting to Check Logs After Deployment

**Symptom:** Automation/script errors silently fail, user notices before you do

**❌ WRONG:**
```bash
# Deploy and reload, move on immediately
scp file.yaml ha:/homeassistant/
hass-cli service call automation.reload
# (immediately starts next task without checking logs)
# Error in logs: "Failed to generate automation"
# User reports broken automation hours later
```

**✅ CORRECT:**
```bash
# Deploy
scp file.yaml ha:/homeassistant/

# Reload
hass-cli service call automation.reload

# IMMEDIATELY check logs (within 30 seconds)
ssh ha "ha core logs | tail -50" | grep -E "(ERROR|error)"

# If errors found → fix immediately
# If no errors → proceed with testing
```

**Prevention:**
- **ALWAYS** check logs within 30 seconds after reload
- Create pattern: `scp → reload → log check → continue`
- Document this in your deployment checklist

**Pattern to add to workflow:**
```bash
post_reload_check() {
  ssh ha "ha core logs | tail -50" | grep -E "(ERROR|error)" | tail -10
}

# Usage
scp file.yaml ha:/homeassistant/ && \
hass-cli service call automation.reload && \
sleep 2 && \
post_reload_check
```

---

## Mistake 12: Using `homeassistant.reload_config_entry` for YAML-Defined Entities

**Symptom:** `ValueError: There were no matching config entries to reload`

**What happened:**
- Tried to reload an input_boolean, template sensor, or other YAML-defined entity
- Used `homeassistant.reload_config_entry` (designed for UI-configured integrations)
- YAML-defined entities don't have config entries—they have their own reload services

**❌ WRONG:**
```bash
# Trying to reload a YAML-defined input_boolean
hass-cli service call homeassistant.reload_config_entry --arguments entity_id=input_boolean.paolo_staleness_latch
# ValueError: There were no matching config entries to reload
```

**✅ CORRECT:**
```bash
# Use the entity-type-specific reload service
hass-cli service call input_boolean.reload
```

**Reload services by entity type:**

| Entity Type | Reload Service |
|-------------|----------------|
| Automations | `automation.reload` |
| Scripts | `script.reload` |
| Input Booleans | `input_boolean.reload` |
| Input Numbers | `input_number.reload` |
| Input Selects | `input_select.reload` |
| Input Text | `input_text.reload` |
| Input Datetime | `input_datetime.reload` |
| Input Buttons | `input_button.reload` |
| Template Entities | `template.reload` |
| Groups | `group.reload` |
| Timers | `timer.reload` |
| Counters | `counter.reload` |
| Scenes | `scene.reload` |
| Zones | `zone.reload` |
| Persons | `person.reload` |
| MQTT | `mqtt.reload` |

**When TO use `homeassistant.reload_config_entry`:**
- UI-configured integrations (configured via Settings → Devices & Services)
- Never for YAML-defined entities

**Prevention:**
- Check `docs/08_quick_reference.md` for the full reload services table
- Remember: YAML entities have their own `<domain>.reload` service
- `homeassistant.reload_config_entry` is only for UI-configured integrations

---

## Quick Reference: Common Pitfalls

| Mistake | Prevention |
|---------|------------|
| Assumed file location without checking configuration.yaml | ALWAYS check configuration.yaml first to understand includes |
| Git pull conflicts | Always `git diff` before `git checkout` |
| SCP + Git conflicts | Track scp files, checkout before pull |
| Wrong paths | Use `ha:` alias, verify paths |
| Service call errors | Test in Developer Tools first |
| Wrong reload/restart | Check decision tree in safety docs |
| SSH grep filtering | Use `ssh -oVisualHostKey=no` |
| Using curl instead of hass-cli | Use `hass-cli state/service call` for all HA API |
| Restart verification loops | Trust `docker ps`, pivot to hass-cli |
| hass-cli 401 errors | Always `source .env` before hass-cli commands |
| `state_attr()` for `last_updated` | Use `states.xxx.last_updated` in templates |
| `state_attr()` in messages | Keep telegram messages simple, avoid nested quotes |
| Skipping post-deploy log check | **ALWAYS** check logs within 30s after reload |
| `reload_config_entry` for YAML entities | Use `<domain>.reload` (e.g., `input_boolean.reload`) |
| **Jumping to alt tools on failure** | **Run `command --help` FIRST after any usage error** |
| `hass-cli state get` multiple entities | Use `state list \| grep` or loop for multiple entities |
| `tail -f` without timeout | **ALWAYS** wrap with `timeout X` |
| Assuming output format | Check actual output before parsing |
| **Failing 3+ times in a row** | **STOP after 2 failures → Add diagnostics → Then retry** |
| `hass-cli template` inline string | It wants a FILE path; write Jinja to a temp file |
| Multiple `service call` params | Repeat `--arguments` flag per key=value pair |
| Parameterized `service call` via hass-cli | 400s or empty params; use YAML/UI/MCP (HA 2026.8) |
| Automation entity lookup by YAML `id` | Entity id is the slugified `alias`; find via `state list \| grep` |
| `ssh ha "hass-cli …"` not found | hass-cli absent on server; use dev-host hass-cli or ha MCP |
| `hass-cli state history` bad escape | Broken in this build; use `.storage/trace.saved_traces` or MCP history |

---

## Force-Refresh Entity Pattern

**When to use:** Device tracker not updating, need to trigger immediate location refresh

```bash
# Force entity to update from its source
hass-cli service call homeassistant.update_entity --arguments entity_id=device_tracker.phone_name

# Then verify the update
hass-cli state get device_tracker.phone_name
```

**Use cases:**
- Testing staleness detection logic
- Forcing GPS update after airplane mode
- Triggering sensor refresh that appears stuck
- Debugging entity update behavior

**Note:** This requests an update from the integration. If the source (phone/app) doesn't respond, the entity won't update.

---

## Mistake 13: Not Using --help When Commands Fail

**Symptom:** Jumping to alternative tools/approaches after first failure, wasting multiple attempts

**What happened:**
- Command failed with usage error
- Instead of running `command --help` to understand correct usage
- Immediately switched to curl, python parsing, or other complex workarounds
- Made 3-5 additional failed attempts before finding a solution

**❌ WRONG:**
```bash
$ hass-cli state get entity1 entity2 entity3
Error: Got unexpected extra arguments

# Immediately tries complex python JSON parsing
$ hass-cli -o json state get entity1 | python3 -c "..."
# Fails again, tries different parsing...
# 4 more failed attempts
```

**✅ CORRECT:**
```bash
$ hass-cli state get entity1 entity2 entity3
Error: Got unexpected extra arguments

# FIRST: Check help to understand usage
$ hass-cli state get --help
# Learns: only accepts ONE entity

# THEN: Use correct approach
$ hass-cli state get entity1
$ hass-cli state get entity2
```

**Prevention:**
- **MANDATORY**: Run `command --help` after ANY usage error
- Read the error message carefully before trying alternatives
- Understand WHY it failed before attempting fixes
- Only switch tools if help confirms the tool can't do what you need

---

## Mistake 14: hass-cli state get Only Accepts One Entity

**Symptom:** `Error: Got unexpected extra arguments`

**What happened:**
- Tried to get multiple entity states in one command
- hass-cli state get only accepts ONE entity at a time

**❌ WRONG:**
```bash
hass-cli state get entity1 entity2 entity3
# Error: Got unexpected extra arguments
```

**✅ CORRECT:**
```bash
# Option 1: Multiple separate calls
hass-cli state get entity1
hass-cli state get entity2

# Option 2: Use state list with grep for multiple entities
hass-cli state list | grep -E "(entity1|entity2|entity3)"

# Option 3: Loop in bash
for e in entity1 entity2 entity3; do
  echo "=== $e ===" && hass-cli state get $e
done
```

**Prevention:**
- Remember: `state get` = ONE entity, `state list` = ALL entities
- Use `state list | grep` pattern for checking multiple specific entities

---

## Mistake 15: tail -f Without Timeout on Remote Logs

**Symptom:** Command hangs indefinitely, blocks entire workflow

**What happened:**
- Used `ssh ha "tail -f logfile"` to monitor logs
- tail -f never exits on its own
- Session blocked waiting for manual Ctrl+C
- No way to recover without user intervention

**❌ WRONG:**
```bash
# Blocks forever
ssh ha "tail -f /var/log/something"
```

**✅ CORRECT:**
```bash
# Use timeout to auto-exit
ssh ha "timeout 120 tail -f /var/log/something"

# Or with head limit for grep results
ssh ha "timeout 120 tail -f logfile" 2>&1 | grep -m 10 "pattern"

# For HA logs specifically
ssh -oVisualHostKey=no ha "ha core logs 2>&1 | tail -100" | grep "pattern"
```

**Prevention:**
- **ALWAYS** wrap `tail -f` with `timeout X` where X is max seconds
- Use `grep -m N` to exit after N matches
- Prefer `ha core logs | tail -N` over `tail -f` for log checking
- Set bash tool timeout parameter for long-running commands

---

## Mistake 16: Assuming Command Output Format Without Checking

**Symptom:** JSON parsing errors, type errors, empty results

**What happened:**
- Assumed `hass-cli -o json` returns a dict
- Actually returns a list
- Made multiple failed parsing attempts with wrong assumptions

**❌ WRONG:**
```bash
# Assumes dict output
hass-cli -o json state get entity | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['state'])"
# TypeError: list indices must be integers or slices, not str
```

**✅ CORRECT:**
```bash
# FIRST: Check actual output format
hass-cli -o json state get entity

# THEN: Parse correctly based on what you see
# Or just use default tabular output which is simpler
hass-cli state get entity
```

**Prevention:**
- **ALWAYS** run command without parsing first to see output format
- Don't assume JSON structure - verify it
- Prefer simple tabular output (`hass-cli state get`) over JSON when possible
- If JSON needed, test parsing on known output first

---

## Meta-Pattern: Stop After Two Failures

**CRITICAL: If you fail twice in a row at the same task, STOP and reflect.**

**What to do after 2 consecutive failures:**

1. **STOP** - Do not attempt a third time blindly
2. **Reflect** - What information am I missing?
3. **Add diagnostics** - What logging/output would reveal the problem?
4. **Gather evidence** - Run diagnostic commands before retrying
5. **Then retry** - With new information, not the same approach

**Examples of diagnostic questions:**

| Failure Type | Diagnostic to Add |
|--------------|-------------------|
| Command syntax error | Run `command --help` |
| Unexpected output | Print raw output before parsing |
| Entity not found | List all entities with `hass-cli state list \| grep pattern` |
| Automation not firing | Check logs: `ssh ha "ha core logs \| grep automation_name"` |
| Template error | Test template in Developer Tools first |
| Timing/race condition | Add timestamps to log messages |

**Anti-pattern to avoid:**
```
Attempt 1: fails
Attempt 2: fails (same approach)
Attempt 3: fails (still same approach)  ← WRONG
Attempt 4: fails...
```

**Correct pattern:**
```
Attempt 1: fails
Attempt 2: fails
STOP → Reflect → "What would help me understand this?"
Add diagnostic: check --help, print raw output, add logging
Attempt 3: succeeds (with new information)
```

---

## Auto-Improve Pattern

**When any command fails:**

1. **Run `--help`** to understand correct usage
2. **Analyze** the error message carefully
3. **Try correcting** the command (not switching tools)
4. **If fails twice** → Apply Meta-Pattern above
5. **Document** the pattern after success

**Example:**
```bash
$ hass-cli state get | grep automation
Error: Missing argument 'ENTITY'

# ❌ WRONG: Immediately try curl
$ curl ... | grep automation

# ✅ CORRECT: Check help first
$ hass-cli state get --help
# Learns: requires ENTITY argument

# Then try correct approach
$ hass-cli state list | grep automation
# Success! Then document this pattern.
```

---

## Mistake 17: Using `hass-cli state set` (Command Doesn't Exist)

**Symptom:** `Error: No such command 'set'`

**What happened:**
- Tried to set an input_number/input_boolean value using `hass-cli state set`
- The `state` subcommand doesn't have a `set` command
- Need to use service calls instead

**❌ WRONG:**
```bash
$ hass-cli state set input_number.batteria_telefono_chiara_scarico 20
Error: No such command 'set'
# Then tries curl or other workarounds...
```

**✅ CORRECT:**
```bash
# Use service call to set input_number value
$ hass-cli service call input_number.set_value --arguments entity_id=input_number.batteria_telefono_chiara_scarico,value=20

# Or for input_boolean
$ hass-cli service call input_boolean.turn_on --arguments entity_id=input_boolean.example

# For other entity types, check the domain's services
$ hass-cli state list | grep input_number  # List available input_number entities
```

**Common entity state change patterns:**

| Entity Type | Service Call Example |
|-------------|---------------------|
| input_number | `hass-cli service call input_number.set_value --arguments entity_id=input_number.x,value=10` |
| input_boolean | `hass-cli service call input_boolean.turn_on --arguments entity_id=input_boolean.x` |
| input_select | `hass-cli service call input_select.select_option --arguments entity_id=input_select.x,option="Option1"` |
| input_text | `hass-cli service call input_text.set_value --arguments entity_id=input_text.x,value="text"` |
| counter | `hass-cli service call counter.increment --arguments entity_id=counter.x` |
| timer | `hass-cli service call timer.start --arguments entity_id=timer.x` |

**Prevention:**
- Remember: `state get` and `state list` are for READING, not WRITING
- To change entity state, use `service call <domain>.<service>`
- Check available services: `hass-cli service list | grep input_number`
- When unsure, run `hass-cli --help` to see available commands

**Recovery:**
```bash
# After "No such command" error:
$ hass-cli state --help  # See available state commands (get, list, edit - no 'set')

# Then find the correct service:
$ hass-cli service list | grep -E "input_number|set_value"

# Use the service:
$ hass-cli service call input_number.set_value --help  # Check parameters
$ hass-cli service call input_number.set_value --arguments entity_id=xxx,value=20
```

---

## Mistake 18: Assuming "Ghost Entity" Means Entity Doesn't Exist

**Symptom:** Spook reports "ghost" entities in dashboards, you assume they're broken and remove them

**What happened:**
- Spook Integration reports entities as "unknown to Home Assistant"
- You assume the entities are missing/broken without verifying
- Removed dashboard references to working entities
- Broke functional automations that depend on those entities

**Root Cause:**
- "Ghost" in Spook means "referenced in dashboard but Spook can't find it"
- This can mean: (a) entity doesn't exist, OR (b) entity exists but Spook's scan missed it, OR (c) entity is loaded from YAML on next restart
- Local `.storage/` grep may not reflect server state

**❌ WRONG:**
```bash
# Spook says: "input_boolean.segnala_chiara_ripartita is unknown"
# Immediately assume it doesn't exist and remove from dashboard

# Check local storage (not server)
$ grep -r "segnala_chiara_ripartita" .storage/
# No results locally → conclude entity missing

# Remove from dashboard → break automation
```

**✅ CORRECT:**
```bash
# FIRST: Verify entity exists on RUNNING HA server
$ source .env && hass-cli state list | grep segnala_chiara_ripartita
input_boolean.segnala_chiara_ripartita    Segnala quando Chiara riparte    on

# Entity EXISTS! Check if automation uses it
$ grep -r "segnala_chiara_ripartita" automations/
# Found: automations/location/location.yaml - chiara_ripartita automation

# Conclusion: Dashboard reference is VALID, entity is functional
# Spook may have stale cache or timing issue
```

**Investigation Pattern for "Ghost" Entities:**

| Step | Command | Purpose |
|------|---------|---------|
| 1. Verify existence | `source .env && hass-cli state list \| grep entity_id` | Does entity exist on server? |
| 2. Check automations | `grep -r entity_id automations/` | Is it actively used? |
| 3. Check YAML config | `grep -r entity_id input_boolean/` | Is it defined in YAML? |
| 4. Decision | - | If exists + used → keep; if truly missing → fix |

**Decision Matrix:**

| Entity State | Dashboard Action |
|--------------|------------------|
| Exists in `hass-cli state list` | ✅ Keep dashboard reference |
| Used in automations | ✅ Keep dashboard reference |
| Not in `hass-cli state list` | ❌ Remove from dashboard |
| Defined in YAML but not loaded | May need restart or reload |

**Why local grep is unreliable:**
- Local `.storage/` files are copies from git pull
- Server state is authoritative (what HA actually runs)
- Entity may be loaded from YAML folder, not single file
- Spook scans may have timing issues or stale caches

**Prevention:**
- **ALWAYS** verify entity existence with `hass-cli state list` FIRST
- Trust server state over local files or Spook warnings
- Check automation dependencies before removing dashboard references
- Remember: `!include_dir_merge_named input_boolean` loads from FOLDER, not `input_boolean.yaml`

**Example: The `input_boolean.yaml` confusion:**
```yaml
# In configuration.yaml:
input_boolean: !include_dir_merge_named input_boolean  # Loads from folder/

# This means:
# - input_boolean/location.yaml gets loaded ✅
# - input_boolean.yaml (root file) gets IGNORED ❌
# - Entities defined in folder/ are created on HA start/restart
```

**Key takeaway:** Spook's "ghost" warning is a hint to investigate, not a verdict to delete. Always verify with `hass-cli state list` before removing dashboard references.

---

## Mistake 19: Passing an Inline Template to `hass-cli template`

**Symptom:** `Error: Invalid value for 'TEMPLATE': '...': No such file or directory`

**What happened:**
- Passed the Jinja template as an inline string argument
- This hass-cli build expects a FILE PATH, not the template text
- It tries to open the template string as a file and fails

**❌ WRONG:**
```bash
hass-cli template '{{ states("input_datetime.last_restart") }}'
# Error: Invalid value for 'TEMPLATE': No such file or directory
```

**✅ CORRECT:**
```bash
# Write the Jinja to a temp file, pass the path
cat > /tmp/test.j2 <<'EOF'
{{ states('input_datetime.last_restart') }}
EOF
hass-cli template /tmp/test.j2
```

**Prevention:**
- `hass-cli template <file>` renders a file; for one-off API-style calls there is also
  `hass-cli raw post /api/template --json '{"template": "..."}'` (see Mistake 7)
- Prefer the temp-file form: plain-text output, no JSON quoting battles

---

## Mistake 20: Multiple Service Parameters Need Repeated `--arguments` Flags

**Symptom:** `Error: Got unexpected extra argument (key2=value2)`

**What happened:**
- Passed several key=value pairs after a single `--arguments` flag, space-separated
- hass-cli consumes only the first pair as the flag value; the rest become unexpected
  positional arguments

**❌ WRONG:**
```bash
hass-cli service call input_datetime.set_datetime --arguments entity_id=input_datetime.last_restart timestamp=1786717888
# Error: Got unexpected extra argument (timestamp=1786717888)
```

**✅ CORRECT:**
```bash
# Repeat the flag once per parameter (required for values containing spaces)
hass-cli service call input_datetime.set_datetime --arguments entity_id=input_datetime.last_restart --arguments timestamp=1786717888
```

**Prevention:**
- `--arguments entity_id=x --arguments key2=y`, one flag per parameter
- Comma-joined form (`--arguments entity_id=x,value=y`) works for simple values but
  breaks on values containing commas or spaces; the repeated-flag form is the robust one

---

## Mistake 21: Parameterized `hass-cli service call` Is Unreliable on HA 2026.8

**Symptom:** Either `Error calling service: 400 - 400: Bad Request` with an empty body,
or the call "succeeds" but the service reports missing/empty parameters

**What happened (verified 2026-08-14/15, HA 2026.8.1):**
- `hass-cli service call input_datetime.set_datetime` with `timestamp=` AND with
  `datetime=` (correct repeated-flag syntax, Mistake 20) both return an empty 400
- `hass-cli service call pyscript.send_portaleargo_notification` with repeated
  `--arguments` flags executes the function but the parameters arrive EMPTY (the
  function logs "Missing required parameters")
- Parameterless calls (`automation.reload`, `pyscript.reload`) work fine
- The same services called from YAML automations/scripts work
- Mechanism unverified (likely this hass-cli build serializing the payload in a way
  current HA rejects or drops); empirically confirmed on this setup only

**✅ Workarounds:**
```bash
# Reads: render templates instead
hass-cli template /tmp/state.j2

# Parameterized service calls: use a YAML automation/script, the UI,
# or the ha MCP tools (channel 1); never burn retries on hass-cli variants
```

**Prevention:**
- Treat hass-cli service calls as parameterless-only on this setup
- After two failures on the same call, switch channel (Meta-Pattern below)

---

## Mistake 22: Automation entity_id Comes From the alias, Not the YAML id

**Symptom:** `hass-cli state get automation.notifiche_didup` → `Entity with ID ... not found`

**What happened:**
- Looked up an automation entity using the YAML `id:` field value
- The YAML `id` is only the automation's internal identifier (used in traces/UI URLs);
  the entity object_id is the slugified `alias:`
- `alias: Notifiche Didup Nora` → `automation.notifiche_didup_nora`, while the YAML id
  was `notifiche_didup`

**✅ CORRECT:**
```bash
# Find the real entity_id from the alias
hass-cli state list | grep -i didup
# automation.notifiche_didup_nora  Notifiche Didup Nora  on
```

**Prevention:**
- Resolve automation entities via `state list | grep <alias fragment>`, never from the
  YAML `id`

---

## Mistake 23: hass-cli Is Not in PATH on the HA Server over SSH

**Symptom:** `ssh ha "hass-cli ..."` → `zsh:1: command not found: hass-cli`

**What happened:**
- Channel hierarchy (SKILL.md) lists `ssh ha "hass-cli …"` as the SSH fallback
- On this setup hass-cli is not installed (or not in PATH for non-interactive SSH), so
  that channel is unavailable
- The dev-host hass-cli (tertiary channel) works when on the home LAN
  (`homeassistant.local` resolves)

**✅ CORRECT:**
```bash
# From the dev host on the home LAN
source .env && hass-cli state get sensor.example

# Server-side operations that hass-cli cannot do anyway still go through plain SSH
ssh -oVisualHostKey=no ha "docker logs homeassistant --since 2h | tail -50"
```

**Prevention:**
- If the dev host cannot resolve `homeassistant.local` AND the server lacks hass-cli,
  the remaining options are the ha MCP tools (channel 1) or `ssh ha "ha core ..."`
  commands; never fall back to curl

---

## Mistake 24: `hass-cli state history` Broken in This Build

**Symptom:** `error: bad escape \d at position 7` on every invocation, even with no
`--since`/`--end` arguments (verified 2026-08-15)

**What happened:**
- Wanted state history to see an entity's transitions across a restart
- `hass-cli state history <entity>` fails before any request: the build mangles its own
  default time-window handling (regex escape error, not a server-side issue)

**✅ Workarounds:**
```bash
# Automation runs (including runs blocked by conditions, script_execution:
# failed_conditions) are persisted on the server:
ssh -oVisualHostKey=no ha "python3 -c \"
import json
data = json.load(open('/homeassistant/.storage/trace.saved_traces'))['data']
for k in data:
    if '<name fragment>' in k:
        for t in data[k]:
            ed = t['extended_dict']
            print(k, ed['timestamp']['start'], ed.get('script_execution'))
\""

# Entity state over time: use the ha MCP history tools (channel 1) instead
```

**Prevention:**
- For "did this automation fire / was it blocked?" questions, go straight to
  `.storage/trace.saved_traces`; it proves both executed runs and condition-blocked runs

