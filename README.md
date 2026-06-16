# DOPEHOUSE OPENMIC

## AI Music Creation Platform

**Created by Jacob Daniel Powell**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)

DOPEHOUSE OPENMIC is a professional AI music creation platform that generates music, lyrics, and audio projects through the AceDataCloud Suno API. It integrates with any MCP-compatible client (Claude, VS Code, Cursor, etc.).

---

## 🎵 Features

- **Music Generation** - Create AI songs from text prompts
- **Custom Lyrics & Style** - Full control over lyrics, title, and music style
- **Song Extension** - Continue existing songs from any timestamp
- **Cover/Remix** - Create cover versions in different styles
- **Lyrics Generation** - Generate structured lyrics from descriptions
- **Persona Management** - Save and reuse voice styles
- **Task Tracking** - Monitor generation progress and retrieve results
- **Stem Separation** - Extract vocals, instruments, and individual tracks
- **Media Conversion** - MP4, WAV, MIDI formatting

## 🚀 Quick Start

### 1. Get Your API Token
Sign up at [AceDataCloud Platform](https://platform.acedata.cloud) and get your API token.

### 2. Installation

#### Windows (Recommended)
Download the installer from [dopehouseopenmic.com](https://dopehouseopenmic.com) and run it.

#### Python (pip)
```bash
pip install dopehouse-openmic
```

#### Docker
```bash
docker pull jacobdpowell/dopehouse-openmic:latest
docker run -p 8000:8000 jacobdpowell/dopehouse-openmic:latest
```

### 3. Configure & Run

1. Set your API token:
   ```bash
   set ACEDATACLOUD_API_TOKEN=your_token_here
   ```

2. Run the server:
   ```bash
   # Stdio mode (for Claude Desktop, etc.)
   dopehouse-openmic

   # HTTP mode (for remote access)
   dopehouse-openmic --transport http --port 8000
   ```

## 🔧 Available Tools

### Music Generation
| Tool | Description |
|------|-------------|
| `suno_generate_music` | Generate music from a text prompt |
| `suno_generate_custom_music` | Generate with custom lyrics, title, and style |
| `suno_extend_music` | Extend an existing song from a timestamp |
| `suno_cover_music` | Create a cover/remix version |
| `suno_concat_music` | Merge extended segments into complete audio |
| `suno_remaster_music` | Remaster a song to improve audio quality |
| `suno_mashup_music` | Blend multiple songs into a mashup |

### Lyrics
| Tool | Description |
|------|-------------|
| `suno_generate_lyrics` | Generate song lyrics from a prompt |
| `suno_optimize_style` | Optimize style descriptions |
| `suno_mashup_lyrics` | Combine two sets of lyrics |

### Persona Management
| Tool | Description |
|------|-------------|
| `suno_create_persona` | Save a voice style from Suno audio |
| `suno_create_voice` | Create persona from external audio URL |
| `suno_list_personas` | List saved personas |
| `suno_delete_persona` | Delete a persona |
| `suno_generate_with_persona` | Generate using saved voice style |

## 📁 Project Structure

```
DOPEHOUSE-OPENMIC/
├── core/          # Core modules (config, server, client, types, etc.)
├── tools/         # MCP tool definitions
├── prompts/       # LLM guidance prompts
├── tests/         # Test suite
├── deploy/        # Kubernetes deployment configs
├── resources/     # Logo, icons, branding
├── installer/     # Build scripts and installer config
├── main.py        # Entry point
└── README.md
```

## 💻 Development

```bash
pip install -e ".[dev]"
pytest --cov=core --cov=tools
ruff check .
```

## 📜 License

Proprietary - Copyright (c) 2026 Jacob Daniel Powell. All rights reserved.

## 🌐 Links

- [Website](https://dopehouseopenmic.com)
- [Documentation](https://dopehouseopenmic.com/docs)
- [GitHub](https://github.com/jacobdpowell/dopehouse-openmic)

---

*Created with passion by Jacob Daniel Powell*
