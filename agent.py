"""ROBOGUARD: AI AGENT SCANS A CODE FILE FOR VULNERABILITIES."""

from smolagents import CodeAgent, LiteLLMModel, tool 
import subprocess
import json

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

@tool
def scan_bandit(path: str) -> str:
    """
    Use Python's bandit to scan for security issues inside the file.
    return the dscan results
    Args:
        path: File to be scanned.
    """
    try:
        scan_result = subprocess.run(["bandit", "-f", "json", path], capture_output=True, text=True)
        if scan_result.stdout:
            parsed_json = json.loads(scan_result.stdout)
            return json.dumps(parsed_json, indent=2)
        if scan_result.stderr:
            return f"bandit ran into an error while scanning: {scan_result.stderr}"
        return "No vulnerabilities or issues found."
    except FileNotFoundError:
        return "bandit not found. use `pip install bandit`."
    except Exception as e:
        return f"bandit ran into an error while scanning: {str(e)}"
agent = CodeAgent(tools=[read_file,scan_bandit], model=model)