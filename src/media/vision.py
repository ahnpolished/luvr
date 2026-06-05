"""Image analysis using vision-capable LLMs.

Uses the configured LLM provider's vision capabilities to analyze images
and generate dating advice based on visual content.
"""

from __future__ import annotations

from src.llm.client import create_llm_client


async def analyze_dating_photo(
    image_data: bytes,
    mime_type: str,
    context: str = "",
) -> str:
    """Analyze a dating-related photo and generate advice.

    This is a convenience wrapper around the LLM client's image analysis.
    Primary use cases:
    - Screenshots of text conversations (analyze tone, suggest responses)
    - Dating app profiles (give feedback on photos/bios)
    - Photos from dates or social situations

    Args:
        image_data: Raw image bytes
        mime_type: Image MIME type (e.g., image/jpeg)
        context: Optional user-provided context/question

    Returns:
        Generated analysis and advice
    """
    llm_client = create_llm_client()
    return await llm_client.analyze_image(
        image_data=image_data,
        mime_type=mime_type,
        context=context,
    )
