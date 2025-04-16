def search_ddg(query: str, num_results: int = 1) -> str:
    from duckduckgo_search import DDGS

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=min(num_results, 10)))
            if not results:
                return "No results found"

            summaries = [f"# {r['title']}\n\n {r['body']}" for r in results]
            return "\n\n".join(summaries)
    except Exception as e:
        return f"Error: {str(e)}" 

def search_bing(query: str, num_results: int = 1) -> str:
    import os
    import requests

    try:
        bing_api_key = os.getenv("BING_API_KEY")
        if not bing_api_key:
            return "Error: BING_API_KEY environment variable is not set"

        endpoint = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            "Ocp-Apim-Subscription-Key": bing_api_key,
            "Accept": "application/json",
            "Accept-Language": "en-US"
        }
        params = {
            "q": query,
            "count": num_results
        }

        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()

        # webPages might not be present if no results are found
        web_pages = data.get("webPages", {}).get("value", [])
        if not web_pages:
            return "No results found"

        summaries = [
            f"# {item.get('name', 'No Title')}\n\n{item.get('snippet', 'No Description')}"
            for item in web_pages
        ]

        return "\n\n".join(summaries)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    print(search_bing("veRL"))