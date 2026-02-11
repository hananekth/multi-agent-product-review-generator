import json
from textwrap import dedent
from typing import Dict, Iterator, Optional

from agno.utils.log import logger

# Agent run outputs
from agno.agent import RunOutput

from ai_product_review_generator.response_model import ScrapedContent, SearchResults


class ProductReviewGenerator:
    """Advanced workflow-like runner for generating comprehensive product reviews with research and citations."""

    description: str = dedent("""\
    An intelligent product review generator that creates balanced, well-researched reviews.
    This runner orchestrates multiple AI agents to research, analyze, and craft
    comprehensive product reviews that combine technical accuracy with practical insights.
    The system excels at creating unbiased content that helps consumers make informed decisions.
    """)

    def __init__(self, review_agents, *args, **kwargs):
        self.searcher = review_agents.searcher_agent
        self.content_scraper = review_agents.content_scraper_agent
        self.reviewer = review_agents.reviewer_agent

    def get_search_results(self, product_name: str, num_attempts: int = 3) -> Optional[SearchResults]:
        for attempt in range(num_attempts):
            try:
                search_query = f"{product_name} review specifications features pros cons"
                searcher_response: RunOutput = self.searcher.run(search_query)

                if (
                    searcher_response is not None
                    and searcher_response.content is not None
                    and isinstance(searcher_response.content, SearchResults)
                ):
                    source_count = len(searcher_response.content.product_sources)
                    logger.info(f"Found {source_count} sources on attempt {attempt + 1}")
                    return searcher_response.content

                logger.warning(f"Attempt {attempt + 1}/{num_attempts} failed: Invalid response type")

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{num_attempts} failed: {str(e)}")

        logger.error(f"Failed to get search results after {num_attempts} attempts")
        return None

    def scrape_content(self, product_name: str, search_results: SearchResults) -> Dict[str, ScrapedContent]:
        scraped_content: Dict[str, ScrapedContent] = {}

        for source in search_results.product_sources:
            if source.url in scraped_content:
                logger.info(f"Found scraped content in cache: {source.url}")
                continue

            try:
                content_scraper_response: RunOutput = self.content_scraper.run(source.url)

                if (
                    content_scraper_response is not None
                    and content_scraper_response.content is not None
                    and isinstance(content_scraper_response.content, ScrapedContent)
                ):
                    scraped_content[content_scraper_response.content.url] = content_scraper_response.content
                    logger.info(f"Scraped content: {content_scraper_response.content.url}")

            except Exception as e:
                logger.warning(f"Failed to scrape {source.url}: {str(e)}")

        return scraped_content

    def run(self, product_name: str) -> Iterator[str]:
        """Run the product review generation and stream TEXT chunks (strings) for Gradio."""
        logger.info(f"Generating a product review for: {product_name}")

        # Search
        search_results: Optional[SearchResults] = self.get_search_results(product_name)
        if search_results is None or len(search_results.product_sources) == 0:
            yield f"Sorry, could not find any information about the product: {product_name}"
            return

        # Scrape
        scraped_content: Dict[str, ScrapedContent] = self.scrape_content(product_name, search_results)

        # Prepare reviewer input
        reviewer_input = {
            "product_name": product_name,
            "sources": [v.model_dump() for v in scraped_content.values()],
        }

        # Reviewer: stream events, but yield only text content to the UI
        for event in self.reviewer.run(json.dumps(reviewer_input, indent=4), stream=True):
            content = getattr(event, "content", None)
            if content:
                yield content

