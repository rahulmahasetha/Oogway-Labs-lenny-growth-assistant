"""
Document generation service — structured document creation with clarification flow.

Handles detection of document-creation requests, asks clarifying follow-up
questions when key details are missing, and generates structured Markdown or
HTML/CSS documents grounded in Lenny transcript knowledge.

Design decisions:
- Detects document requests via regex patterns (broader than artifact triggers)
- Analyzes query for missing details and asks 1-3 follow-up questions
- Supports skipping clarification ("just generate it")
- Generates structured documents with title, executive summary, sections, takeaways
- HTML documents include a styled gradient cover section (no external image API)
- Reuses existing JSONB artifact schema: {type, content, title}
"""

import re

from app.services.llm.base import LLMProvider
from app.services.rag import build_context
from app.utils.logging import get_logger

logger = get_logger("document_generator")

# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

DOCUMENT_TRIGGERS = [
    r"\b(create|generate|make|build|draft|write)\s+(a\s+)?(growth\s+strategy|strategy|marketing|product|onboarding|retention|go[\s-]to[\s-]market|gtm|competitive|market\s+analysis)\s+(document|doc|report|plan|playbook|brief|framework)\b",
    r"\b(create|generate|make|build|draft)\s+(a\s+)?(document|doc|report|plan|playbook|brief|framework)\s+(on|about|for|regarding)\b",
    r"\b(create|generate|make|build|draft)\s+(me\s+)?(a\s+)?(detailed|comprehensive|structured|professional|formal)\s+(document|doc|report|plan|playbook|brief)\b",
    r"\b(document|doc)\s+(on|about|for|regarding)\b.*\b(create|generate|make|build|draft)\b",
    r"\bcreate\s+(a\s+)?document\b",
    r"\bgenerate\s+(a\s+)?document\b",
    r"\bgrowth\s+strategy\s+document\b",
    r"\b(draft|make|build)\s+(a\s+)?\w+\s+(strategy|analysis)\s+(document|doc|report|plan|brief)\b",
    r"\b(draft|make|build)\s+(a\s+)?\w+\s+(document|doc|report|plan|brief)\b",
]


def is_document_request(query: str) -> bool:
    """Detect if the user wants a structured document created."""
    q = query.lower()
    return any(re.search(p, q) for p in DOCUMENT_TRIGGERS)


# ---------------------------------------------------------------------------
# Clarification
# ---------------------------------------------------------------------------

SKIP_PATTERNS = [
    r"\bjust\s+generate\b",
    r"\bskip\s+(the\s+)?questions?\b",
    r"\bgo\s+ahead\b",
    r"\bjust\s+(do|create|make|build)\s+it\b",
    r"\bdon'?t\s+(need|want)\s+(to\s+)?(ask|clarif)\b",
]

async def check_and_generate_clarification(
    query: str, chunks: list[dict], provider: LLMProvider
) -> str | None:
    """
    Check if the user's document generation query is too vague.
    If it is, use the LLM to generate 2-3 dynamic clarification questions.
    Returns the clarification message, or None if the query is clear enough.
    """
    q = query.lower()
    if any(re.search(p, q) for p in SKIP_PATTERNS):
        return None

    # Ask the LLM if the query is vague and generate questions if so
    system_prompt = """You are an expert product management advisor. 
The user wants to generate a structured document based on Lenny's Podcast/Newsletter.
Evaluate the user's request:
- If the request has a specific topic, target audience, or clear scope, reply exactly with: "CLEAR"
- If the request is too vague (e.g., "Create a document", "Write a growth strategy"), generate 2-3 highly specific, bulleted clarification questions to understand their exact needs (e.g., B2B vs B2C, specific growth levers, target audience).

If you generate questions, just list them. Do not include introductory text."""

    context = build_context(chunks) if chunks else "No specific transcripts found."
    user_prompt = f"User Request: {query}\n\nAvailable Context Snippet:\n{context[:1000]}"

    response = await provider.generate(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0.3,
        max_tokens=200,
    )

    if response.strip().upper() == "CLEAR":
        return None

    # Format the response
    lines = [
        "Great idea! Before I create this document, a few quick questions to make sure it's exactly what you need:\n",
        response.strip(),
        "\n💡 *If you'd rather I just go ahead, reply \"just generate it\" and I'll create the document with sensible defaults.*"
    ]
    return "\n".join(lines)


def has_prior_clarification(conversation_history: list[dict]) -> bool:
    """Check if clarification was already asked in conversation history."""
    for msg in conversation_history:
        if msg.get("role") == "assistant":
            content = msg.get("content", "").lower()
            if "before i create" in content or "help me create" in content or "a few questions" in content:
                return True
    return False


# ---------------------------------------------------------------------------
# Document generation
# ---------------------------------------------------------------------------

DOCUMENT_SYSTEM_PROMPT = """You are a senior product strategist creating a professional, structured document based on Lenny's Podcast and Newsletter content.

## Document Structure

Create a well-organized document with the following structure:

1. **Title**: A clear, descriptive title for the document
2. **Executive Summary**: A 2-3 sentence overview of what this document covers and why it matters
3. **Table of Contents**: A brief list of the main sections
4. **Main Sections (3-6)**: Each section should have:
   - A descriptive heading
   - Key insights with attribution to speakers from Lenny's Podcast
   - Data points, frameworks, or mental models where available
   - Bullet points for actionable items
5. **Key Takeaways**: 3-5 bullet points summarizing the most important insights
6. **Recommended Actions**: Specific, prioritized next steps
7. **Sources**: Episodes and articles referenced

## Rules

- ONLY use information from the provided transcript context
- Attribute insights to their speakers (e.g., "According to Keith Rabois...")
- Be specific and data-driven where possible
- Use professional, clear language suitable for executive-level readers
- Use Markdown formatting: headings (#, ##, ###), bold (**), bullet points, numbered lists
- Aim for 1,500-2,500 words — comprehensive but focused
- If context is insufficient, say so explicitly — do NOT fabricate content
- Do NOT use any placeholders, brackets, or incomplete sections (e.g., "[Insert data here]"). Write the full, complete text.
- Deduplicate all sources in your citations section; list each source only once.
"""

