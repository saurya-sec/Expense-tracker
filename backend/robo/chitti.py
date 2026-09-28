import os
from robo.tools import tools
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent

load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)



SYSTEM_PROMPT = """
You are a personal finance assistant.

You help users with:
- income
- expenses
- budgeting
- saving
- spending habits
- financial analysis

Be clear, concise, and practical.

Do not invent financial data.
If financial data is required but you don't have access to it,
clearly say that you don't have the required information.
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)



def chat_with_finance_agent(input_message: str) -> str:

    messages = [
        {"role": "user", "content": input_message}
        
    ]

    response = agent.invoke({"messages": messages})

    return response["messages"][-1].content


