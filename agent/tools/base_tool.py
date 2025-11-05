# agent/tools/base_tool.py
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """An abstract base class for all tools."""

    def __init__(self, llm_client=None):
        """Initializes the tool, optionally with a reference to the LLM client."""
        self.llm_client = llm_client

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool (e.g., 'open_notepad')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the tool does."""
        pass

    @abstractmethod
    def execute(self, argument: str) -> str:
        """The method that runs the tool's logic."""
        pass