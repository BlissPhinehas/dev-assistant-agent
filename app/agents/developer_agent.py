import logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from app.config import get_settings
from app.tools.github_tool import list_open_issues, create_issue, read_file_from_repo, search_code_in_repo
from app.tools.file_tool import scan_todos, read_local_file

logger = logging.getLogger(__name__)
settings = get_settings()

TOOLS = [
    scan_todos,
    read_local_file,
    list_open_issues,
    create_issue,
    read_file_from_repo,
    search_code_in_repo,
]

SYSTEM_PROMPT = """You are an expert developer assistant agent. You help developers
automate repository tasks using tools at your disposal.

When given a task:
1. Break it into clear steps
2. Use the appropriate tools to execute each step
3. Summarize what you did and the results

Always be concise, accurate, and confirm what actions you took."""


def build_llm():
    if settings.llm_provider == "bedrock":
        try:
            import boto3
            from langchain_aws import ChatBedrock
            client = boto3.client(
                "bedrock-runtime",
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
            )
            return ChatBedrock(client=client, model_id=settings.bedrock_model_id)
        except Exception as e:
            logger.warning(f"Bedrock unavailable: {e}. Falling back to Groq.")

    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model_id,
    )


def run_agent(task: str) -> dict:
    llm = build_llm()
    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT,
    )
    result = agent.invoke({"messages": [{"role": "user", "content": task}]})
    final_message = result["messages"][-1].content
    return {
        "task": task,
        "output": final_message,
    }
