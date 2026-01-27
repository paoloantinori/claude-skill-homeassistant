# 02. Deployment Workflows

**Home Assistant Manager - Deployment Documentation**

## Overview

Three deployment approaches for different scenarios:

| Workflow | Use Case | Speed | Version Control |
|----------|----------|-------|-----------------|
| **Git Workflow** | Finalized changes | Slower | ✅ Yes |
| **Rapid SCP** | Testing/iteration | Fast | ⏳ Later |
| **SCP + Git Pull** | Tested changes | Medium | ✅ Yes |

---

## Standard Git Workflow (Final Changes)

Use for changes you want in version control:

```bash
# 1. Make changes locally
# 2. Check validity
ssh ha "ha core check"

# 3. Commit and push
git add file.yaml
git commit -m "Description"
git push

# 4. CRITICAL: Pull to HA instance
ssh ha "cd /homeassistant && git pull"

# 5. Reload or restart
hass-cli service call automation.reload  # if reload sufficient
# OR
ssh ha "ha core restart"  # if restart needed (ASK FIRST!)

# 6. Verify
hass-cli state get sensor.new_entity
ssh ha "ha core logs | grep -i error | tail -20"
```

---

## Rapid Development Workflow (Testing/Iteration)

Use `scp` for quick testing before committing:

```bash
# 1. Make changes locally
# 2. Quick deploy
scp automations.yaml ha:/homeassistant/

# 3. Reload/restart
hass-cli service call automation.reload

# 4. Test and iterate (repeat 1-3 as needed)

# 5. Once finalized, commit and push to git
git add automations.yaml
git commit -m "Final tested changes"
git push

# 6. CRITICAL: Sync HA git state (reset scp'd files, then pull)
# First, discard local changes for the specific files we scp'd
ssh ha "cd /homeassistant && git checkout -- automations.yaml"
# Then pull (now clean, will succeed)
ssh ha "cd /homeassistant && git pull"
```

### Why `git checkout -- <files>` before `git pull`

After testing with `scp`, the HA instance has modified files. A regular `git pull` would fail.

**Safe approach:**
1. `git checkout -- <files>` - reverts ONLY the specific files we scp'd
2. `git pull` - now succeeds since there are no conflicts

**Important:** Only checkout the files you explicitly scp'd. Do NOT use `git reset --hard`.

---

## 🚨 CRITICAL SAFETY: Git Operations on HA Server

### Never Use `git reset --hard`

**FORBIDDEN command:**
```bash
# NEVER DO THIS - can lose uncommitted work
ssh ha "cd /homeassistant && git reset --hard origin/master"
```

**Why this is dangerous:**
- The HA server may have uncommitted changes (manual edits, UI changes)
- `git reset --hard` discards ALL local modifications without warning
- There is no recovery from this operation

### INSPECT Before Discarding Changes

**NEVER run `git checkout --` without FIRST inspecting:**

When `git pull` fails with "uncommitted local changes":

```bash
# ✅ CORRECT WORKFLOW:
# Step 1: INSPECT what changed and WHY
ssh ha "cd /homeassistant && git diff <file>"

# Step 2: ANALYZE changes
# - Are these MY scp changes from this session? → Safe to discard
# - Are these UNKNOWN changes? → STOP, ask user, do NOT discard

# Step 3: Only then checkout
ssh ha "cd /homeassistant && git checkout -- <file>"
```

**❌ WRONG - Blindly discarding:**
```bash
# This loses data without checking what it is
ssh ha "cd /homeassistant && git checkout -- <file>"
```

### Evidence > Assumptions

The HA server may have legitimate changes from:
- UI-based configuration
- Other tools or integrations
- Manual edits
- Previous sessions

**Always verify before discarding.**

---

## SCP + Git Pull Workflow (Avoiding Conflicts)

When you've tested changes via SCP and want to sync to git:

```bash
# 1. Commit your local changes
git add automations.yaml
git commit -m "Tested automation changes"
git push

# 2. 🔍 CRITICAL: INSPECT before discarding
# Check what's actually in the file on the server
ssh ha "cd /homeassistant && git diff automations.yaml"

# 3. ANALYZE the diff:
#    - Only shows your SCP changes from this session? → Safe to continue
#    - Shows UNKNOWN/EXTERNAL modifications? → STOP, investigate first
#    - Shows mixed changes? → Manual merge needed, ask user

# 4. Only if diff shows ONLY your SCP changes, then checkout:
ssh ha "cd /homeassistant && git checkout -- automations.yaml"

# 5. Now pull (clean state)
ssh ha "cd /homeassistant && git pull"

# 6. Reload if needed
hass-cli service call automation.reload
```

### Why the Diff Step Matters

**Scenario:** You SCP'd a file for testing, but in the meantime:
- Someone made UI changes to that same file
- Another tool modified the file
- A previous session's changes were never committed

**Without diff:** You blindly `git checkout --` and lose those changes
**With diff:** You see the external modifications and can investigate

---

## Decision Tree: Which Workflow?

```
Are you still testing the change?
├─ YES → Use Rapid SCP workflow
│         - scp → reload → test → repeat
│         - Commit to git when done
│
└─ NO (change is finalized)
   ├─ First time deploying?
   │  └─ YES → Use Git workflow
   │           - commit → push → pull → reload
   │
   └─ Already tested via SCP?
      └─ YES → Use SCP + Git Pull workflow
                - commit → push → checkout → pull → reload
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy via SCP | `scp file.yaml ha:/homeassistant/` |
| Pull from git | `ssh ha "cd /homeassistant && git pull"` |
| Revert scp'd file | `ssh ha "cd /homeassistant && git checkout -- file.yaml"` |
| Reload automations | `hass-cli service call automation.reload` |
| Check git status | `ssh ha "cd /homeassistant && git status"` |
| View diffs | `ssh ha "cd /homeassistant && git diff file.yaml"` |

---

## Common Pitfalls

| Mistake | Consequence | Solution |
|---------|-------------|----------|
| `git reset --hard` | Loses uncommitted work | Use `git checkout -- <files>` |
| `git pull` without checkout | Fails with conflicts | Checkout scp'd files first |
| Blind checkout without diff | Loses unknown changes | Always `git diff` first |
| SCP to wrong path | Changes not active | Use `ha:/homeassistant/` |
| Forgot to reload | Changes not active | Reload after deploy |
