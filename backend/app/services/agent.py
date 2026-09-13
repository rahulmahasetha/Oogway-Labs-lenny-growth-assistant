"""
Chat agent — orchestrates the full conversational flow.

This is the central router that:
1. Loads session history
2. Detects if the query needs a special skill (document, essay, artifact)
3. Retrieves relevant transcript chunks via RAG
4. Routes to the appropriate handler
5. Returns a grounded response with source citations

Design:
- The agent always retrieves RAG context before responding
- Special skills (Document, Ship 30, artifacts) are detected via keyword matching
- Regular Q&A uses a grounded system prompt that cites sources
- If no relevant transcripts are found, the agent explicitly says so
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.artifacts import generate_artifact, is_artifact_request
from app.services.document_generator import (
    check_and_generate_clarification,
    generate_document,
    has_prior_clarification,
    is_document_request,
)
from app.services.llm.factory import get_llm_provider
from app.services.rag import (
    build_context,
    build_source_citations,
    retrieve_relevant_chunks,
)
from app.services.ship30 import generate_essay, is_essay_request
from app.utils.logging import get_logger

logger = get_logger("agent")

SYSTEM_PROMPT = """You are the Lenny Growth Assistant — an AI expert on product management, growth, and startup strategy, grounded in knowledge from Lenny's Podcast and Lenny's Newsletter.

## Your Knowledge

You have access to transcripts from Lenny's Podcast episodes and newsletter articles. Your answers must be based on this knowledge.

## How to Respond

1. **Answer from the transcripts**: Use the provided context to answer the user's question. Reference specific insights, frameworks, and advice from the sources.

2. **Attribute insights**: When citing advice or quotes, attribute them to the speaker (e.g., "According to Marc Andreessen..." or "As Keith Rabois shared on Lenny's Podcast...").

3. **Be specific and practical**: Give concrete, actionable advice. Avoid vague generalizations.

4. **Cite sources**: At the end of your response, include a brief "**Sources:**" section listing the episodes/articles you drew from.

5. **Acknowledge limitations**: If the provided context doesn't contain relevant information for the question, clearly say: "Based on the available Lenny's Podcast transcripts and newsletters, I don't have specific information on this topic." Do NOT make up content.

6. **Conversation context**: You may reference earlier messages in the conversation to provide continuity, but always ground new claims in the transcript context.

## Tone

- Authoritative but conversational — like Lenny himself
- Direct and practical
- Enthusiastic about product management and growth
"""

NO_CONTEXT_RESPONSE = (
    "Based on the available Lenny's Podcast transcripts and newsletters, "
    "I don't have specific information on this topic. The dataset includes "
    "50 podcast episodes and 10 newsletter articles covering product management, "
    "growth strategy, AI, and team leadership. Try asking about one of these topics, "
    "or about a specific guest like Adam Mosseri, Simon Willison, Marc Andreessen, "
    "or others featured in the podcast."
)


async def generate_response(
    query: str,
    session_messages: list,
    db: AsyncSession,
) -> dict:
    """
    Generate a grounded AI response.

    Returns:
        dict with keys: content, sources (list), artifact (optional)
    """
    provider = get_llm_provider()

    # 1. Retrieve relevant transcript chunks
    chunks = await retrieve_relevant_chunks(query, db)

    # 2. Route to appropriate handler

    # --- Document creation (new) ---
    if is_document_request(query):
        logger.info("routing_to_document", query_preview=query[:80])

        # Build conversation history for clarification check
        conv_history = [
            {"role": m.role, "content": m.content}
            for m in (session_messages or [])
        ]

        # Ask clarification questions if this is the first message
        # and the query is vague
        if not has_prior_clarification(conv_history):
            clarification = await check_and_generate_clarification(query, chunks, provider)
            if clarification:
                logger.info("requesting_clarification", query_preview=query[:80])
                return {
                    "content": clarification,
                    "sources": [],
                    "artifact": None,
                }

        # Detect HTML preference
        query_lower = query.lower()
        use_html = bool(
            __import__("re").search(r"\b(html|styled|css|formatted|visual)\b", query_lower)
        )

        result = await generate_document(
            query=query,
            chunks=chunks,
            provider=provider,
            conversation_history=conv_history,
            use_html=use_html,
        )
        result["sources"] = build_source_citations(chunks) if chunks else []
        return result

    # --- Essay generation ---
    if is_essay_request(query):
        logger.info("routing_to_essay", query_preview=query[:80])
        result = await generate_essay(query, chunks, provider)
        result["sources"] = build_source_citations(chunks) if chunks else []
        return result

    # --- Generic artifact generation ---
    if is_artifact_request(query):
        logger.info("routing_to_artifact", query_preview=query[:80])
        result = await generate_artifact(query, chunks, provider)
        result["sources"] = build_source_citations(chunks) if chunks else []
        return result

    # 3. Regular Q&A with RAG grounding
    context = build_context(chunks)

    if not context:
        logger.info("no_relevant_context", query_preview=query[:80])
        return {
            "content": NO_CONTEXT_RESPONSE,
            "sources": [],
            "artifact": None,
        }

    # Build conversation history for the LLM
    conversation = []
    # Include recent session messages for continuity (last 10 messages)
    recent_messages = session_messages[-10:] if session_messages else []
    for msg in recent_messages:
        conversation.append({
            "role": msg.role,
            "content": msg.content,
        })

    # Add the current query with RAG context
    grounded_query = f"""The user asks: {query}

Here is relevant knowledge from Lenny's Podcast and Newsletter transcripts:

{context}

Answer the user's question using this knowledge. Be specific, cite speakers, and include a Sources section."""

    conversation.append({"role": "user", "content": grounded_query})

    # 4. Generate response
    logger.info(
        "generating_qa_response",
        query_preview=query[:80],
        context_chunks=len(chunks),
        history_messages=len(conversation),
    )

    content = await provider.generate(
        system_prompt=SYSTEM_PROMPT,
        messages=conversation,
        temperature=0.7,
        max_tokens=2048,
    )

    # 5. Build source citations
    sources = build_source_citations(chunks)

    return {
        "content": content,
        "sources": sources,
        "artifact": None,
    }
