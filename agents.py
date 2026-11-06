import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url

# Local Ollama model - No API key, 100% free on your PC
model = ChatOllama(
    model="qwen2.5",  # Make sure your ollama background server is running
    temperature=0.7
)

# 1st Agent: Search Agent
def build_search_agent():
    class SearchAgentRunner:
        def invoke(self, inputs):
            query = inputs.get("input", "")
            search_data = web_search.invoke(query) if hasattr(web_search, "invoke") else web_search(query)
            prompt = f"Based on this search data for query '{query}', provide detailed information:\n\n{search_data}"
            res = model.invoke(prompt)
            return {"output": res.content if hasattr(res, 'content') else str(res)}
    return SearchAgentRunner()

# 2nd Agent: Reader Agent
def build_reader_agent():
    class ReaderAgentRunner:
        def invoke(self, inputs):
            text_input = inputs.get("input", "")
            scraped_data = scrape_url.invoke(text_input) if hasattr(scrape_url, "invoke") else scrape_url(text_input)
            prompt = f"Analyze and extract deep content from this scraped data:\n\n{scraped_data}"
            res = model.invoke(prompt)
            return {"output": res.content if hasattr(res, 'content') else str(res)}
    return ReaderAgentRunner()

# Writer Chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional.
""")
])

writer_chain = writer_prompt | model | StrOutputParser()

# Critic Chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""")
])

critic_chain = critic_prompt | model | StrOutputParser()