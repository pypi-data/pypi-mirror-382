from typing import List, Optional, Dict, Any, Literal
from haystack import (
    component,
    Document,
    default_to_dict,
    default_from_dict,
    logging,
    ComponentError,
)
from haystack.utils import Secret, deserialize_secrets_inplace
from valyu import Valyu

logger = logging.getLogger(__name__)

SearchType = Literal["web", "proprietary", "all"]


@component
class ValyuSearch:
    """
    A component for searching using the Valyu Search API (DeepSearch).

    The Valyu Search API returns results with content already included,
    making it suitable for direct use in RAG pipelines.

    Usage example:
    ```python
    from valyu_haystack import ValyuSearch

    searcher = ValyuSearch(top_k=5)
    results = searcher.run(query="What is Haystack?")
    documents = results["documents"]
    ```
    """

    def __init__(
        self,
        api_key: Secret = Secret.from_env_var("VALYU_API_KEY"),
        top_k: int = 10,
        search_type: SearchType = "all",
        relevance_threshold: float = 0.5,
        max_price: int = 100,
    ):
        """
        Initialize the ValyuSearch component.

        :param api_key: API key for Valyu Search API. Defaults to VALYU_API_KEY environment variable.
        :param top_k: Maximum number of results to return
        :param search_type: Type of search - "web", "proprietary", or "all"
        :param relevance_threshold: Minimum relevance score to return results (0.0-1.0)
        :param max_price: Maximum price per thousand queries in cents
        """
        self.api_key = api_key
        self.top_k = top_k
        self.search_type = search_type
        self.relevance_threshold = relevance_threshold
        self.max_price = max_price

        # Initialize Valyu client
        self.valyu_client = Valyu(api_key=self.api_key.resolve_value())

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns: Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            api_key=self.api_key.to_dict(),
            top_k=self.top_k,
            search_type=self.search_type,
            relevance_threshold=self.relevance_threshold,
            max_price=self.max_price,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValyuSearch":
        """
        Deserializes the component from a dictionary.

        :returns: Deserialized component.
        """
        deserialize_secrets_inplace(data["init_parameters"], keys=["api_key"])
        return default_from_dict(cls, data)

    def _call_api(self, query: str) -> List[Document]:
        """
        Calls the Valyu DeepSearch API using the Valyu SDK.
        """
        # Use the Valyu SDK's search method with input validation
        response = self.valyu_client.search(
            query=query,
            search_type=self.search_type,
            max_num_results=self.top_k,
            is_tool_call=True,
            relevance_threshold=self.relevance_threshold,
            max_price=self.max_price,
        )

        # Check if the request was successful
        if not response.success:
            error_msg = response.error or "Unknown error"
            raise ComponentError(f"Valyu API returned error: {error_msg}")

        # Parse the SearchResponse format
        documents = []
        for result in response.results:
            # Handle both string and structured content
            content = result.content
            if isinstance(content, list):
                # If content is structured (list of dicts), convert to string
                content = "\n".join(
                    [
                        f"{item.get('key', '')}: {item.get('value', '')}"
                        for item in content
                        if isinstance(item, dict)
                    ]
                )

            doc = Document(
                content=str(content),
                meta={
                    "title": result.title,
                    "url": result.url,
                    "description": result.description or "",
                    "source": result.source,
                    "relevance_score": result.relevance_score,
                    "price": result.price,
                    "length": result.length,
                    "data_type": result.data_type,
                    "image_url": result.image_url,
                },
            )
            documents.append(doc)

        logger.debug(
            "ValyuSearch returned {number_documents} documents for the query '{query}'",
            number_documents=len(documents),
            query=query,
        )

        return documents

    @component.output_types(documents=List[Document], links=List[str])
    def run(self, query: str) -> Dict[str, Any]:
        """
        Search for information on the web and proprietary sources using the Valyu Search API.

        :param query: The search query string
        :returns: A dictionary with the following keys:
            - "documents": List of documents returned by the search.
            - "links": List of URLs returned by the search.
        """
        if not query or not query.strip():
            logger.warning("Received empty query, returning no results")
            return {"documents": [], "links": []}

        documents = self._call_api(query)

        # Extract links from documents
        links = [doc.meta.get("url", "") for doc in documents if doc.meta.get("url")]

        return {"documents": documents[: self.top_k], "links": links[: self.top_k]}
