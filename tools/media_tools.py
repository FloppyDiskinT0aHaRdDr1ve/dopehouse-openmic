"""Media conversion and extraction tools for DOPEHOUSE OPENMIC."""

import json
from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp
from core.utils import format_audio_result


@mcp.tool()
async def suno_get_mp4(
    audio_id: Annotated[str, Field(description="The song ID to get the MP4 video for.")],
) -> str:
    """Get an MP4 video version of a generated song.

    Returns:
        Task ID and MP4 video information.
    """
    result = await client.get_mp4(audio_id=audio_id)
    return format_audio_result(result)


@mcp.tool()
async def suno_get_timing(
    audio_id: Annotated[str, Field(description="The song ID to get timing/subtitle data for.")],
) -> str:
    """Get timing and subtitle data for a generated song.

    Returns:
        Timing data with word-level timestamps.
    """
    result = await client.get_timing(audio_id=audio_id)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_extract_vocals(
    audio_id: Annotated[str, Field(description="The song ID to extract vocals from.")],
    vocal_start: Annotated[float | None, Field(description="Start time for vocal extraction.")] = None,
    vocal_end: Annotated[float | None, Field(description="End time for vocal extraction.")] = None,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Extract the vocal track from a generated song (stem separation).

    Returns:
        Task ID and extracted vocal audio information.
    """
    payload: dict = {"audio_id": audio_id}
    if vocal_start is not None:
        payload["vocal_start"] = vocal_start
    if vocal_end is not None:
        payload["vocal_end"] = vocal_end
    if callback_url:
        payload["callback_url"] = callback_url
    result = await client.get_vox(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_get_wav(
    audio_id: Annotated[str, Field(description="The song ID to get the WAV format for.")],
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Get the lossless WAV format of a generated song.

    Returns:
        Task ID and WAV audio information.
    """
    payload: dict = {"audio_id": audio_id}
    if callback_url:
        payload["callback_url"] = callback_url
    result = await client.get_wav(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_get_midi(
    audio_id: Annotated[str, Field(description="The song ID to get MIDI data for.")],
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Get MIDI data extracted from a generated song.

    Returns:
        Task ID and MIDI data information.
    """
    payload: dict = {"audio_id": audio_id}
    if callback_url:
        payload["callback_url"] = callback_url
    result = await client.get_midi(**payload)
    return format_audio_result(result)
