"""Abstract base class for LLM client adapters."""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger("klira.adapters.llm_base")


class BaseLLMAdapter(ABC):
    """Abstract base class for adapters that patch specific LLM client libraries."""

    # Indicates if the corresponding LLM library is available
    is_available: bool = False

    @abstractmethod
    def patch(self) -> None:
        """Apply patches to the underlying LLM client library for augmentation injection."""
        raise NotImplementedError

    # Optional: A common helper could live here, but injection is often client-specific
    # def _inject_guidelines(self, *args, **kwargs):
    #    pass
