from github import Github, GithubException
from langchain_core.tools import tool
from app.config import get_settings

settings = get_settings()
_client = Github(settings.github_token)
_repo = _client.get_repo(settings.github_repo)


@tool
def list_open_issues(limit: int = 10) -> str:
    """List open issues in the GitHub repository."""
    try:
        issues = _repo.get_issues(state="open")
        results = []
        for i, issue in enumerate(issues):
            if i >= limit:
                break
            results.append(f"#{issue.number}: {issue.title}")
        return "\n".join(results) if results else "No open issues found."
    except GithubException as e:
        return f"GitHub error: {e.status} - {e.data}"


@tool
def create_issue(title: str, body: str, label: str = "todo") -> str:
    """Create a new GitHub issue with a title, body, and optional label."""
    try:
        existing_labels = [l.name for l in _repo.get_labels()]
        label_objs = []
        if label in existing_labels:
            label_objs.append(_repo.get_label(label))
        issue = _repo.create_issue(title=title, body=body, labels=label_objs)
        return f"Created issue #{issue.number}: {issue.title} -> {issue.html_url}"
    except GithubException as e:
        return f"GitHub error: {e.status} - {e.data}"


@tool
def read_file_from_repo(file_path: str) -> str:
    """Read the contents of a file from the GitHub repository."""
    try:
        content = _repo.get_contents(file_path)
        return content.decoded_content.decode("utf-8")
    except GithubException as e:
        return f"GitHub error: {e.status} - {e.data}"


@tool
def search_code_in_repo(query: str) -> str:
    """Search for a keyword or pattern across files in the repository."""
    try:
        results = _client.search_code(f"{query} repo:{settings.github_repo}")
        matches = []
        for item in results:
            matches.append(f"{item.path} -> {item.html_url}")
        return "\n".join(matches) if matches else "No matches found."
    except GithubException as e:
        return f"GitHub error: {e.status} - {e.data}"
