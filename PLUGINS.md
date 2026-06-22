# Installed Plugins

Plugins installed in this Claude Code setup. Plugin code itself not published here
(third-party cache) — install from the marketplaces below.

## Marketplaces

| Marketplace | Source |
|---|---|
| `claude-plugins-official` | github: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| `caveman` | github: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) |
| `citedy` | github: [citedy/claude-plugins](https://github.com/citedy/claude-plugins) |

## Plugins

| Plugin | Marketplace | Version | Scope |
|---|---|---|---|
| `caveman` | caveman | `63e797cd753b` | user |
| `game-sounds` | citedy | `3.0.0` | user |
| `frontend-design` | claude-plugins-official | `19a119f97e36` | user + project |
| `context7` | claude-plugins-official | `19a119f97e36` | user |
| `code-review` | claude-plugins-official | `19a119f97e36` | user |
| `github` | claude-plugins-official | `19a119f97e36` | user |

## Install

```bash
# add a marketplace, then install a plugin from it
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace add JuliusBrussee/caveman
/plugin marketplace add citedy/claude-plugins

/plugin install caveman@caveman
/plugin install game-sounds@citedy
/plugin install frontend-design@claude-plugins-official
/plugin install context7@claude-plugins-official
/plugin install code-review@claude-plugins-official
/plugin install github@claude-plugins-official
```
