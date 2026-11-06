# import time
# from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# def safe_invoke(agent_or_chain, inputs):
#     """Groq API limits / Rate limit errors se bachne ke liye automatic retry mechanism"""
#     max_retries = 8
#     for attempt in range(max_retries):
#         try:
#             return agent_or_chain.invoke(inputs)
#         except Exception as e:
#             err_msg = str(e)
#             # Rate limit (429), server errors, ya connection issues ko catch karta hai
#             if any(code in err_msg for code in ["503", "502", "429", "UNAVAILABLE", "rate_limit"]):
#                 wait_time = (attempt + 1) * 3  # Har retry par wait time badhega
#                 print(f"⚠️ Groq API rate limited/busy. Retrying in {wait_time}s... ({attempt+1}/{max_retries})")
#                 time.sleep(wait_time)
#             else:
#                 raise e
#     raise Exception("Groq API servers are heavily congested right now. Please try again later.")


# def run_research_pipeline(topic: str) -> dict:
#     state = {}

#     # ----------------------------------------------------
#     # Step 1: Search Agent Working
#     # ----------------------------------------------------
#     print("\n" + "="*50)
#     print("step1 -> search_Agent_is_working..")
#     print("="*50)

#     search_agent = build_search_agent()
#     search_result = safe_invoke(search_agent, {
#         "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
#     })

#     # Output extract karna (LangChain message list se)
#     state["search_results"] = search_result['messages'][-1].content
#     print("\n[Search Agent Result]:\n", state['search_results'])

#     # ----------------------------------------------------
#     # Step 2: Reader Agent Scraping
#     # ----------------------------------------------------
#     print("\n" + "="*50)
#     print("step2 -> reader_Agent_is_scraping_top_researchs..")
#     print("="*50)

#     reader_agent = build_reader_agent()
#     reader_result = safe_invoke(reader_agent, {
#         "messages": [("user", 
#             f"Based on the following search results about '{topic}', "
#             f"pick the most relevant URL and scrape it for deeper content.\n\n"
#             f"Search Results:\n{state['search_results'][:800]}"
#         )]
#     })

#     state["scraped_content"] = reader_result['messages'][-1].content
#     print("\n[Scraped Content]:\n", state['scraped_content'])

#     # ----------------------------------------------------
#     # Step 3: Writer Drafting the Report
#     # ----------------------------------------------------
#     print("\n" + "="*50)
#     print("step3 -> writer_is_drafting_the_report..")
#     print("="*50)

#     research_combined = (
#         f"SEARCH RESULTS:\n{state['search_results']}\n\n"
#         f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}\n\n"
#     )

#     writer_res = safe_invoke(writer_chain, {
#         "topic": topic,
#         "research": research_combined
#     })

#     # Chain response extract karna
#     report = writer_res.content if hasattr(writer_res, 'content') else str(writer_res)
#     state["report"] = report

#     print("\n[Final Report]:\n", report)

#     # ----------------------------------------------------
#     # Step 4: Critic Analyzing the Report
#     # ----------------------------------------------------
#     print("\n" + "="*50)
#     print("step4 -> critic_is_analysing_the_report..")
#     print("="*50)

#     critic_res = safe_invoke(critic_chain, {
#         "report": report
#     })

#     critic_report = critic_res.content if hasattr(critic_res, 'content') else str(critic_res)
#     state["critic_report"] = critic_report

#     print("\n[Critic Report]:\n", critic_report)

#     return state


# if __name__ == "__main__":
#     user_topic = input("\nEnter a research topic : ")
#     run_research_pipeline(user_topic)


import time
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

def safe_invoke(agent_or_chain, inputs):
    """Local execution safe wrapper"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return agent_or_chain.invoke(inputs)
        except Exception as e:
            err_msg = str(e)
            print(f"⚠️ Error encountered: {err_msg}. Retrying... ({attempt+1}/{max_retries})")
            time.sleep(2)
    raise Exception("Execution failed locally.")


def run_research_pipeline(topic: str) -> dict:
    state = {}

    # ----------------------------------------------------
    # Step 1: Search Agent Working
    # ----------------------------------------------------
    print("\n" + "="*50)
    print("step1 -> search_Agent_is_working..")
    print("="*50)

    search_agent = build_search_agent()
    search_result = safe_invoke(search_agent, {
        "input": f"Find recent, reliable and detailed information about: {topic}"
    })

    state["search_results"] = search_result['output']
    print("\n[Search Agent Result]:\n", state['search_results'])

    # ----------------------------------------------------
    # Step 2: Reader Agent Scraping
    # ----------------------------------------------------
    print("\n" + "="*50)
    print("step2 -> reader_Agent_is_scraping_top_researchs..")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = safe_invoke(reader_agent, {
        "input": state['search_results'][:800]
    })

    state["scraped_content"] = reader_result['output']
    print("\n[Scraped Content]:\n", state['scraped_content'])

    # ----------------------------------------------------
    # Step 3: Writer Drafting the Report
    # ----------------------------------------------------
    print("\n" + "="*50)
    print("step3 -> writer_is_drafting_the_report..")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}\n\n"
    )

    writer_res = safe_invoke(writer_chain, {
        "topic": topic,
        "research": research_combined
    })

    report = writer_res.content if hasattr(writer_res, 'content') else str(writer_res)
    state["report"] = report

    print("\n[Final Report]:\n", report)

    # ----------------------------------------------------
    # Step 4: Critic Analyzing the Report
    # ----------------------------------------------------
    print("\n" + "="*50)
    print("step4 -> critic_is_analysing_the_report..")
    print("="*50)

    critic_res = safe_invoke(critic_chain, {
        "report": report
    })

    critic_report = critic_res.content if hasattr(critic_res, 'content') else str(critic_res)
    state["critic_report"] = critic_report

    print("\n[Critic Report]:\n", critic_report)

    return state


if __name__ == "__main__":
    user_topic = input("\nEnter a research topic : ")
    run_research_pipeline(user_topic)