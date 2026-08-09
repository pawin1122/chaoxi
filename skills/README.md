# chaoxi Skills

AI coding assistant skills for the chaoxi CLI tool. Teaches AI agents how to query A-share announcements from cninfo.com.cn.

## Versions

| Platform | File | Description |
|---|---|---|
| OpenCode | `opencode/chaoxi/SKILL.md` | YAML frontmatter + full command reference |
| Claude Code | `claude-code/chaoxi.md` | English command reference + use cases |
| Codex (OpenAI) | `codex/chaoxi.md` | English parameter table + JSON schema |
| Pi Agent | `pi-agent/chaoxi.md` | Concise English quick reference |

## Installation

### OpenCode

```bash
# Global install
cp -r skills/opencode/chaoxi ~/.config/opencode/skills/

# Project-level (place in .opencode/skills/chaoxi/SKILL.md)
```

### Claude Code

```bash
cp skills/claude-code/chaoxi.md ~/.claude/skills/chaoxi.md
```

### Codex

Reference in project `.codex` config:

```yaml
instructions: skills/codex/chaoxi.md
```

### Pi Agent

Paste the content of `skills/pi-agent/chaoxi.md` into Pi Agent's custom instructions.
