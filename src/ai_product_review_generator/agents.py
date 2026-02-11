from textwrap import dedent

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

from ai_product_review_generator.model import Model
from ai_product_review_generator.response_model import ScrapedContent, SearchResults


class ReviewAgents:
    """Agents for product review generation workflow"""

    def __init__(self, llm: Model):
        """Initialize the agents for product review generation workflow"""
        self.llm = llm.get()
        self.searcher_agent = self._create_searcher_agent()
        self.content_scraper_agent = self._create_content_scraper_agent()
        self.reviewer_agent = self._create_reviewer_agent()

    def _create_searcher_agent(self) -> Agent:
        """Create the search agent for finding relevant product information"""
        return Agent(
            model=self.llm,
            tools=[DuckDuckGoTools()],
            description=dedent("""\
                You are ProductResearch-X, an elite research assistant specializing in discovering
                comprehensive information about products. Find official specs, user reviews, expert opinions,
                pricing info, and common issues about products.
            """),
            instructions=dedent("""\
                Search Strategy:
                - Find 5-7 relevant sources about the product
                - Include official product pages, review sites, user forums, and tech blogs
                - Look for both professional reviews and user experiences
                - Search for product reviews, specifications, and user experience
                - Prioritize verified purchase reviews and recent information

                Output Requirements:
                - You MUST return structured output that matches the SearchResults schema.
                - Each source must include: title, url, and summary (brief).
                - Do not return plain text; return only the structured object.
            """),
            # ✅ NEW: structured result parsing
            output_schema=SearchResults,
            structured_outputs=True,
        )

    def _create_content_scraper_agent(self) -> Agent:
        """Create the content scraper agent for extracting information from sources"""
        return Agent(
            model=self.llm,
            tools=[Newspaper4kTools()],
            description=dedent("""\
                You are ContentExtract-X, a specialist in extracting and processing product
                information from various sources. Extract content efficiently, identify key specs,
                preserve ratings and quotes, and maintain attribution.
            """),
            instructions=dedent("""\
                Content Extraction:
                - Extract product information, specifications, and reviews from the given URL
                - Preserve important ratings, pros, and cons
                - Maintain proper attribution
                - Format text in clean markdown
                - Structure specifications clearly
                - Ensure accurate extraction and readability

                Output Requirements:
                - You MUST return structured output that matches the ScrapedContent schema.
                - Do not return plain text; return only the structured object.
            """),
            # ✅ NEW: structured result parsing
            output_schema=ScrapedContent,
            structured_outputs=True,
        )

    def _create_reviewer_agent(self) -> Agent:
        """Create the review writer agent for generating product reviews"""
        return Agent(
            model=self.llm,
            description=dedent("""\
                You are ReviewMaster-X, an expert product reviewer combining technical knowledge
                with consumer advocacy. Write balanced reviews, explain technical specs clearly,
                synthesize multiple sources, and provide clear recommendations.
            """),
            instructions=dedent("""\
                Review Structure (800-1200 words):
                - Start with a compelling introduction
                - Include sections: Overview, Key Features, Performance, Pros & Cons, Value, Verdict
                - Use descriptive subheadings
                - Present both positive and negative aspects fairly
                - Support claims with evidence from sources
                - Explain technical specifications in accessible language
                - Relate features to real-world benefits
                - Provide clear verdict on who should buy this product
                - Discuss value proposition and mention alternatives when appropriate
                - Cite all sources with URLs at the end
                - Maintain factual accuracy and attribute opinions to sources
            """),
            expected_output=dedent("""\
                # Product Review: Engaging Title

                ## Introduction
                Hook and context about the product

                ## Overview
                Product category, manufacturer, key positioning

                ## Key Features & Specifications
                Main features and technical specs explained clearly

                ## Performance & User Experience
                Real-world performance analysis and what users/experts say

                ## Pros
                - Strength 1
                - Strength 2
                - Strength 3

                ## Cons
                - Weakness 1
                - Weakness 2
                - Weakness 3

                ## Value for Money
                Price analysis and value assessment

                ## Verdict
                Final recommendation and who should buy

                ## Sources
                List all source URLs used
            """),
            markdown=True,
        )

