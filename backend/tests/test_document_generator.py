"""Tests for the document_generator service."""

import pytest

from app.services.document_generator import (
    _extract_title,
    check_and_generate_clarification,
    generate_document,
    has_prior_clarification,
    is_document_request,
)


# is_document_request

class TestIsDocumentRequest:
    """Tests for document-request detection."""

    @pytest.mark.parametrize(
        "query",
        [
            "Create a growth strategy document",
            "Generate a document on product-led growth",
            "Build a go-to-market plan for my SaaS product",
            "Draft a retention document",
            "Create a detailed document about user onboarding",
            "create a document",
            "generate a document on retention strategies",
            "Make a competitive analysis document",
            "growth strategy document",
        ],
    )
    def test_positive_detection(self, query: str):
        assert is_document_request(query) is True

    @pytest.mark.parametrize(
        "query",
        [
            "What is product-led growth?",
            "Tell me about retention",
            "How did Duolingo grow?",
            "Write me an essay on growth",
            "Who are Lenny's best guests?",
            "Hello",
        ],
    )
    def test_negative_detection(self, query: str):
        assert is_document_request(query) is False


# check_and_generate_clarification

class TestCheckAndGenerateClarification:
    @pytest.mark.asyncio
    async def test_needs_clarification(self):
        class MockProvider:
            async def generate(self, **kwargs):
                return '{"needs_clarification": true, "questions": ["Who is the audience?", "What is the goal?"]}'

        result, msg = await check_and_generate_clarification("Create a document", MockProvider())
        assert result is True
        assert "Who is the audience?" in msg

    @pytest.mark.asyncio
    async def test_no_clarification_needed(self):
        class MockProvider:
            async def generate(self, **kwargs):
                return '{"needs_clarification": false, "questions": []}'

        result, msg = await check_and_generate_clarification(
            "Create a document for PMs about retention, just generate it", MockProvider()
        )
        assert result is False
        assert msg == ""


# has_prior_clarification

class TestHasPriorClarification:
    def test_detects_prior_clarification(self):
        history = [
            {"role": "user", "content": "Create a document"},
            {"role": "assistant", "content": "Before I create this document, a few questions..."},
        ]
        assert has_prior_clarification(history) is True

    def test_no_clarification_in_history(self):
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        assert has_prior_clarification(history) is False

    def test_empty_history(self):
        assert has_prior_clarification([]) is False





# _extract_title

class TestExtractTitle:
    def test_extracts_markdown_heading(self):
        content = "# Growth Strategy for SaaS\n\nSome content here..."
        assert _extract_title(content, "fallback") == "Growth Strategy for SaaS"

    def test_extracts_html_h1(self):
        content = "<html><body><h1>Product-Led Growth Report</h1></body></html>"
        assert _extract_title(content, "fallback") == "Product-Led Growth Report"

    def test_fallback_on_no_heading(self):
        content = "Just some text without any headings"
        title = _extract_title(content, "my query")
        assert "my query" in title

    def test_nested_html_tags_stripped(self):
        content = "<h1><span>Styled Title</span></h1>"
        assert _extract_title(content, "fallback") == "Styled Title"


# generate_document (with mocked provider)

class TestGenerateDocument:
    @pytest.mark.asyncio
    async def test_empty_context_returns_no_artifact(self):
        """When no RAG chunks are available, should return error message."""

        class MockProvider:
            async def generate(self, **kwargs):
                return "mock content"

        result = await generate_document(
            query="Create a document",
            chunks=[],
            provider=MockProvider(),
        )
        assert result["artifact"] is None
        assert "don't have enough" in result["content"]

    @pytest.mark.asyncio
    async def test_markdown_generation(self):
        """With chunks, should return a Markdown artifact."""

        class MockProvider:
            async def generate(self, **kwargs):
                return "# Test Document\n\nSome content here."

        # Simulate chunks with required fields
        chunks = [
            {
                "chunk_content": "Growth is about retention...",
                "title": "Episode 1",
                "guest": "Test Guest",
                "source_type": "podcast",
                "speaker": "Lenny",
                "source_id": "abc-123",
            }
        ]

        result = await generate_document(
            query="Create a growth strategy document",
            chunks=chunks,
            provider=MockProvider(),
            use_html=False,
        )
        assert result["artifact"] is not None
        assert result["artifact"]["type"] == "markdown"
        assert result["artifact"]["title"] == "Test Document"

    @pytest.mark.asyncio
    async def test_html_generation(self):
        """With HTML flag, should return an HTML artifact."""

        class MockProvider:
            async def generate(self, **kwargs):
                return "<html><body><h1>HTML Doc</h1><p>Content</p></body></html>"

        chunks = [
            {
                "chunk_content": "Insights about growth...",
                "title": "Episode 2",
                "guest": "Guest 2",
                "source_type": "podcast",
                "speaker": "Lenny",
                "source_id": "def-456",
            }
        ]

        result = await generate_document(
            query="Create a styled HTML document",
            chunks=chunks,
            provider=MockProvider(),
            use_html=True,
        )
        assert result["artifact"] is not None
        assert result["artifact"]["type"] == "html"
        assert result["artifact"]["title"] == "HTML Doc"

    @pytest.mark.asyncio
    async def test_conversation_history_used(self):
        """Should incorporate prior user answers into the document prompt."""

        class CapturingProvider:
            last_messages = None

            async def generate(self, **kwargs):
                self.last_messages = kwargs.get("messages", [])
                return "# Doc\n\nContent"

        provider = CapturingProvider()
        chunks = [
            {
                "chunk_content": "Some knowledge...",
                "title": "Ep",
                "guest": "G",
                "source_type": "podcast",
                "speaker": "S",
                "source_id": "x",
            }
        ]

        history = [
            {"role": "user", "content": "Create a document"},
            {"role": "assistant", "content": "Before I create, a few questions..."},
            {"role": "user", "content": "For product managers, about retention"},
        ]

        await generate_document(
            query="Create a document",
            chunks=chunks,
            provider=provider,
            conversation_history=history,
        )

        # The prompt sent to the LLM should include the user's answers
        assert provider.last_messages is not None
        user_msg = provider.last_messages[0]["content"]
        assert "additional details" in user_msg.lower()
