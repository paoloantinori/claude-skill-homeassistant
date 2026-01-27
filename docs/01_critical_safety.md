# 01. Critical Safety Rules

**Home Assistant Manager - Critical Safety Documentation**

## 🚨🚨🚨 CRITICAL: NEVER RESTART WITHOUT ASKING 🚨🚨🚨

**MEMORIZE THIS RULE - NO EXCEPTIONS:**

**You are FORBIDDEN from executing `ha core restart` without:**
1. Explaining why you think a restart is needed
2. Getting EXPLICIT permission from the user

**Violating this rule disrupts all running automations and services for ~30+ seconds.**

**Examples of CORRECT behavior:**
- ✅ "Configuration.yaml changed. May I restart Home Assistant for this to take effect?"
- ✅ "New integration added. This requires a restart. Shall I proceed?"
- ✅ "I believe a restart is needed because [reason]. May I proceed?"

**Examples of WRONG behavior:**
- ❌ Restarting without asking first
- ❌ Saying "restarting..." and then doing it
- ❌ Assuming consent because the user didn't object

**When in doubt: ALWAYS ASK.**

---

## 🚨 CRITICAL GUARDRAILS - Reload vs Restart

**Golden Rule:** Prefer RELOAD over RESTART whenever possible.

### When to RELOAD (Fast, No Disruption)

| Operation | Command | Time | Disruption |
|-----------|---------|------|------------|
| Automations | `hass-cli service call automation.reload` | ~2s | None |
| Scripts | `hass-cli service call script.reload` | ~2s | None |
| Templates | `hass-cli service call homeassistant.reload_template_entity` | ~2s | None |
| Groups | `hass-cli service call group.reload` | ~2s | None |
| Core config | `hass-cli service call homeassistant.reload_core_config` | ~5s | Minimal |

**Use reload for:**
- Editing existing automations, scripts, templates
- Adding/removing automations, scripts, templates
- Changing configuration.yaml (only for certain things)
- Updating group definitions

**Reload triggers:**
- File modifications in: `automations/`, `scripts/`, `templates/`

### When to RESTART (Slow, Disruptive)

| Operation | Command | Time | Disruption |
|-----------|---------|------|------------|
| Full restart | `ssh ha "ha core restart"` | ~30-60s | **ALL services stop** |

**Use restart ONLY for:**
- Adding new HACS integrations
- Modifying `configuration.yaml` for integrations
- Adding new platforms (e.g., new `sensor:` platform)
- Python script dependencies changes
- After certain configuration changes

### ⚠️ KNOWN: Reload Doesn't Work for Everything

**These require restart (reload won't pick up changes):**
- New HACS integrations
- Template entities (new sensors/binary sensors defined in templates/)
- Some `configuration.yaml` changes
- Changes to `secrets.yaml`
- UI-based configuration changes

**If reload doesn't work:**
1. Check if the change type actually requires a restart
2. Ask user: "This change type requires a restart. May I proceed?"
3. NEVER restart without explicit permission

### Decision Tree

```
Did you change...
├─ automation/script/template file?
│  └─ YES → RELOAD (automation.reload, script.reload, etc.)
│
├─ configuration.yaml?
│  ├─ Integration/platform addition? → RESTART (ask first!)
│  └─ Other change? → Try reload, then restart if needed (ask!)
│
└─ Added new HACS integration?
   └─ RESTART (ask first!)
```

### Quick Reference Commands

```bash
# Reload automations
hass-cli service call automation.reload

# Reload scripts
hass-cli service call script.reload

# Reload templates
hass-cli service call homeassistant.reload_template_entity

# Reload core config
hass-cli service call homeassistant.reload_core_config

# Restart (ASK FIRST!)
ssh ha "ha core restart"
```

---

## Summary: Reload vs Restart

| Action | When | Must Ask? |
|--------|------|-----------|
| Reload automations/scripts/templates | After editing those files | No |
| Reload core config | After configuration.yaml changes (some) | No |
| Restart | Adding integrations, template entities, major changes | **YES** |

**Remember:** When in doubt, ASK. A 30-second interruption is better than an unexpected disruption during critical automations.
