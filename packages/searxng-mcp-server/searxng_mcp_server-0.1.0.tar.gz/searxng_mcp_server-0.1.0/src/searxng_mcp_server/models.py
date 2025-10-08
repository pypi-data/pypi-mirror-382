from datetime import datetime

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Base model for search results."""

    title: str = Field(description="The title of the search result")
    url: str = Field(description="The URL of the search result")
    content: str | None = Field(default=None, description="The content/description of the result")
    engine: str = Field(description="The search engine that provided this result")
    score: float | None = Field(default=None, description="The relevance score")
    published_date: datetime | None = Field(default=None, description="Publication date if available")


class WebSearchResult(SearchResult):
    """Model for web search results."""

    pass


class ImageSearchResult(SearchResult):
    """Model for image search results."""

    thumbnail_url: str | None = Field(default=None, description="URL to thumbnail image")
    image_url: str | None = Field(default=None, description="URL to full-size image")
    width: int | None = Field(default=None, description="Image width")
    height: int | None = Field(default=None, description="Image height")


class VideoSearchResult(SearchResult):
    """Model for video search results."""

    duration: str | None = Field(default=None, description="Video duration")
    channel: str | None = Field(default=None, description="Channel or uploader name")
    view_count: str | None = Field(default=None, description="Number of views")
    thumbnail_url: str | None = Field(default=None, description="URL to video thumbnail")


class NewsSearchResult(SearchResult):
    """Model for news search results."""

    source: str | None = Field(default=None, description="News source/publication")
    author: str | None = Field(default=None, description="Article author")
    published_date: datetime | None = Field(default=None, description="Article publication date")


class WebSearchResponse(BaseModel):
    """Base model for web search responses."""

    query: str = Field(description="The search query that was executed")
    total_results: int = Field(description="Total number of results found")
    results: list[WebSearchResult] = Field(description="List of web search results")
    error: str | None = Field(default=None, description="Error message if search failed")


class ImageSearchResponse(BaseModel):
    """Response model for image searches."""

    query: str = Field(description="The search query that was executed")
    total_results: int = Field(description="Total number of results found")
    results: list[ImageSearchResult] = Field(description="List of image search results")
    error: str | None = Field(default=None, description="Error message if search failed")


class VideoSearchResponse(BaseModel):
    """Response model for video searches."""

    query: str = Field(description="The search query that was executed")
    total_results: int = Field(description="Total number of results found")
    results: list[VideoSearchResult] = Field(description="List of video search results")
    error: str | None = Field(default=None, description="Error message if search failed")


class NewsSearchResponse(BaseModel):
    """Response model for news searches."""

    query: str = Field(description="The search query that was executed")
    total_results: int = Field(description="Total number of results found")
    results: list[NewsSearchResult] = Field(description="List of news search results")
    error: str | None = Field(default=None, description="Error message if search failed")
