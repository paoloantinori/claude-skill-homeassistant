---
name: home-assistant-manager
description: Expert-level Home Assistant configuration management with deployment workflows, remote CLI access via SSH and hass-cli, automation verification, log analysis, reload vs restart optimization, and Lovelace dashboard management.
---

# Home Assistant Manager

Expert-level Home Assistant configuration management with efficient workflows, remote CLI access, and verification protocols.

## Critical Rules

1. **NEVER restart without asking** — see [docs/01_critical_safety.md](docs/01_critical_safety.md)
2. **ALWAYS use hass-cli, NEVER curl** — see [docs/07_remote_access.md](docs/07_remote_access.md)
3. **ALWAYS check configuration.yaml FIRST** for file organization — see [docs/10_file_organization.md](docs/10_file_organization.md)

| Rule | Violation | Correct Approach |
|------|-----------|------------------|
| NO restart without asking | `ssh ha "ha core restart"` | Always ask: "May I restart?" |
| NO curl for HA API | `curl -H "Authorization: Bearer $TOKEN" ...` | Use `hass-cli state get/service call` |
| NO grep for SSH fingerprint | `ssh ha ... \| grep -v "Host key..."` | Use `ssh -oVisualHostKey=no ha ...` |
| NO blind git checkout | `ssh ha "cd /homeassistant && git checkout ."` | Always `git diff` first |

## Documentation Index

| Topic | File | When to Read |
|-------|------|--------------|
| Critical Safety | [01_critical_safety.md](docs/01_critical_safety.md) | Before ANY HA operation |
| Deployment | [02_deployment.md](docs/02_deployment.md) | Before deploying changes |
| Validation | [03_validation.md](docs/03_validation.md) | Before deployment |
| Automation Testing | [04_automation_testing.md](docs/04_automation_testing.md) | After automation changes |
| Lovelace Dashboards | [05_lovelace_dashboards.md](docs/05_lovelace_dashboards.md) | When working with UI |
| Common Mistakes | [06_common_mistakes.md](docs/06_common_mistakes.md) | When encountering errors |
| Remote Access | [07_remote_access.md](docs/07_remote_access.md) | For hass-cli/SSH patterns |
| Quick Reference | [08_quick_reference.md](docs/08_quick_reference.md) | Command cheat sheet |
| Logger Configuration | [09_logger_configuration.md](docs/09_logger_configuration.md) | When adjusting log levels |

## Quick Start

```bash
source .env                                          # 1. Load environment
# Edit files...                                      # 2. Make changes locally
ssh -oVisualHostKey=no ha "ha core check"            # 3. Validate
scp file.yaml ha:/homeassistant/                     # 4a. Deploy via SCP (testing)
# OR: git push && ssh ha "cd /homeassistant && git pull"  # 4b. Deploy via Git (final)
hass-cli service call automation.reload              # 5. Reload
hass-cli state get entity.name                       # 6. Verify
```

## Decision Trees

### Reload vs Restart

```
Did you change...
├─ automation/script/template? → RELOAD
├─ configuration.yaml integration? → RESTART (ASK FIRST!)
├─ template entity? → RESTART (ASK FIRST!)
└─ Not sure? → Check docs/01_critical_safety.md
```

### Git vs SCP

```
Are you still testing?
├─ YES → Use SCP (rapid iteration)
└─ NO → Use Git (version controlled)
```

## Quick Command Reference

| Task | Command |
|------|---------|
| Check file organization | `grep -A 2 "input_boolean:" configuration.yaml` |
| Validate config | `ssh ha "ha core check"` |
| Reload automations | `hass-cli service call automation.reload` |
| Reload scripts | `hass-cli service call script.reload` |
| Reload templates | `hass-cli service call homeassistant.reload_template_entity` |
| Restart HA | `ssh ha "ha core restart"` (**ASK FIRST!**) |
| Get state | `hass-cli state get entity.name` |
| List states | `hass-cli state list` |
| Trigger automation | `hass-cli service call automation.trigger --arguments entity_id=automation.name` |
| View logs | `ssh ha "ha core logs \| tail -50"` |
| Deploy via SCP | `scp file.yaml ha:/homeassistant/` |
| Deploy via Git | `ssh ha "cd /homeassistant && git status"` → (if clean) → `git pull` |

## Path Reference

| Location | Path |
|----------|------|
| Project root | `/home/pantinor/data/repo/personal/hassio/` |
| HA server (via SSH) | `ha:/homeassistant/` |
| Automations | `automations/*/` |
| Scripts | `scripts/*/` |
| Templates | `templates/` |
| Dashboards | `.storage/lovelace.*` |

## Utility Scripts

Python helper scripts in `.claude/skills/home-assistant-manager/scripts/`:

| Script | Purpose | Agent |
|--------|---------|-------|
| `ha_entity_metadata.py` | Bulk labels, icons, areas | `ha-entity-metadata` |
| `ha_expose_entities.py` | Expose/unexpose to conversation | `ha-conversation-exposure` |
| `ha_backup_registry.py` | Registry backup and restore | `ha-registry-backup` |
| `ha_migrate_automation_ids.py` | Automation ID migration | `ha-automation-id-migration` |

Common workflows:
- **Add metadata**: `stats` → `export` → edit → `apply --dry-run` → `apply`
- **Expose for voice**: `list` → `expose <entity>` → `check <entity>`
- **Backup before migration**: `backup` → [make changes] → `restore <timestamp>` if needed
- **Migrate IDs**: `generate` → edit → `preview` → update YAML → `execute`

## Subagent Delegation

### Decision Matrix

| Task Type | Delegate To | Trigger Words |
|-----------|-------------|---------------|
| Log analysis | `ha-log-analyzer` | "check logs", "analyze logs", "errors", "debug" |
| Automation verification | `ha-automation-verifier` | "test automation", "verify logic", "did it fire?" |
| YAML validation | `ha-yaml-validator` | "validate yaml", "check yaml", "yaml syntax" |
| Config validation | `ha-config-validator` | "validate config", "check config", "safe to deploy?" |
| Deployment | `ha-deployment-orchestrator` | "deploy", "scp", "git push", "reload" |
| Git sync (3-way) | `ha-git-sync` | "sync git", "check sync status", "repos in sync" |
| Dashboard work | `ha-lovelace-dashboard-tester` | "dashboard", "lovelace", "UI", "card" |
| Service call testing | `ha-service-call-tester` | "test service call", "call service" |
| Entity metadata | `ha-entity-metadata` | "set labels", "assign icons", "set areas" |
| Conversation exposure | `ha-conversation-exposure` | "expose entities", "voice control" |
| Registry backup | `ha-registry-backup` | "backup registry", "restore registry" |
| Automation ID migration | `ha-automation-id-migration` | "migrate ids", "fix _2 duplicates" |

### Delegation Flow

```
Task identified → Consult matrix → Match found? → YES: Delegate to agent → NO: Proceed directly
```

**Always delegate when a match exists.** Only skip if user explicitly says "do it directly."

## Auto-Improve

When commands fail: analyze error → try correcting command → after success, document pattern.

See [docs/06_common_mistakes.md](docs/06_common_mistakes.md) for known patterns.
