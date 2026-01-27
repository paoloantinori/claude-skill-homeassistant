# 05. Lovelace Dashboards

**Home Assistant Manager - Dashboard Development**

---

## Dashboard Fundamentals

**What are Lovelace Dashboards?**
- JSON files in `.storage/` directory (e.g., `.storage/lovelace.control_center`)
- UI configuration for Home Assistant frontend
- Optimizable for different devices (mobile, tablet, wall panels)

**Critical Understanding:**
- Creating dashboard file is NOT enough - must register in `.storage/lovelace_dashboards`
- Dashboard changes don't require HA restart (just browser refresh)
- Use panel view for full-screen content (maps, cameras)
- Use sections view for organized multi-card layouts

---

## Dashboard Development Workflow

**Rapid Iteration with scp (Recommended):**

```bash
# 1. Make changes locally
vim .storage/lovelace.control_center

# 2. Deploy immediately (no git commit yet)
scp .storage/lovelace.control_center ha:/homeassistant/.storage/

# 3. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
# No HA restart needed!

# 4. Iterate: Repeat 1-3 until perfect

# 5. Commit when stable
git add .storage/lovelace.control_center
git commit -m "Update dashboard layout"
git push
```

**Why scp for dashboards:**
- ✅ Instant feedback (no HA restart)
- ✅ Iterate quickly on visual changes
- ✅ Commit only stable versions

---

## Creating New Dashboard

**Complete workflow:**

```bash
# Step 1: Create dashboard file
cp .storage/lovelace.my_home .storage/lovelace.new_dashboard

# Step 2: Register in lovelace_dashboards
# Edit .storage/lovelace_dashboards to add entry

# Step 3: Deploy both files
scp .storage/lovelace.new_dashboard ha:/homeassistant/.storage/
scp .storage/lovelace_dashboards ha:/homeassistant/.storage/

# Step 4: Restart HA (required for registry changes)
ssh ha "ha core restart"
```

**Dashboard registration format:**
```json
{
  "id": "new_dashboard",
  "show_in_sidebar": true,
  "icon": "mdi:tablet-dashboard",
  "title": "New Dashboard",
  "require_admin": false,
  "mode": "storage",
  "url_path": "new-dashboard"
}
```

---

## View Types Decision Matrix

| View Type | Best For | Characteristics |
|-----------|----------|-----------------|
| **Panel** | Full-screen content | Maps, cameras, single focus |
| **Sections** | Organized layouts | Multiple card types, scrollable |
| **Masonry** | Responsive grids | Auto-arranging cards |
| **Grid** | Precise control | Fixed positioning |

---

## Common Template Patterns

### State-Based Visibility

```yaml
visibility: "{{ states('input_boolean.show_panel') == 'on' }}"
```

### Entity Filters

```yaml
type: 'custom:config-template-card'
variables:
  FILTER: "input_select.filter_source"
entities:
  - input_select.filter_source
card:
  type: entity-filter
  entities:
    - entity1
    - entity2
  state_filter:
    - "on"
  filter: "${variables.FILTER}"
```

---

## Tablet Optimization

**Considerations for wall/tablet mounts:**
- Large touch targets (min 48x48px)
- High contrast (visibility in various lighting)
- Simplified layouts (reduced cognitive load)
- Critical info only (no clutter)
- Auto-refresh strategies (for dynamic content)

---

## Common Dashboard Pitfalls

| Pitfall | Solution |
|---------|----------|
| Invalid JSON | Validate: `python3 -m json.tool file.json` |
| Dashboard not appearing | Check `.storage/lovelace_dashboards` registration |
| Changes not visible | Hard refresh browser (Ctrl+F5) |
| Cards not loading | Check entity IDs exist |

---

## Quick Reference

```bash
# Deploy dashboard
scp .storage/lovelace.dashboard ha:/homeassistant/.storage/

# Validate JSON
python3 -m json.tool .storage/lovelace.dashboard > /dev/null

# Register new dashboard (requires restart)
scp .storage/lovelace_dashboards ha:/homeassistant/.storage/

# Quick iteration cycle
vim .storage/lovelace.dashboard
scp .storage/lovelace.dashboard ha:/homeassistant/.storage/
# Refresh browser
```

---

## .gitignore for Dashboards

```gitignore
# Exclude .storage/ by default
.storage/*

# Include specific dashboards
!.storage/lovelace.control_center
!.storage/lovelace.control_center_test
!.storage/lovelace_dashboards
```
