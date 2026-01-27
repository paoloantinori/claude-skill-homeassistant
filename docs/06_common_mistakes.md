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

## Quick Reference: Common Pitfalls

| Mistake | Prevention |
|---------|------------|
| Git pull conflicts | Always `git diff` before `git checkout` |
| SCP + Git conflicts | Track scp files, checkout before pull |
| Wrong paths | Use `ha:` alias, verify paths |
| Service call errors | Test in Developer Tools first |
| Wrong reload/restart | Check decision tree in safety docs |
| SSH grep filtering | Use `ssh -oVisualHostKey=no` |
| Using curl instead of hass-cli | Use `hass-cli state/service call` for all HA API |
| Restart verification loops | Trust `docker ps`, pivot to hass-cli |

---

## Auto-Improve Pattern

**When any command fails:**

1. **Analyze** the error message carefully
2. **Try correcting** the command (not switching tools)
3. **Document** the pattern after success

**Example:**
```bash
$ hass-cli state get | grep automation
Error: Missing argument 'ENTITY'

# ❌ WRONG: Immediately try curl
$ curl ... | grep automation

# ✅ CORRECT: Analyze → "state get needs entity" → Try correct approach
$ hass-cli state list | grep automation
# Success! Then document this pattern.
```
