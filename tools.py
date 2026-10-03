from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


# --------------------------------
# TOOL 1: WEB SEARCH
# --------------------------------

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic.
    Return titles, URLs and snippets."""

    results = tavily.search(
        query=query,
        max_results=3
    )

    out = []

    for result in results["results"]:
        out.append(
            f"Title: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Snippet: {result['content']}\n"
        )

    return "\n".join(out)


# --------------------------------
# TOOL 2: WEB SCRAPER
# --------------------------------

@tool
def scrape_webpage(url: str) -> str:
    """Scrape a webpage and return its readable text content."""

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove unnecessary elements
        for element in soup(
            ["script", "style", "nav", "footer", "header"]
        ):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return text[:3000]

    except requests.RequestException as e:
        return f"Error fetching webpage: {e}"


# --------------------------------
# TEST TOOLS ONLY WHEN RUN DIRECTLY
# --------------------------------

if __name__ == "__main__":

    print("\n--- WEB SEARCH TEST ---\n")

    print(
        web_search.invoke(
            "What are the latest developments in AI?"
        )
    )

    print("\n--- WEB SCRAPER TEST ---\n")

    print(
        scrape_webpage.invoke(
            "https://www.aljazeera.com/tag/israel-iran-conflict"
        )
    )