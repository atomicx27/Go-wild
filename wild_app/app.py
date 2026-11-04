import streamlit as st
from langchain_ollama import ChatOllama
from duckduckgo_search import DDGS
from langchain_core.messages import SystemMessage, HumanMessage

st.set_page_config(page_title="Autonomous Web Researcher", page_icon="🕵️", layout="wide")

st.title("🕵️ Autonomous Web Researcher")
st.markdown("Enter a topic, and I will search the web using DuckDuckGo, analyze the results with **qwen2.5:1.5b**, and generate a comprehensive report!")

topic = st.text_input("What would you like me to research?", placeholder="e.g., 'Quantum Computing advancements 2024'")

if st.button("Start Research"):
    if topic:
        with st.status("Initializing research process...") as status:
            try:
                # Initialize ChatOllama
                status.update(label="Loading AI model (qwen2.5:1.5b)...")
                llm = ChatOllama(model="qwen2.5:1.5b", temperature=0.2)

                # Search using DuckDuckGo
                status.update(label=f"Searching DuckDuckGo for: '{topic}'...")
                ddgs = DDGS()
                results = list(ddgs.text(topic, max_results=5))

                if not results:
                    st.error("No search results found. Please try a different topic.")
                    st.stop()

                # Format search results
                status.update(label="Formatting search context...")
                context_parts = []
                for idx, result in enumerate(results, 1):
                    context_parts.append(f"Result {idx}:\nTitle: {result.get('title', 'No Title')}\nSnippet: {result.get('body', 'No snippet')}\nURL: {result.get('href', 'No URL')}\n")

                context_str = "\n".join(context_parts)

                # Generate Report
                status.update(label="Synthesizing final report...")
                system_prompt = (
                    "You are an expert autonomous research assistant. "
                    "I will provide you with a user's research topic and several web search results. "
                    "Your task is to analyze these search results and synthesize a well-structured, comprehensive, and objective research report. "
                    "Use headings, bullet points, and clear language. If the search results contradict each other, mention the different perspectives. "
                    "Always base your report strictly on the provided search context."
                )

                human_prompt = (
                    f"Research Topic: {topic}\n\n"
                    f"Search Results Context:\n{context_str}\n\n"
                    "Please generate the comprehensive research report now."
                )

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt)
                ]

                response = llm.invoke(messages)

                status.update(label="Research complete!", state="complete")

                st.success("Report Generated Successfully!")
                st.markdown("---")
                st.markdown(response.content)

            except Exception as e:
                status.update(label="An error occurred during research.", state="error")
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a research topic before starting.")
