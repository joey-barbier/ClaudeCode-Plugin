# CLAUDE.md - Public Marketplace

## Project Structure

This is a marketplace of Claude Code plugins. Each plugin lives in `plugins/<plugin-name>/` with its own `.claude-plugin/plugin.json`.

The root `.claude-plugin/marketplace.json` is the central registry that lists ALL available plugins.

## Critical Rules

### marketplace.json must stay in sync
When adding, removing, or updating a plugin:
1. Update the plugin's own `plugin.json` (version, description, etc.)
2. **Also update `.claude-plugin/marketplace.json`** — add the new entry or sync the version/description
3. These two files must ALWAYS match on `version` and `description`

### Checklist for new plugin release
- [ ] Plugin folder created in `plugins/<name>/`
- [ ] `plugins/<name>/.claude-plugin/plugin.json` filled
- [ ] **`.claude-plugin/marketplace.json` updated with new entry**
- [ ] README updated with new plugin in catalog (all languages)
