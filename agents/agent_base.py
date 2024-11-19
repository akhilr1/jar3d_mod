import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar
from langsmith import traceable
from datetime import datetime
from termcolor import colored
from langchain_core.documents.base import Document
# from .agent_registry import AgentRegistry
import sys
from models.llms import OpenAIModel


StateT = TypeVar('StateT', bound=Dict[str, Any])

class BaseAgent(ABC, Generic[StateT]):
    """
    Abstract base class for all agents in the system.
    Provides common functionality and interface for agent implementations.
    """
    def __init__(
        self,
        name: str,
        model: str = None,
        server: str = None,
        temperature: float = 0,
        model_endpoint: str = None,
        stop: str = None
    ):
        """
        Initialize the BaseAgent with common parameters.

        :param name: The name to register the agent
        :param model: The name of the language model to use
        :param server: The server hosting the language model
        :param temperature: Controls randomness in model outputs
        :param model_endpoint: Specific endpoint for the model API
        :param stop: Stop sequence for model generation
        """
        self.name = name  # Store the initialized name
        self.model = model
        self.server = server
        self.server = "openai"                                          #change: "openai
        self.temperature = temperature
        self.model_endpoint = model_endpoint
        self.stop = stop
        self.llm = self.get_llm()
        # self.register()

    def get_llm(self, json_response: bool = False, prompt_caching: bool = True):
        """
        Factory method to create and return the appropriate language model instance.
        :param json_response: Whether the model should return JSON responses
        :param prompt_caching: Whether to use prompt caching
        :return: An instance of the appropriate language model
        """
        if self.server == "openai":
            return OpenAIModel(
                temperature=self.temperature,
                model=self.model,
                json_response=json_response
            )

        else:
            raise ValueError(f"Unsupported server type: {self.server}")


class SimpleAgent(BaseAgent[StateT]):
    def invoke(self, state: StateT) -> Dict[str, Any]:
        # Implement the required method, even if it's just a pass or a simple implementation
        return {}