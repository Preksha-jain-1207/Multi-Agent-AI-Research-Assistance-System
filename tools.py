from langchain.tools import tool
import requests  # idhar mai online web ka use karugi or online web ki scraping krni hi hai to request import kr lia
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from rich import print

from dotenv import load_dotenv
load_dotenv()

# creating our very first tool
# tavily ka # tavily client ko load karege

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

import time
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns titles, URLs and snippets"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # max_results ko 3 ya 4 rakhein
            results = tavily.search(query=query, max_results=3)
            
            out = []
            for r in results['results']:
                out.append(
                    f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
                )
            
            return "\n".join(out)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Tavily timeout/error. Retrying ({attempt+1}/{max_retries})...")
                time.sleep(2)
            else:
                return f"Search failed after {max_retries} attempts: {str(e)}"




# for creating a tool mai ek function banaugi jo bascially custom hoga
# @tool
# def web_search(query: str) -> str:
#     """Search the web for recent and reliable information on a topic. Returns titles, URLs and snippets"""
#     results =  tavily.search(query=query, max_results=4)
#     out = []
#     for r in results['results']:
#         out.append(
#             f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:200]}\n"
#         )

#     return "\n-----\n".join(out)




@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"


# ye doc string will tell the AI model (llm) what work it will do and what data to extract
# ye max_results = 4 isiliye likha hai kyuki hadd barbaad nahi krna chahte hai api tokens ko isiliye limit kr dia
# ye jo tavily.search se result milege wo kahi na kahi to store krne padege to result naam k variable me store kr dege
# sirf result k content ko memory me rakhna hai    
