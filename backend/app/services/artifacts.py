"""
Artifact generation service.

Handles creation of Markdown and HTML/CSS artifacts from LLM output.

Design decisions:
- Artifacts are stored as JSONB in the messages table: {type, content, title}
- Markdown artifacts are the default output for essays and documents
- HTML/CSS artifacts are used when the user explicitly requests styled output
- Security: HTML artifacts are rendered in sandboxed iframes on the frontend
"""

import re

from app.services.llm.base import LLMProvider
from app.services.rag import build_context
from app.utils.logging import get_logger

logger = get_logger("artifacts")

# Keywords that trigger artifact/document generation (not essays)
ARTIFACT_TRIGGERS = [
    r"\b(create|generate|make|build)\s+(a\s+)?(document|doc|report|summary|guide|cheatsheet|cheat\s*sheet)\b",
    r"\b(html|styled|formatted)\s+(document|page|output|report|artifact)\b",
    r"\bcreate\s+(an?\s+)?artifact\b",
]


def is_artifact_request(query: str) -> bool:
    """Detect if the user wants a standalone document/artifact."""
    query_lower = query.lower()
    return any(re.search(pattern, query_lower) for pattern in ARTIFACT_TRIGGERS)


def is_html_request(query: str) -> bool:
    """Detect if the user specifically wants HTML output."""
    query_lower = query.lower()
    return bool(re.search(r"\b(html|styled|css|formatted|visual)\b", query_lower))


ARTIFACT_SYSTEM_PROMPT = """You are a technical writer creating a well-structured document based on Lenny's Podcast and Newsletter content.

Create a document using the provided transcript knowledge. The document should:

1. Have a clear title
2. Use proper Markdown formatting (headings, bullets, bold, code blocks as needed)
3. Be well-organized with logical sections
4. Include specific insights and quotes from the transcripts
5. Attribute insights to their speakers
6. Be practical and actionable

ONLY use information from the provided context. Do not invent content."""

HTML_ARTIFACT_PROMPT = """You are a technical writer creating a beautifully styled HTML document based on Lenny's Podcast and Newsletter content.

Create a complete, self-contained HTML document with embedded CSS. The document should:

1. Be a complete HTML5 document with <html>, <head>, <body> tags
2. Include embedded <style> CSS for professional typography and layout
3. Use a clean, modern design (think: readable blog post or newsletter)
4. Have proper headings, paragraphs, and lists
5. Include specific insights and quotes from the transcripts
6. Attribute insights to their speakers
7. Use a color scheme that's easy to read (dark text on light background)

ONLY use information from the provided context. Do not invent content.
Do NOT include any JavaScript. The document should be pure HTML + CSS."""


async def generate_artifact(
    query: str,
    chunks: list[dict],
    provider: LLMProvider,
) -> dict:
    """
    Generate a document artifact (Markdown or HTML) grounded in transcript knowledge.
    """
    context = build_context(chunks)

    if not context:
        return {
            "content": (
                "I don't have enough transcript material to create this document. "
                "The available transcripts don't cover this topic in sufficient detail."
            ),
            "artifact": None,
            "sources": [],
        }

    use_html = is_html_request(query)
    system_prompt = HTML_ARTIFACT_PROMPT if use_html else ARTIFACT_SYSTEM_PROMPT

    user_message = f"""Create a document on this topic: {query}

Use the following transcript knowledge:

{context}"""

    logger.info(
        "generating_artifact",
        topic=query[:80],
        format="html" if use_html else "markdown",
    )

    content = await provider.generate(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": user_message}],
        temperature=0.5,
        max_tokens=4096,
    )

    artifact_type = "html" if use_html else "markdown"

    return {
        "content": f"I've created a {'styled HTML' if use_html else 'Markdown'} document for you. Check the artifact viewer to read it.",
        "artifact": {
            "type": artifact_type,
            "content": content,
            "title": f"Document: {query[:60]}",
        },
    }
