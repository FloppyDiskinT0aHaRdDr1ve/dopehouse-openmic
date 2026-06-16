"""Task query tools for DOPEHOUSE OPENMIC."""

import asyncio
from typing import Annotated

from pydantic import Field

from core.client import client
from core.server import mcp
from core.utils import format_task_result


@mcp.tool()
async def suno_get_task(
    task_id: Annotated[str, Field(description="The task ID from a generation request.")],
) -> str:
    """Query the status and result of a music generation task.

    Use this to check if a generation is complete and retrieve the resulting
    audio URLs, titles, lyrics, and other metadata.

    Task states:
    - 'pending': Still in progress
    - 'processing': Being processed
    - 'complete': Finished successfully
    - 'failed': Generation failed

    Returns:
        Task status and generated audio information.
    """
    result = await client.query_task(id=task_id, action="retrieve")
    response = result.get("response", {})
    is_complete = response.get("success", False)
    if not is_complete:
        await asyncio.sleep(5)
    return format_task_result(result)


@mcp.tool()
async def suno_get_tasks_batch(
    task_ids: Annotated[list[str], Field(description="List of task IDs to query.")],
) -> str:
    """Query multiple music generation tasks at once.

    Returns:
        Status and audio information for all queried tasks.
    """
    result = await client.query_task(ids=task_ids, action="retrieve_batch")
    if "error" in result:
        error = result.get("error", {})
        return f"Error: {error.get('code', 'unknown')} - {error.get('message', 'Unknown error')}"
    lines = [f"Total Tasks: {result.get('count', 0)}", ""]
    for item in result.get("items", []):
        response_info = item.get("response", {})
        state = item.get("state", "unknown")
        success = response_info.get("success", False)
        lines.extend([
            f"=== Task: {item.get('id', 'N/A')} ===",
            f"State: {state}",
            f"Created At: {item.get('created_at', 'N/A')}",
            f"Success: {success}",
        ])
        if state == "complete" and success:
            for audio in response_info.get("data", []):
                lines.append(f"  - {audio.get('title', 'Untitled')}: {audio.get('audio_url', 'N/A')}")
        elif state == "failed":
            lines.append(f"  Error: {response_info.get('error', 'Unknown error')}")
        else:
            lines.append(f"  Still {state} — keep polling.")
        lines.append("")
    return "\n".join(lines)
