import arxiv

def search_arxiv(query: str, max_results: int = 10) -> list[arxiv.Result]:
    """Search for papers on arXiv."""
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending,
    )
    return list(search.results())
