# app/agents/agent_interface.py
"""
Unified agent interface for summarizer, translator, and TTS agents.
"""

from abc import ABC, abstractmethod


class AgentBase(ABC):
    @abstractmethod
    def run(self, text: str, **kwargs):
        pass
