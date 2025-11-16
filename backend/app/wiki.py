import wikipedia  # `pip install wikipedia`

from .rag import store_text


async def import_wiki_article(query: str):
    page = wikipedia.page(query, auto_suggest=True)
    await store_text(title=page.title, text=page.content, source="wikipedia")
    return {
        "title": page.title,
        "url": page.url,
    }

