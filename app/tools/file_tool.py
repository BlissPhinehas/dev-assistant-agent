import os
import re
from langchain_core.tools import tool


EXCLUDED_DIRS = {".git", "venv", "__pycache__", ".env", "node_modules"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"}
_COMMENT_MARKER = re.compile(r"#.*\bTODO\b|//.*\bTODO\b|/\*.*\bTODO\b", re.IGNORECASE)


@tool
def scan_todos(directory: str = ".") -> str:
    """Scan a directory recursively for TODO comments in code files.
    Returns a list of TODOs with their file path and line number."""
    todos = []

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for filename in files:
            ext = os.path.splitext(filename)[1]
            if ext not in CODE_EXTENSIONS:
                continue
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, start=1):
                        if _COMMENT_MARKER.search(line):
                            clean = line.strip()
                            todos.append(f"{filepath}:{line_num} -> {clean}")
            except OSError:
                continue

    if not todos:
        return "No TODO comments found."
    return "\n".join(todos)


@tool
def read_local_file(file_path: str) -> str:
    """Read the contents of a local file and return it as a string."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError as e:
        return f"Error reading file: {e}"
