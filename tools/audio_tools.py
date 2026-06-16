"""Audio generation tools for DOPEHOUSE OPENMIC."""

from typing import Annotated, Any

from pydantic import Field

from core.client import client
from core.server import mcp
from core.types import DEFAULT_MODEL, SunoModel, VariationCategory, VocalGender
from core.utils import format_audio_result


@mcp.tool()
async def suno_generate_music(
    prompt: Annotated[str, Field(description="Description of the music to generate. Be descriptive about genre, mood, instruments, and theme. Examples: 'A happy birthday song with acoustic guitar', 'Epic orchestral battle music with dramatic choir'")],
    model: Annotated[SunoModel, Field(description="Suno model version. 'chirp-v5-5' is the latest and recommended.")] = DEFAULT_MODEL,
    instrumental: Annotated[bool, Field(description="If true, generate instrumental music without vocals.")] = False,
    variation_category: Annotated[VariationCategory | None, Field(description="Variation intensity for v5+ models.")] = None,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL for async notifications.")] = None,
) -> str:
    """Generate AI music from a text prompt using Inspiration Mode.

    This is the simplest way to create music - just describe what you want and Suno
    will automatically generate appropriate lyrics, melody, style, and arrangement.

    Returns:
        Task ID and generated audio information including URLs, title, lyrics, and duration.
    """
    payload: dict = {
        "action": "generate",
        "prompt": prompt,
        "model": model,
        "instrumental": instrumental,
        "callback_url": callback_url,
    }
    if variation_category:
        payload["variation_category"] = variation_category
    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_generate_custom_music(
    lyric: Annotated[str, Field(description="Song lyrics with section markers like [Verse], [Chorus], etc.")] = "",
    title: Annotated[str, Field(description="Title of the song.")] = "",
    style: Annotated[str, Field(description="Music style description. Examples: 'upbeat pop rock, energetic drums'")] = "",
    model: Annotated[SunoModel, Field(description="Suno model version.")] = DEFAULT_MODEL,
    instrumental: Annotated[bool, Field(description="If true, generate instrumental version.")] = False,
    lyric_prompt: Annotated[dict[str, Any] | None, Field(description="Prompt for auto-generating lyrics.")] = None,
    style_negative: Annotated[str, Field(description="Styles to exclude.")] = "",
    vocal_gender: Annotated[VocalGender, Field(description="Preferred vocal gender. 'f' for female, 'm' for male.")] = "",
    variation_category: Annotated[VariationCategory | None, Field(description="Variation intensity for v5+ models.")] = None,
    weirdness: Annotated[float | None, Field(description="Controls how unusual/experimental the generation is.")] = None,
    style_influence: Annotated[float | None, Field(description="Controls how strongly the style influences the generation.")] = None,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Generate AI music with full control over lyrics, title, and style (Custom Mode).

    Gives you complete creative control over the song. Provide lyrics with section markers.

    Returns:
        Task ID and generated audio information.
    """
    payload: dict[str, Any] = {
        "action": "generate",
        "custom": True,
        "lyric": lyric,
        "title": title,
        "model": model,
        "instrumental": instrumental,
        "callback_url": callback_url,
    }
    if lyric_prompt is not None:
        payload["lyric_prompt"] = lyric_prompt
    if style:
        payload["style"] = style
    if style_negative:
        payload["style_negative"] = style_negative
    if vocal_gender in ("f", "m"):
        payload["vocal_gender"] = vocal_gender
    if variation_category:
        payload["variation_category"] = variation_category
    if weirdness is not None:
        payload["weirdness"] = weirdness
    if style_influence is not None:
        payload["style_influence"] = style_influence
    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_extend_music(
    audio_id: Annotated[str, Field(description="ID of the audio to extend.")],
    lyric: Annotated[str, Field(description="Lyrics for the extended section.")],
    continue_at: Annotated[float, Field(description="Timestamp in seconds where to start the extension.")],
    style: Annotated[str, Field(description="Music style for the extension.")] = "",
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Extend an existing song from a specific timestamp with new lyrics.

    Allows you to continue a previously generated song, adding new sections.

    Returns:
        Task ID and the extended audio information.
    """
    payload = {
        "action": "extend",
        "audio_id": audio_id,
        "lyric": lyric,
        "continue_at": continue_at,
        "custom": True,
        "model": model,
        "callback_url": callback_url,
    }
    if style:
        payload["style"] = style
    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_cover_music(
    audio_id: Annotated[str, Field(description="ID of the audio to create a cover of.")],
    prompt: Annotated[str, Field(description="Description of how you want the cover to sound.")] = "",
    style: Annotated[str, Field(description="Target music style for the cover.")] = "",
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    audio_weight: Annotated[float | None, Field(description="Controls how much the original audio influences the cover.")] = None,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Create a cover or remix version of an existing song in a different style.

    Returns:
        Task ID and the cover audio information.
    """
    payload: dict = {"action": "cover", "audio_id": audio_id, "model": model, "callback_url": callback_url}
    if prompt:
        payload["prompt"] = prompt
    if style:
        payload["style"] = style
    if audio_weight is not None:
        payload["audio_weight"] = audio_weight
    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_concat_music(
    audio_id: Annotated[str, Field(description="ID of the LAST segment of an extended song chain.")],
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Concatenate extended song segments into a single complete audio file.

    Returns:
        Task ID and the concatenated audio information.
    """
    result = await client.generate_audio(action="concat", audio_id=audio_id, callback_url=callback_url)
    return format_audio_result(result)


@mcp.tool()
async def suno_generate_with_persona(
    audio_id: Annotated[str, Field(description="ID of a reference audio.")],
    persona_id: Annotated[str, Field(description="ID of the persona to use.")],
    prompt: Annotated[str, Field(description="Description of the music to generate.")],
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Generate music using a saved artist persona for consistent vocal style.

    Returns:
        Task ID and generated audio information with the persona's voice applied.
    """
    result = await client.generate_audio(action="artist_consistency", audio_id=audio_id, persona_id=persona_id, prompt=prompt, model=model, callback_url=callback_url)
    return format_audio_result(result)


@mcp.tool()
async def suno_remaster_music(
    audio_id: Annotated[str, Field(description="ID of the audio to remaster.")],
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Remaster an existing song to improve audio quality.

    Returns:
        Task ID and the remastered audio information.
    """
    result = await client.generate_audio(action="remaster", audio_id=audio_id, model=model, callback_url=callback_url)
    return format_audio_result(result)


@mcp.tool()
async def suno_stems_music(
    audio_id: Annotated[str, Field(description="ID of the audio to separate into stems.")],
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Separate a song into individual stems (vocals and instruments).

    Returns:
        Task ID and stem separation results.
    """
    result = await client.generate_audio(action="stems", audio_id=audio_id, callback_url=callback_url)
    return format_audio_result(result)


@mcp.tool()
async def suno_replace_section(
    audio_id: Annotated[str, Field(description="ID of the audio to replace a section in.")],
    replace_section_start: Annotated[float, Field(description="Start time in seconds of the section to replace.")],
    replace_section_end: Annotated[float, Field(description="End time in seconds of the section to replace.")],
    lyric: Annotated[str | None, Field(description="New lyrics for the replaced section.")] = None,
    style: Annotated[str, Field(description="Music style for the replaced section.")] = "",
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Replace a specific time range in a song with new generated content.

    Returns:
        Task ID and the updated audio information.
    """
    payload: dict = {
        "action": "replace_section", "audio_id": audio_id,
        "replace_section_start": replace_section_start, "replace_section_end": replace_section_end,
        "model": model, "callback_url": callback_url,
    }
    if lyric:
        payload["lyric"] = lyric
        payload["custom"] = True
    if style:
        payload["style"] = style
    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_upload_extend(
    audio_id: Annotated[str, Field(description="ID of the uploaded audio to extend.")],
    lyric: Annotated[str, Field(description="Lyrics for the extension section.")],
    continue_at: Annotated[float, Field(description="Timestamp in seconds where to start the extension.")],
    style: Annotated[str, Field(description="Music style for the extension.")] = "",
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Extend an uploaded audio with new AI-generated content.

    Returns:
        Task ID and the extended audio information.
    """
    payload: dict = {"action": "upload_extend", "audio_id": audio_id, "lyric": lyric, "continue_at": continue_at, "custom": True, "model": model, "callback_url": callback_url}
    if style:
        payload["style"] = style
    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_upload_cover(
    audio_id: Annotated[str, Field(description="ID of the uploaded audio to create a cover of.")],
    style: Annotated[str, Field(description="Target music style for the cover.")] = "",
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    audio_weight: Annotated[float | None, Field(description="Controls how much the original influences the cover.")] = None,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Create an AI cover of an uploaded audio.

    Returns:
        Task ID and the cover audio information.
    """
    payload: dict = {"action": "upload_cover", "audio_id": audio_id, "model": model, "callback_url": callback_url}
    if style:
        payload["style"] = style
    if audio_weight is not None:
        payload["audio_weight"] = audio_weight
    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_mashup_music(
    mashup_audio_ids: Annotated[list[str], Field(description="List of audio IDs to mashup together.")],
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Create a musical mashup by blending multiple songs together.

    Returns:
        Task ID and the mashup audio information.
    """
    result = await client.generate_audio(action="mashup", mashup_audio_ids=mashup_audio_ids, model=model, callback_url=callback_url)
    return format_audio_result(result)


@mcp.tool()
async def suno_all_stems_music(
    audio_id: Annotated[str, Field(description="ID of the audio to separate into all individual stems.")],
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Separate a song into all individual stems (vocals, bass, drums, other instruments).

    Returns:
        Task ID and all stem separation results with individual track URLs.
    """
    result = await client.generate_audio(action="all_stems", audio_id=audio_id, callback_url=callback_url)
    return format_audio_result(result)


@mcp.tool()
async def suno_generate_with_persona_vox(
    audio_id: Annotated[str, Field(description="ID of a reference audio.")],
    persona_id: Annotated[str, Field(description="ID of the persona to use for VOX generation.")],
    prompt: Annotated[str, Field(description="Description of the music to generate.")],
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Generate music using a saved artist persona with VOX-specific consistency.

    Returns:
        Task ID and generated audio information.
    """
    result = await client.generate_audio(action="artist_consistency_vox", audio_id=audio_id, persona_id=persona_id, prompt=prompt, model=model, callback_url=callback_url)
    return format_audio_result(result)


@mcp.tool()
async def suno_underpainting(
    audio_id: Annotated[str, Field(description="ID of the uploaded audio to add accompaniment to.")],
    underpainting_start: Annotated[float, Field(description="Start time for adding accompaniment.")] = 0.0,
    underpainting_end: Annotated[float | None, Field(description="End time for adding accompaniment.")] = None,
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Add AI-generated accompaniment/instrumental background to uploaded audio.

    Returns:
        Task ID and the audio with accompaniment added.
    """
    payload: dict = {"action": "underpainting", "audio_id": audio_id, "underpainting_start": underpainting_start, "model": model, "callback_url": callback_url}
    if underpainting_end is not None:
        payload["underpainting_end"] = underpainting_end
    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_overpainting(
    audio_id: Annotated[str, Field(description="ID of the uploaded audio to add vocals to.")],
    overpainting_start: Annotated[float, Field(description="Start time for adding vocals.")] = 0.0,
    overpainting_end: Annotated[float | None, Field(description="End time for adding vocals.")] = None,
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Add AI-generated vocals to uploaded instrumental audio.

    Returns:
        Task ID and the audio with vocals added.
    """
    payload: dict = {"action": "overpainting", "audio_id": audio_id, "overpainting_start": overpainting_start, "model": model, "callback_url": callback_url}
    if overpainting_end is not None:
        payload["overpainting_end"] = overpainting_end
    result = await client.generate_audio(**payload)
    return format_audio_result(result)


@mcp.tool()
async def suno_samples_music(
    audio_id: Annotated[str, Field(description="ID of the uploaded audio to add samples to.")],
    samples_start: Annotated[float, Field(description="Start time for adding samples.")] = 0.0,
    samples_end: Annotated[float | None, Field(description="End time for adding samples.")] = None,
    model: Annotated[SunoModel, Field(description="Model version to use.")] = DEFAULT_MODEL,
    callback_url: Annotated[str | None, Field(description="Webhook callback URL.")] = None,
) -> str:
    """Add AI-generated samples to uploaded audio.

    Returns:
        Task ID and the audio with samples added.
    """
    payload: dict = {"action": "samples", "audio_id": audio_id, "samples_start": samples_start, "model": model, "callback_url": callback_url}
    if samples_end is not None:
        payload["samples_end"] = samples_end
    result = await client.generate_audio(**payload)
    return format_audio_result(result)