HTML_DOCUMENT_PROMPT = """You are a senior product strategist creating a beautifully designed HTML document based on Lenny's Podcast and Newsletter content.

Create a complete, self-contained HTML5 document with embedded CSS. The document MUST include:

1. **Cover Section**: A styled gradient header with:
   - Document title in large, bold text
   - Subtitle describing the scope
   - A "Powered by Lenny's Podcast" attribution line
   - Use a gradient background (e.g., from #4f46e5 to #0ea5e9)

2. **Professional Layout**:
   - Clean, modern typography (system font stack)
   - Proper spacing and margins
   - A max-width container (700-800px) centered on the page
   - Light background with dark text

3. **Content Structure**:
   - Executive Summary
   - Main sections (3-6) with clear headings
   - Key insights attributed to speakers
   - Takeaways section
   - Sources section

4. **Visual Elements**:
   - Styled blockquotes for speaker quotes
   - Highlighted key metrics or numbers
   - Clean tables if comparing items
   - A subtle border-left accent on important callouts

## Rules

- ONLY use information from the provided transcript context
- Return a COMPLETE HTML document with <html>, <head>, <style>, <body>
- Do NOT include any JavaScript
- Aim for 1,500-2,500 words of content
- Use professional, executive-level language
- Do NOT use any placeholders, brackets, or incomplete sections. Write the full, complete text.
- Deduplicate all sources in your citations section; list each source only once.
- ONLY output the raw HTML code. Do NOT wrap it in markdown code blocks (```html). Do NOT include any conversational text before or after the HTML.
"""


async def generate_document(
    query: str,
    chunks: list[dict],
    provider: LLMProvider,
    conversation_history: list[dict] | None = None,
    use_html: bool = False,
) -> dict:
    """
    Generate a structured document artifact grounded in transcript knowledge.

    Returns:
        dict with keys: content, artifact, sources
    """
    context = build_context(chunks)

    if not context:
        return {
            "content": (
                "I don't have enough transcript material to create this document. "
                "The available Lenny's Podcast transcripts and newsletters don't cover "
                "this topic in sufficient detail. Try a topic covered in the dataset, "
                "such as growth strategy, product-led growth, retention, or team leadership."
            ),
            "artifact": None,
            "sources": [],
        }

    system_prompt = HTML_DOCUMENT_PROMPT if use_html else DOCUMENT_SYSTEM_PROMPT

    messages = []
    if conversation_history:
        for msg in conversation_history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    user_message = f"""Create a document on this topic: {query}

Use the following transcript knowledge as your source material:

{context}

Remember: Create a comprehensive, well-structured document with proper sections, speaker attributions, and actionable takeaways."""
    messages.append({"role": "user", "content": user_message})

    # Check if the user requested an image (e.g., "cover image", "AI image")
    image_markdown = ""
    image_html = ""
    if re.search(r"\b(image|picture|cover|art)\b", query.lower()):
        logger.info("generating_cover_image", topic=query[:80])
        image_prompt = f"A professional, minimalist cover image for a product management and growth strategy document about: {query}. High quality, modern vector art style."
        image_url = await provider.generate_image(prompt=image_prompt)
        if image_url:
            image_markdown = f"![Cover Image]({image_url})\n\n"
            image_html = f'<div style="text-align: center; margin-bottom: 2rem;"><img src="{image_url}" alt="Cover Image" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" /></div>\n'

    logger.info(
        "generating_document",
        topic=query[:80],
        format="html" if use_html else "markdown",
        context_chunks=len(chunks),
    )

    content = await provider.generate(
        system_prompt=system_prompt,
        messages=messages,
        temperature=0.5,
        max_tokens=6000,
    )

    # Strip markdown code blocks if the LLM ignored instructions
    if content.strip().startswith("```"):
        content = re.sub(r"^```[a-zA-Z]*\n?", "", content.strip())
        content = re.sub(r"\n?```(.*)?$", "", content, flags=re.DOTALL)
        content = content.strip()

    if image_markdown and not use_html:
        content = image_markdown + content
    elif image_html and use_html:
        # Insert image after the body tag or at the top
        content = re.sub(r'(<body[^>]*>)', r'\1' + image_html, content, count=1, flags=re.IGNORECASE)
        if image_html not in content:
            content = image_html + content

    artifact_type = "html" if use_html else "markdown"
    doc_label = "styled HTML" if use_html else "Markdown"

    # Extract a title from the generated content
    title = _extract_title(content, query)

    return {
        "content": (
            f"📄 I've created a {doc_label} document for you: **{title}**\n\n"
            f"Check the artifact viewer panel on the right to read the full document. "
            f"You can copy, download, or regenerate it from there."
        ),
        "artifact": {
            "type": artifact_type,
            "content": content,
            "title": title,
        },
    }


def _extract_title(content: str, fallback_query: str) -> str:
    """Pull the first heading from the generated content as the title."""
    # Try Markdown heading
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Try HTML <h1>
    match = re.search(r"<h1[^>]*>(.+?)</h1>", content, re.IGNORECASE | re.DOTALL)
    if match:
        # Strip any nested tags
        return re.sub(r"<[^>]+>", "", match.group(1)).strip()
    # Fallback
    return f"Document: {fallback_query[:60]}"
