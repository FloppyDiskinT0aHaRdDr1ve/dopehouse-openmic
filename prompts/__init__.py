"""Prompt templates for DOPEHOUSE OPENMIC."""

from core.server import mcp


@mcp.prompt()
def suno_music_generation_guide() -> str:
    """Guide for choosing the right tool for music generation."""
    return """# Music Generation Guide

When the user wants to generate music, choose the appropriate tool based on their needs:

## Quick Generation (Inspiration Mode)
**Tool:** `suno_generate_music`
**Use when:**
- User gives a simple description
- User wants Suno to handle lyrics and arrangement
- Quick, low-effort music creation

## Custom Generation (Full Control)
**Tool:** `suno_generate_custom_music`
**Use when:**
- User provides specific lyrics
- User wants control over title and style
- User specifies vocal gender preference

## Extending Songs
**Tool:** `suno_extend_music`
**Use when:**
- User wants to make a song longer
- Building a multi-part composition

## Creating Covers
**Tool:** `suno_cover_music`
**Use when:**
- User wants a different version of an existing song

## Generating Lyrics Only
**Tool:** `suno_generate_lyrics`
**Use when:**
- User wants lyrics without music yet

## Checking Status
**Tool:** `suno_get_task`
**Use when:**
- Generation takes time and user wants to check if it's ready

## Important Notes:
1. Music generation is async in MCP - generation tools return quickly with a task_id
2. After any generation call, use `suno_get_task` to poll for the final result
3. CRITICAL: Only `state: "complete"` with `success: true` means the task is done
4. Default model is chirp-v5-5
5. For longest songs (8 min), use chirp-v5 or chirp-v4-5-plus
6. Vocal gender only works on v4.5+ models
"""


@mcp.prompt()
def suno_workflow_examples() -> str:
    """Common workflow examples for music generation."""
    return """# Workflow Examples

## Workflow 1: Quick Song Generation
1. Call `suno_generate_music(prompt="...")`
2. Poll with `suno_get_task(task_id)` until state is complete

## Workflow 2: Custom Song with User's Lyrics
1. User provides lyrics
2. Call `suno_generate_custom_music(lyric=..., title="...", style="...")`
3. Poll with `suno_get_task(task_id)` until complete

## Workflow 3: Creating a Long Song (>4 minutes)
1. Generate initial song
2. Call `suno_extend_music(audio_id, new_lyrics, continue_at)`
3. Repeat as needed
4. Call `suno_concat_music(last_audio_id)` to merge

## Workflow 4: Consistent Voice Across Songs
1. Generate a song the user likes
2. Call `suno_create_persona(audio_id, name="My Voice")`
3. Use `suno_generate_with_persona(audio_id, persona_id, prompt)` for future songs

## Workflow 5: Cover/Remix
1. Call `suno_cover_music(audio_id, prompt="jazz version", style="smooth jazz")`
2. Poll until complete
"""


@mcp.prompt()
def suno_style_suggestions() -> str:
    """Style and prompt writing suggestions."""
    return """# Style Prompt Guide

## Effective Prompt Writing

Good prompts include:
- **Genre:** pop, rock, jazz, classical, electronic, hip-hop
- **Mood:** happy, sad, energetic, calm, dark, uplifting
- **Instruments:** guitar, piano, drums, synthesizer, violin
- **Tempo:** slow, mid-tempo, fast, upbeat, ballad
- **Era/Style:** 80s, 90s, modern, vintage, retro, futuristic

## Example Prompts by Genre

**Pop:** "Catchy pop song, upbeat, synth hooks, danceable, modern production"

**Rock:** "Hard rock anthem, electric guitars, powerful drums, stadium rock feel"

**Jazz:** "Smooth jazz, saxophone solo, walking bass, brushed drums, late night vibe"

**Electronic:** "EDM banger, heavy bass drops, synth arpeggios, festival energy"

**Classical:** "Orchestral piece, strings, dramatic, cinematic, emotional crescendo"

**Hip-Hop:** "Trap beat, 808 bass, hi-hats, confident flow, modern hip-hop"

## Lyric Section Tips

Each section has a purpose:
- **[Intro]:** Set the mood, can be instrumental
- **[Verse]:** Tell the story, build narrative
- **[Pre-Chorus]:** Build tension before the hook
- **[Chorus]:** The catchiest, most memorable part
- **[Bridge]:** Contrast, often emotional peak
- **[Outro]:** Wind down, resolve the song
"""
