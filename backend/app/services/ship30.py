"""
Ship 30 for 30 essay writing skill.

A dedicated module for generating ~1,250-word essays in the Ship 30 for 30 format
using retrieved transcript knowledge.

Design:
- Detects essay requests via keyword patterns
- Uses a specialized system prompt enforcing Ship 30 structure
- Requires RAG context (will not generate without grounding)
- Returns Markdown artifact

Inputs:
- User query/topic
- Retrieved transcript chunks (RAG context)

Outputs:
- Markdown essay (~1,250 words)
- Source citations

Ship 30 format:
1. Strong opening hook (1-2 punchy sentences)
2. Clear thesis/promise
3. 3-5 sections with descriptive headings
4. Bullet points and **bold** for key concepts
5. Practical takeaway section
6. Source attributions
"""

import re

from app.services.llm.base import LLMProvider
from app.services.rag import build_context
from app.utils.logging import get_logger

logger = get_logger("ship30")

# Keywords that trigger essay generation
ESSAY_TRIGGERS = [
    r"\bessay\b",
    r"\bship\s*30\b",
    r"\batomic\s+essay\b",
    r"\bwrite\s+(an?\s+)?(long|detailed|in-depth|comprehensive)\s+(piece|article|post)\b",
    r"\bwrite\s+(me\s+)?(an?\s+)?(essay|article|piece|post|blog)\b",
    r"\bgenerate\s+(an?\s+)?(essay|article|piece|post)\b",
    r"\b(deep\s*dive|long[- ]form)\b",
]


def is_essay_request(query: str) -> bool:
    """Detect if the user is requesting an essay/article."""
    query_lower = query.lower()
    return any(re.search(pattern, query_lower) for pattern in ESSAY_TRIGGERS)


SHIP30_SYSTEM_PROMPT = """You are an expert product-management writer creating a Ship 30 for 30-style essay.

Your task is to write a compelling ~1,250-word essay using ONLY the provided transcript knowledge.

## Format Requirements

1. **Opening Hook**: Start with 1-2 punchy sentences that create curiosity or challenge a common assumption. No generic introductions.

2. **Thesis**: After the hook, state clearly what the reader will learn and why it matters.

3. **Body Sections (3-5)**: Each section should have:
   - A descriptive, specific heading (not generic like "Section 1")
   - A mix of narrative prose, bullet points, and **bold emphasis** on key concepts
   - Direct quotes or paraphrased insights from the transcripts, attributed to the speaker
   - Concrete examples, numbers, or frameworks where available

4. **Practical Takeaway**: End with a clearly labeled "## Takeaway" or "## What This Means for You" section containing specific, actionable advice.

5. **Sources**: End with a "## Sources" section listing the episodes/articles referenced.

## Rules

- Write approximately 1,250 words (between 1,000 and 1,500).
- ONLY use information from the provided transcript context.
- If the transcripts don't contain enough relevant material, say so explicitly — do NOT make up content.
- Use Markdown formatting throughout.
- Attribute insights to speakers by name (e.g., "As Adam Mosseri explains...").
- Be specific and concrete. Avoid vague generalizations.
- Write for a product manager or tech leader audience.
- Maintain an authoritative but conversational tone — like Lenny's Newsletter.
"""


async def generate_essay(
    query: str,
    chunks: list[dict],
    provider: LLMProvider,
) -> dict:
    """
    Generate a Ship 30 for 30-style essay grounded in transcript knowledge.

    Returns:
        dict with keys: content, artifact, sources
    """
    context = build_context(chunks)

    if not context:
        return {
            "content": (
                "I don't have enough transcript material to write a grounded essay on this topic. "
                "The available Lenny's Podcast transcripts and newsletters don't cover this subject "
                "in sufficient detail. Try a topic that's covered in the dataset, such as product "
                "management, growth strategy, AI in product development, or team leadership."
            ),
            "artifact": None,
            "sources": [],
        }

    user_message = f"""Write a Ship 30 for 30-style essay on this topic: {query}

Use the following transcript knowledge as your source material:

{context}

Remember: Write ~1,250 words, use Markdown, attribute insights to speakers, and include practical takeaways."""

    logger.info("generating_essay", topic=query[:80], context_chunks=len(chunks))

    essay_content = await provider.generate(
        system_prompt=SHIP30_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        temperature=0.7,
        max_tokens=4096,
    )

    return {
        "content": "I've generated a Ship 30 for 30-style essay for you. Check the artifact viewer to read it.",
        "artifact": {
            "type": "markdown",
            "content": essay_content,
            "title": f"Essay: {query[:60]}",
        },
    }
