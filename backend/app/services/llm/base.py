"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface that all LLM providers must implement."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Active model name."""
        ...

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            system_prompt: System instructions.
            messages: List of {"role": "user"|"assistant", "content": "..."} dicts.
            temperature: Sampling temperature.
            max_tokens: Maximum response tokens.

        Returns:
            The generated text response.
        """
        ...

    async def generate_image(self, prompt: str) -> str | None:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Description of the image to generate.
            
        Returns:
            URL of the generated image, or None if unsupported or failed.
        """
        return None
