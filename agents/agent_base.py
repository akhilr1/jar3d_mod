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

    # def register(self, state: StateT):
    #     """
    #     Register the agent in the AgentRegistry using its initialized name.
    #     Stores the agent's docstring in the AgentRegistry.
    #     """
    #     # Extract the docstring from the child class
    #     agent_docstring = self.__class__.__doc__
    #     if agent_docstring:
    #         agent_description = agent_docstring.strip()
    #     else:
    #         agent_description = "No description provided."

    #     # Store the agent's description in the AgentRegistry
    #     if self.name != "meta_agent":
    #         AgentRegistry[self.name] = agent_description
    #         print(f"Agent '{self.name}' registered in AgentRegistry.")

    #     state[self.name] = []

        

    # def write_to_state(self, state: StateT, response: Any):
    #     """
    #     Write the agent's response to the state under its registered name.

    #     :param state: The state dictionary to write to.
    #     :param response: The response to be written to the state.
    #     """
    #     response_document = Document(page_content=response, metadata={"agent": self.name})
    #     print("hii\n\n", response_document)
    #     # Ensure state[self.name] is always a list
    #     if self.name not in state or not isinstance(state[self.name], list):
    #         state[self.name] = []

    #     state[self.name].append(response_document)
    #     print(f"Agent '{self.name}' wrote to state.")

    # def read_instructions(self, state: StateT) -> str:
    #     """
    #     Read instructions from the 'meta_agent' in the state.

    #     :param state: The current state of the agent.
    #     :return: Instructions as a string.
    #     """
    #     try:
    #         meta_agent_response = state.get("meta_agent", [])[-1].page_content
    #         meta_agent_response_json = json.loads(meta_agent_response)
            
    #         print(f"\n response Agent '{meta_agent_response_json}'\n")#--------------------------------------#2 change                                                           
            
    #         instructions = meta_agent_response_json.get("step_4", {}).get("final_draft", "")
    #         # print(colored(f"\n\n{self.name} read instructions from meta_agent: {instructions}\n\n", 'green'))
    #     except Exception as e:
    #         print(f"You must have a meta_agent in your workflow: {e}")
    #         return ""
    #     return instructions

    # @abstractmethod
    # def invoke(self, state: StateT) -> Dict[str, Any]:
    #     """
    #     Abstract method to invoke the agent's main functionality.

    #     :param state: The current state of the agent.
    #     :return: A dictionary of outputs.
    #     """
    #     pass


class SimpleAgent(BaseAgent[StateT]):
    def invoke(self, state: StateT) -> Dict[str, Any]:
        # Implement the required method, even if it's just a pass or a simple implementation
        return {}