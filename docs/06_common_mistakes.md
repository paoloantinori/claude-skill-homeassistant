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

**Symptom:** Git pull fails due to local modifications from earlier scp deployments

**What happened:**
1. Deployed via scp for testing
2. Later committed and pushed changes
3. Git pull on server conflicts with scp-modified files

**Prevention:**
- Document which files were deployed via scp
- Checkout scp files BEFORE git pull
- OR use scp-only for /tmp, git-only for /homeassistant

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

## Mistake 7: Stuck in Restart Verification Loop

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
