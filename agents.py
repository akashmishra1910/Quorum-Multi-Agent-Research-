from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_webpage

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured.")


# --------------------------------------------------
# MODELS
# --------------------------------------------------

fast_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=1500,
    api_key=GROQ_API_KEY,
)

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    reasoning_effort="low",
    api_key=GROQ_API_KEY,
)


# --------------------------------------------------
# SEARCH AGENT
# --------------------------------------------------

def build_search_agent():
    return create_agent(
        model=fast_llm,
        tools=[web_search],
        system_prompt="""
You are a research search agent.

Find recent and reliable information about the user's topic.

Return only:
- The 3 most relevant sources
- Title
- URL
- A short 1-2 sentence summary

Do not write a long report.
Do not repeat information.
"""
    )


# --------------------------------------------------
# READER AGENT
# --------------------------------------------------

def build_reader_agent():
    return create_agent(
        model=fast_llm,
        tools=[scrape_webpage],
        system_prompt="""
You are a web-reading agent.

Your task:
1. Examine the provided search results.
2. Select ONE most relevant URL.
3. Call scrape_webpage exactly ONCE.
4. Extract the most useful factual information.
5. Return a concise summary.

Do not perform another web search.
Do not call scrape_webpage more than once.
Do not reproduce the entire webpage.
"""
    )


# --------------------------------------------------
# WRITER
# --------------------------------------------------

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research writer.

Write clear, structured and factual reports.
Use only the research provided to you.
Do not invent facts, statistics or URLs.
"""
    ),
    (
        "human",
        """
Write a detailed research report on:

Topic:
{topic}

Research Gathered:
{research}

Structure:

## Introduction

## Key Findings
Include at least 3 well-explained findings.

## Conclusion

## Sources
List the URLs found in the research.

Be detailed, factual and professional.
"""
    )
])

writer_chain = writer_prompt | llm | StrOutputParser()


# --------------------------------------------------
# CRITIC
# --------------------------------------------------

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a sharp and constructive research critic.

Evaluate factual grounding, clarity, structure,
completeness and source usage.

Be specific and concise.
"""
    ),
    (
        "human",
        """
Review this research report:

{report}

Respond exactly in this format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...
"""
    )
])

critic_chain = critic_prompt | fast_llm | StrOutputParser()