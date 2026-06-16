"""Lyrics generation tools for DOPEHOUSE OPENMIC."""

from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp
from core.types import DEFAULT_LYRICS_MODEL, LyricsModel
from core.utils import format_lyrics_result


@mcp.tool()
async def suno_generate_lyrics(
    prompt: Annotated[str, Field(description="Description of the lyrics you want. Include theme, mood, genre.")],
    model: Annotated[LyricsModel, Field(description="Model version for lyrics generation.")] = DEFAULT_LYRICS_MODEL,
) -> str:
    """Generate song lyrics from a text prompt.

    Creates structured lyrics with proper song sections (Verse, Chorus, Bridge, etc.)
    based on your description.

    Returns:
        Generated lyrics with title, status, and formatted text with section markers.
    """
    result = await client.generate_lyrics(prompt=prompt, model=model)
    return format_lyrics_result(result)
