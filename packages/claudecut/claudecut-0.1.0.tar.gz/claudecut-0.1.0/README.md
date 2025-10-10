# claudecut

AI-powered vibe video editing with Claude Agent based on captions.

![claudecut](img/claudecut.png)

## Requirements

- **ffmpeg** (must be installed on your system)
- **Claude Code** version 2.0.0 or higher
- **~1.5GB disk space** (Whisper large-v3-turbo model downloads on first run)

## Installation

**From PyPI:**
```bash
uvx claudecut
```

**Local development:**
```bash
git clone https://github.com/mellebrouwer/claudecut.git
cd claudecut
uv pip install -e .
uv run claudecut
```
