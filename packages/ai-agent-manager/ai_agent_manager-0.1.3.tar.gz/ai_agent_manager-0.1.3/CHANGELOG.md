# Changelog

All notable changes to AI Agent Manager will be documented in this file.

## [0.1.0] - 2025-10-08

### 🎉 Initial Beta Release

First public release of AI Agent Manager - a terminal UI for managing AI agents across multiple tools.

### ✨ Features

**TUI (Terminal User Interface):**
- Visual menu-driven interface with keyboard navigation
- Dual-pane agent editor with multi-select (Space key)
- Real-time agent configuration preview
- Integrated help and keyboard shortcuts
- Error logging to `~/.config/ai-configurator/logs/tui.log`

**Agent Management:**
- Create, edit, rename, delete agents
- Visual resource selection with checkboxes
- Visual MCP server selection with checkboxes
- Auto-export to Q CLI (`~/.aws/amazonq/cli-agents/`)
- Manual export with `x` key
- Agent validation

**Library Management:**
- Base library with 5 default templates (daily-assistant, software-engineer, system-administrator, product-owner, software-architect)
- Personal library for custom files
- Clone base files to personal for editing
- Create new files with templates
- Visual separation of base vs personal files

**MCP Server Management:**
- Add servers by pasting JSON configs
- Flexible JSON parsing (handles multiple formats)
- Edit server configurations
- Delete servers
- Browse MCP registry

**Package:**
- Published as `ai-agent-manager` on PyPI
- CLI commands: `ai-agent-manager` and `ai-config`
- Bundled templates included in package
- GitHub Actions CI/CD pipeline

### 📝 Notes

This is a beta release. Feedback and bug reports welcome at https://github.com/jschwellach/ai-configurator/issues

---

## [4.0.0] - 2025-10-07 (Internal)

### 🎉 Major Release - Complete Redesign

AI Configurator v4.0 was a complete rewrite focused on Amazon Q CLI integration with a visual TUI interface.

### ✨ Added

**TUI (Terminal User Interface):**
- Visual menu-driven interface with keyboard navigation
- Dual-pane agent editor with multi-select (Space key)
- Real-time agent configuration preview
- Integrated help and keyboard shortcuts
- Error logging to `~/.config/ai-configurator/logs/tui.log`

**Agent Management:**
- Create, edit, rename, delete agents
- Visual resource selection with checkboxes
- Visual MCP server selection with checkboxes
- Auto-export to Q CLI (`~/.aws/amazonq/cli-agents/`)
- Manual export with `x` key
- Agent validation

**Library Management:**
- Base library (shared templates)
- Personal library (custom files)
- Clone base files to personal for customization
- Edit files in your preferred editor
- Create new markdown files
- Visual separation between base and personal files

**MCP Server Management:**
- Add servers by pasting JSON configs
- Flexible JSON parsing (handles multiple formats)
- Edit server configurations
- Delete servers
- Sync with MCP registry
- Auto-strip trailing commas from pasted JSON

**CLI Commands:**
- Simplified command structure: `ai-config <resource> <action>`
- Agent commands: list, create, export
- Library commands: list
- MCP commands: list
- System commands: status, health

### 🔄 Changed

- **Breaking**: Complete rewrite of internal architecture
- **Breaking**: New configuration directory structure
- **Breaking**: Agents now stored in `~/.config/ai-configurator/agents/`
- **Breaking**: Library split into `base/` and `personal/` directories
- **Breaking**: MCP servers in `~/.config/ai-configurator/registry/servers/`

### 🗑️ Removed

- Old CLI interface (replaced with simplified version)
- Profile system (replaced with agents)
- Hook system (may return in future version)
- Context manager (replaced with library)

### 🐛 Fixed

- Library file indexing now uses relative paths
- MCP server JSON parsing handles multiple formats
- Agent editor properly handles immutable Pydantic models
- Cursor position preserved during table refresh
- Editor selection (kate, vim, vi) with proper blocking

### 📚 Documentation

- Complete README rewrite with quick start guide
- TUI Guide with keyboard shortcuts
- Agent Editor Guide with dual-pane usage
- Migration Guide from v3.x

### 🔧 Technical

- Built with Textual TUI framework
- Pydantic models for data validation
- Async-safe event handling
- Comprehensive error logging
- Type hints throughout codebase

## [3.x] - Previous Versions

See git history for v3.x changes.
