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
