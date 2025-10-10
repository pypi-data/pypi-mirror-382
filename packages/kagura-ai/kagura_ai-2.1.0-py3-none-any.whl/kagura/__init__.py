"""
Kagura AI 2.0 - Python-First AI Agent Framework

Example:
    from kagura import agent

    @agent
    async def hello(name: str) -> str:
        '''Say hello to {{ name }}'''
        pass

    result = await hello("World")
"""
from .core.decorators import agent, tool, workflow
from .version import __version__

__all__ = ["agent", "tool", "workflow", "__version__"]
