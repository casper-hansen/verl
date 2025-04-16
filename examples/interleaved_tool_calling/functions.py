import aiohttp

async def search_bing(query: str, session: aiohttp.ClientSession, num_results: int = 1) -> str:
    import os

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

    try:
        async with session.get(endpoint, headers=headers, params=params) as response:
            # response.raise_for_status()
            print(await response.text())
            data = await response.json()

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
