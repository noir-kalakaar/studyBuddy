import wikipedia  # `pip install wikipedia`


async def import_wiki_article(query: str):
    """
    Fetch Wikipedia article metadata only.
    We intentionally do NOT embed or store the content to avoid extra Mistral calls.
    """
    page = wikipedia.page(query, auto_suggest=True)
    return {
        "title": page.title,
        "url": page.url,
    }

