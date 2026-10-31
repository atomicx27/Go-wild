import streamlit as st
import json
import requests
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import re
import ast
import operator

st.set_page_config(page_title="Researcher Agent", page_icon="🕵️", layout="wide")

st.title("🕵️ Intelligent Researcher Agent")
st.markdown("Powered by **Ollama** (`qwen2.5:0.5b`) + **LangGraph** + **DuckDuckGo**.")

@tool
def web_search(query: str) -> str:
    """Search the web for real-time information."""
    try:
        results = DDGS().text(query, max_results=3)
        formatted = []
        for r in results:
            formatted.append(f"Title: {r.get('title')}\nURL: {r.get('href')}\nSummary: {r.get('body')}")
        if not formatted:
            return "No results found."
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Web search failed: {str(e)}"

@tool
def extract_website_content(url: str) -> str:
    """Extract readable text from a URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(separator=' ', strip=True)
        # return first 2000 chars to avoid context overflow for small model
        return text[:2000] + ("..." if len(text) > 2000 else "")
    except Exception as e:
        return f"Failed to extract content: {str(e)}"


# Safe mathematical evaluator
def eval_expr(expr):
    """
    Evaluate a mathematical string safely.
    Raises ValueError for unsafe operations (e.g. huge exponents).
    """
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg
    }

    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                right = _eval(node.right)
                left = _eval(node.left)
                # prevent huge calculations that might lock the thread
                if abs(left) > 1000 or abs(right) > 100:
                    raise ValueError("Exponentiation arguments are too large.")
                return ops[type(node.op)](left, right)
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        else:
            raise TypeError("Unsupported mathematical operation")

    try:
        tree = ast.parse(expr, mode='eval').body
        return _eval(tree)
    except Exception as e:
        raise ValueError(f"Invalid math expression: {e}")

@tool
def calculator(expression: str) -> str:
    """Evaluate simple mathematical expressions (e.g. '2 + 2 * 3')."""
    try:
        result = eval_expr(expression)
        return str(result)
    except Exception as e:
        return f"Calculation error: {str(e)}"

tools = [web_search, extract_website_content, calculator]
llm = ChatOllama(model="qwen2.5:0.5b", temperature=0.2)
agent_executor = create_react_agent(llm, tools)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask the agent to research something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        try:
            with st.spinner("Agent is working... (this may involve searching or calculation)"):

                # Convert session state messages to LangChain format
                lc_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        lc_messages.append(("user", msg["content"]))
                    elif msg["role"] == "assistant":
                        lc_messages.append(("assistant", msg["content"]))

                response = agent_executor.invoke(
                    {"messages": lc_messages},
                    config={"configurable": {"thread_id": "1"}}
                )

                final_content = response["messages"][-1].content
                message_placeholder.markdown(final_content)
                st.session_state.messages.append({"role": "assistant", "content": final_content})

                # Show tool calls debug info in an expander
                with st.expander("Agent Thought Process (Tool Calls)"):
                    for msg in response["messages"]:
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tool_call in msg.tool_calls:
                                st.write(f"🔧 **Used Tool:** `{tool_call['name']}`")
                                st.json(tool_call['args'])
                        elif msg.type == "tool":
                            st.write(f"📥 **Tool Result:**")
                            st.text(msg.content[:500] + ("..." if len(msg.content) > 500 else ""))
                            st.divider()

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            message_placeholder.markdown(f"**Error:** {error_msg}")
            import traceback
            st.error(traceback.format_exc())
