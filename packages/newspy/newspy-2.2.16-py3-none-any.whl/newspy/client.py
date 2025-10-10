import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from newspy import newsorg, rss
from newspy.models import Article, Category, Channel, Country, Language, Source

default_client_config = {}

channels = {
    Channel.NEWSORG: newsorg,
    Channel.RSS: rss,
}


def configure(newsorg_api_key: str | None = None) -> None:
    global default_client_config

    if newsorg_api_key is None:
        newsorg_api_key = os.getenv("NEWSORG_API_KEY")

    default_client_config = {
        "newsorg_api_key": newsorg_api_key,
    }


def get_sources(
    category: Category | None = None,
    country: Country | None = None,
    language: Language | None = None,
) -> list[Source]:
    sources = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                channels[key].client.get_sources,
                category=category,
                country=country,
                language=language,
            )
            for key in channels
        ]

        for future in as_completed(futures):
            sources.extend([r.to_source() for r in future.result()])

    return sources


def get_articles(
    category: Category | None = None,
    country: Country | None = None,
    language: Language | None = None,
) -> list[Article]:
    articles = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                channels[key].client.get_articles,
                category=category,
                country=country,
                language=language,
            )
            for key in channels
        ]

        for future in as_completed(futures):
            articles.extend([r.to_article() for r in future.result()])

    return articles


def get_categories() -> list[Category]:
    return [c for c in Category]  # type: ignore
