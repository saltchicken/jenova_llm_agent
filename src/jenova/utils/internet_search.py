import requests
from duckduckgo_search import DDGS
import wikipedia
from jenova.utils.crawler import crawl

def get_wikipedia_summary(question):
    try:
        # Search for the topic
        search_results = wikipedia.search(question)
        if not search_results:
            return "No relevant articles found."

        # Get the first result's summary
        page_title = search_results[0]
        # summary = wikipedia.summary(page_title, sentences=2)
        summary = wikipedia.summary(page_title)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Too many possible meanings: {e.options[:5]}..."
    except wikipedia.exceptions.PageError:
        return "Page not found."
    except Exception as e:
        return f"An error occurred: {e}"

def duckduckgo_instant_answer(question):
    url = "https://api.duckduckgo.com/"
    params = {
        "q": question,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1
    }
    response = requests.get(url, params=params)
    data = response.json()

    answer = data.get("AbstractText") or data.get("Answer") or None
    return answer

def duckduckgo_search(question):
    results = DDGS().text(question, max_results=1)
    return [r["href"] for r in results]

async def search_engine_crawler(question):
    links = duckduckgo_search(question)
    print(f"FOUND LINKS: {links}")
    if len(links) == 0:
        return None
    question_information = ''
    for link in links:
        print("calling crawler")
        result = await crawl(link)
        if result is None:
            print("Resut is none. Skipping")
        else:
            question_information += result + "\n"
    return question_information



if __name__ == "__main__":
    question = "Who is the current president of the United States?"

    # result = get_wikipedia_summary(question)
    # result = duckduckgo_instant_answer(question)


    # print(result)
