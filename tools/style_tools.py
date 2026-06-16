"""Style and mashup tools for DOPEHOUSE OPENMIC."""

import json
from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp


@mcp.tool()
async def suno_optimize_style(
    prompt: Annotated[str, Field(description="Style prompt words that need optimization.")],
) -> str:
    """Optimize a music style description for better generation results.

    Returns:
        Optimized style description ready for use in music generation.
    """
    result = await client.get_style(prompt=prompt)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_mashup_lyrics(
    lyrics_a: Annotated[str, Field(description="The first set of lyrics to combine.")],
    lyrics_b: Annotated[str, Field(description="The second set of lyrics to combine.")],
) -> str:
    """Generate mashup lyrics by combining two sets of lyrics.

    Returns:
        Combined mashup lyrics.
    """
    result = await client.mashup_lyrics(lyrics_a=lyrics_a, lyrics_b=lyrics_b)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_upload_audio(
    audio_url: Annotated[str, Field(description="Public URL of the audio file to upload.")],
) -> str:
    """Upload an external audio file for use in subsequent operations.

    Returns:
        Upload result with audio ID for use in subsequent operations.
    """
    result = await client.upload_audio(audio_url=audio_url)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_create_voice(
    audio_url: Annotated[str, Field(description="Publicly accessible URL of the audio file.")],
    name: Annotated[str, Field(description="Name for the custom voice persona.")],
    description: Annotated[str | None, Field(description="Description of the voice persona.")] = None,
) -> str:
    """Create a custom voice persona from an external audio URL.

    Returns:
        Persona ID for use with suno_generate_with_persona.
    """
    payload: dict = {"audio_url": audio_url, "name": name}
    if description:
        payload["description"] = description
    result = await client.create_voice(**payload)
    return json.dumps(result, ensure_ascii=False, indent=2)
