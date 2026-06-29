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

# 4. 🔍 CRITICAL: BEFORE pull, check for external modifications
ssh ha "cd /homeassistant && git status"
# If "working tree clean", skip to step 6
# If "uncommitted local changes", CONTINUE to step 5

# 5. 🔍 INSPECT changes before discarding
ssh ha "cd /homeassistant && git diff <file>"
# Analyze: Are these MY changes (safe) or EXTERNAL modifications (ASK USER)?
# Only if safe: checkout then pull
ssh ha "cd /homeassistant && git checkout -- <file> && git pull"

# 6. Pull (clean state)
ssh ha "cd /homeassistant && git pull"

# 7. Reload or restart
hass-cli service call automation.reload  # if reload sufficient
# OR
ssh ha "ha core restart"  # if restart needed (ASK FIRST!)

# 8. Verify
hass-cli state get sensor.new_entity
ssh ha "ha core logs | grep -i error | tail -20"
```

**⚠️ CRITICAL SAFETY:** Always `git diff` before `git checkout` to avoid losing external modifications.

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

## 🔍 Detecting Server Drift (Commits Behind + Uncommitted Files)

A blocked `git pull` is usually one scp'd file you can safely checkout. But sometimes the server has **silently drifted**: many commits behind origin *and* multiple uncommitted files from different concerns. That is **not** a checkout-and-pull — it's a **reconciliation problem** needing a human decision per file. Detect it *before* reaching for `git checkout`.

### Drift check (run before pulling)

```bash
ssh ha "cd /homeassistant && git log --oneline HEAD..origin/master | wc -l"   # how far behind
ssh ha "cd /homeassistant && git log --oneline HEAD..origin/master"           # what's incoming
ssh ha "cd /homeassistant && git status --short"                               # uncommitted local files
ssh ha "cd /homeassistant && git diff --name-only HEAD..origin/master"        # what the pull touches
```

### Read the signals

| Signal | Meaning | Action |
|---|---|---|
| 0 behind, 1 modified file (your scp) | Normal scp-conflict | diff → checkout that file → pull |
| **Many behind (5+) + multiple uncommitted files across concerns** | **Drifted tree** — real work never committed | **STOP. No blind `git checkout`.** Reconcile per file (server-vs-origin), commit/stash, then pull |
| Uncommitted files the pull doesn't touch | Unrelated local mods | Safe — pull proceeds, they stay modified |

**Why:** `git checkout -- <file>` assumes the local change is expendable. On a drifted tree those files may be **live work that exists only on the server** (sensor renames, debug config, UI dashboards) — checking them out destroys them irrecoverably.

**Real incident (2026-06-14):** a deploy was blocked by 5 uncommitted files while the server sat **12 commits behind** origin; two files were live work with no copy elsewhere. The fix was applied to the live working copy directly; reconciliation was deferred to the user rather than risk `git checkout`.

**Rule:** if `HEAD..origin/master` shows >1–2 commits OR `git status` shows uncommitted files you didn't create this session → treat as drift, surface it to the user, and never `git checkout` to force the pull.

---

## SCP + Git Pull Workflow (Avoiding Conflicts)

When you've tested changes via SCP and want to sync to git:

```bash
# 1. Commit your local changes
git add automations.yaml
git commit -m "Tested automation changes"
git push

# 2. 🔍 CHECK server status first
ssh ha "cd /homeassistant && git status"
# If "working tree clean", skip to step 6
# If "uncommitted local changes", CONTINUE to step 3

# 3. 🔍 CRITICAL: INSPECT before discarding
# Check what's actually in the file on the server
ssh ha "cd /homeassistant && git diff automations.yaml"

# 4. ANALYZE the diff:
#    - Only shows your SCP changes from this session? → Safe to continue
#    - Shows UNKNOWN/EXTERNAL modifications? → STOP, investigate first
#    - Shows mixed changes? → Manual merge needed, ask user

# 5. Only if diff shows ONLY your SCP changes, then checkout:
ssh ha "cd /homeassistant && git checkout -- automations.yaml"

# 6. Now pull (clean state)
ssh ha "cd /homeassistant && git pull"

# 7. Reload if needed
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
   │           - commit → push → status → (diff?) → checkout → pull → reload
   │
   └─ Already tested via SCP?
      └─ YES → Use SCP + Git Pull workflow
                - commit → push → status → diff → checkout → pull → reload
```

**⚠️ ALWAYS:** `git status` before `git pull` on HA server
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy via SCP | `scp file.yaml ha:/homeassistant/` |
| **Deploy via Git** | `ssh ha "cd /homeassistant && git status"` → (if clean) → `git pull` |
| View diffs | `ssh ha "cd /homeassistant && git diff file.yaml"` |
| Revert scp'd file | `ssh ha "cd /homeassistant && git checkout -- file.yaml"` |
| Reload automations | `hass-cli service call automation.reload` |

**⚠️ CRITICAL:** Always `git status` → `git diff` → `git checkout` → `git pull`

---

## 🚨 FAILURE RECOVERY: Git Pull Conflicts

**When `git pull` fails with "local changes would be overwritten":**

```bash
# ❌ WRONG: Pull fails, you're stuck
ssh ha "cd /homeassistant && git pull"
# Error: Your local changes to the following files would be overwritten...

