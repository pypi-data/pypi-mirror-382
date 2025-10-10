# claudecut

AI-powered vibe video editing with Claude Agent based on captions.

![claudecut](img/claudecut.png)

## Requirements

- **[ffmpeg](https://github.com/FFmpeg/FFmpeg)** (must be installed on your system - [installation guide](https://ffmpeg.org/download.html))
- **[Claude Code](https://www.claude.com/product/claude-code)** version 2.0.0 or higher
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

## Acknowledgments

This project uses [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped) for accurate speech-to-text transcription with word-level timestamps.

## License

MIT License - see [LICENSE](LICENSE) file for details.
