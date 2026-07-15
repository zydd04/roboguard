"""ROBOGUARD: AI AGENT SCANS A CODE FILE FOR VULNERABILITIES."""

from smolagents import CodeAgent, LiteLLMModel, tool 
import subprocess
import json
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

def run_agent(file: str, max_chars: int = 36000) -> str:
    """
    Runs agent for scanning file returns scan results.
    """
    prompt = (
        f"Scan the file at '{file}' for security vulnerabilities.\n"
        "You are required to follow these steps:\n"
        "1. Use read_file to read the file.\n"
        "2. Run scan_bandit on the Python file.\n"
        "3.  Return ONLY a JSON array where each "
        "object has exactly these fields: file, line, severity "
        "(low/medium/high/critical), issue, recommendation."
        "Execute your tools, gather the findings, and then "
        "immediately provide your final answer. Do not create new steps "
        "once you have the scanner output."
    )
    report = agent.run(prompt)
    return report

if __name__ == "__main__":
    file = input("Enter the name of the file to be scanned after putting it in the dir:")
    if not os.path.exists(file):
        print(f"File Not Found.")
    else:
        output = run_agent(file)
        print("////////// --- SCAN RESULTS : --- /////////")
        if output:
            print(json.dumps(output, indent=2))
            print(f"\nResults Found: {len(output)}")
        else:
            print("No Results Found.")