# ✅ CORRECT: Recovery pattern
# Step 1: Check what's modified
ssh ha "cd /homeassistant && git status"

# Step 2: Inspect the changes (are they YOUR scp changes?)
ssh ha "cd /homeassistant && git diff <file>"

# Step 3: If safe, checkout specific files, then pull
ssh ha "cd /homeassistant && git checkout -- <files> && git pull"
```

**Key pattern:** `git pull` → fails → `git checkout -- <files>` → `git pull` (succeeds)

**One-liner for known scp files:**
```bash
ssh ha "cd /homeassistant && git checkout -- file.yaml && git pull"
```

---

## Common Pitfalls

| Mistake | Consequence | Solution |
|---------|-------------|----------|
| `git reset --hard` | Loses uncommitted work | Use `git checkout -- <files>` |
| `git pull` without checkout | Fails with conflicts | Checkout scp'd files first |
| Blind checkout without diff | Loses unknown changes | Always `git diff` first |
| SCP to wrong path | Changes not active | Use `ha:/homeassistant/` |
| Forgot to reload | Changes not active | Reload after deploy |
| Deployed to wrong file path (single file vs directory) | Changes not active, requires restart | Check configuration.yaml includes first |


---

## Reload Procedures: Which Reload to Use?

**CRITICAL:** Different object types require different reload commands. Using wrong reload = changes not active.

| Object Type Modified | Reload Command | What it Reloads |
|------------------|---------------|-----------------|
| **Automations** (`automations/**/*.yaml`) | `hass-cli service call automation.reload` | ONLY automations (NOT templates) |
| **Templates** (`templates/`) | `hass-cli service call homeassistant.reload_template_entity` | Template entities |
| **Scripts** (`scripts/**/*.yaml`) | `hass-cli service call script.reload` | Python scripts |
| **Input datetime helpers** (`input_datetime/`) | `hass-cli service call input_datetime.reload` | ONLY input_datetime helpers (NOT all input helpers) |
| **Scenes** (`scenes/`) | `hass-cli service call scene.reload` | Scenes |
| **configuration.yaml** | RESTART REQUIRED | `ssh ha "ha core restart"` (ASK FIRST!) |

### Reload Decision Tree

```
What did you modify?
├─ automations/ (YAML files) → hass-cli service call automation.reload (ONLY automations, NOT templates)
├─ scripts/ (YAML files) → hass-cli service call script.reload (ONLY Python scripts)
├─ templates/ (Jinja2 templates) → hass-cli service call homeassistant.reload_template_entity (ONLY template entities)
├─ input_datetime/ (helpers) → hass-cli service call input_datetime.reload (ONLY input_datetime helpers, NOT all input helpers)
├─ scenes/ (YAML files) → hass-cli service call scene.reload (ONLY scenes)
├─ configuration.yaml → ssh ha "ha core restart" (ASK USER FIRST!)
└─ Not sure? → Use most specific reload for your change type
```

### Examples

```bash
# After editing automation YAML
scp automations/climate/*.yaml ha:/homeassistant/automations/climate/
hass-cli service call automation.reload  # ONLY reloads automations

# After creating new input_datetime helpers
scp input_datetime/input_datetime.yaml ha:/homeassistant/input_datetime/
hass-cli service call input_datetime.reload  # Reloads ONLY helpers

# After editing template entities
scp templates/template_entity.yaml ha:/homeassistant/templates/
hass-cli service call homeassistant.reload_template_entity  # Reloads template entities

# After modifying configuration.yaml
git add configuration.yaml && git commit -m "Config change" && git push
ssh ha "cd /homeassistant && git pull"
# Ask user: "May I restart Home Assistant?"
ssh ha "ha core restart"
```

**Key Principle:** Use the most specific reload for what you changed. `automation.reload` is NOT a generic reload command.

### Reloads via the ha MCP server (no hass-cli needed)

Every reload above is a service call, so you can also fire it through the ha MCP server
— preferred when your dev host can't reach HA's LAN:

- Automations → `ha_call_service(domain="automation", service="reload")`
- Scripts → `ha_call_service(domain="script", service="reload")`
- Template entities → `ha_call_service(domain="homeassistant", service="reload_template_entity")`
- Everything reloadable → `ha_reload_core(target="all")`

### Trivial deploys don't need delegation

For a single-file edit you fully understand + one reload (no restart), execute the deploy
directly — don't spin up the deployment-orchestrator subagent. Delegate only for
multi-step, ambiguous, or drift-prone deploys (see the drift section above).

---


