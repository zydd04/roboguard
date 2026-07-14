"""ROBOGUARD: AI AGENT SCANS A CODE FILE FOR VULNERABILITIES."""

from smolagents import CodeAgent, LiteLLMModel, tool
import os


model = LiteLLMModel(
    model_id="ollama_chat/qwen2:7b",
    api_base="http://127.0.0.1:11434",
    num_ctx=8192,
)

@tool
def read_file(filepath: str, max_chars: int = 36000) -> str:
    """
    Reads the content of the file up to a max number of chars.
    Args:
        filepath: the path of the file.
        max_chars: the maximum of the number of chars of file.
    """
    with open(filepath, "r", errors="ignore") as f:
        content = f.read(max_chars)
    return content
agent = CodeAgent(tools=[read_file], model=model)