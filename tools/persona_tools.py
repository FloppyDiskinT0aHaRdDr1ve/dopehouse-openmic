"""Persona management tools for DOPEHOUSE OPENMIC."""

import json
from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp
from core.utils import format_persona_result


@mcp.tool()
async def suno_create_persona(
    audio_id: Annotated[str, Field(description="ID of the audio to use as the persona reference.")],
    name: Annotated[str, Field(description="Name for this persona.")],
    vox_audio_id: Annotated[str | None, Field(description="Optional audio ID for hybrid vocal personas.")] = None,
    vocal_start: Annotated[float | None, Field(description="Start time of vocal segment.")] = None,
    vocal_end: Annotated[float | None, Field(description="End time of vocal segment.")] = None,
    description: Annotated[str | None, Field(description="Description of the singer's style.")] = None,
) -> str:
    """Create a new artist persona from an existing audio's vocal style.

    Saves vocal characteristics from a generated song for reuse.

    Returns:
        Persona ID for use with suno_generate_with_persona.
    """
    payload: dict = {"audio_id": audio_id, "name": name}
    if vox_audio_id:
        payload["vox_audio_id"] = vox_audio_id
    if vocal_start is not None:
        payload["vocal_start"] = vocal_start
    if vocal_end is not None:
        payload["vocal_end"] = vocal_end
    if description:
        payload["description"] = description
    result = await client.create_persona(**payload)
    return format_persona_result(result)


@mcp.tool()
async def suno_list_personas(
    user_id: Annotated[str, Field(description="The user ID to list personas for.")],
    limit: Annotated[int, Field(description="Maximum number of personas to return.")] = 50,
    offset: Annotated[int, Field(description="Number of personas to skip for pagination.")] = 0,
) -> str:
    """List all saved artist personas for a user.

    Returns:
        List of personas with their IDs, names, and descriptions.
    """
    result = await client.list_personas(user_id=user_id, limit=limit, offset=offset)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def suno_delete_persona(
    persona_id: Annotated[str, Field(description="The persona ID to delete.")],
    user_id: Annotated[str | None, Field(description="The user ID for ownership verification.")] = None,
) -> str:
    """Delete a saved artist persona.

    Returns:
        Confirmation of the deletion.
    """
    payload: dict = {"persona_id": persona_id}
    if user_id:
        payload["user_id"] = user_id
    result = await client.delete_persona(**payload)
    return json.dumps(result, ensure_ascii=False, indent=2)
