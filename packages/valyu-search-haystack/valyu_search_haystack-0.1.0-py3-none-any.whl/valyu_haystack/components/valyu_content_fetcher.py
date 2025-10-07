from typing import List, Optional, Dict, Any, Union, Literal
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

ExtractEffort = Literal["normal", "high", "auto"]
ContentsResponseLength = Union[Literal["short", "medium", "large", "max"], int]


@component
class ValyuContentFetcher:
    """
    A component for extracting clean content from URLs using the Valyu Content API.

    This component is useful when you have URLs (from search results or other sources)
    and want to extract their full content. Since ValyuSearch already returns content,
    this component is optional but can be used for:
    - Fecthing user provided URLs
    - Extracting content with different parameters

    Usage example:
    ```python
    from valyu_haystack import ValyuContentFetcher
    from haystack import Document

    fetcher = ValyuContentFetcher()

    # Option 1: Pass URLs directly
    results = fetcher.run(urls=["https://example.com/article"])
    ```
    """

    def __init__(
        self,
        api_key: Secret = Secret.from_env_var("VALYU_API_KEY"),
        extract_effort: Optional[ExtractEffort] = None,
        response_length: Optional[ContentsResponseLength] = None,
        summary: Optional[Union[bool, str, Dict[str, Any]]] = None,
    ):
        """
        Initialize the ValyuContentFetcher component.

        :param api_key: API key for Valyu Content API. Defaults to VALYU_API_KEY environment variable.
        :param extract_effort: Extraction thoroughness - "normal", "high", or "auto"
        :param response_length: Content length per URL - "short", "medium", "large", "max", or int
        :param summary: AI summary config - False/None (no AI), True (basic), str (custom), or dict (schema)
        """
        self.api_key = api_key
        self.extract_effort = extract_effort
        self.response_length = response_length
        self.summary = summary

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
            extract_effort=self.extract_effort,
            response_length=self.response_length,
            summary=self.summary,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValyuContentFetcher":
        """
        Deserializes the component from a dictionary.

        :returns: Deserialized component.
        """
        deserialize_secrets_inplace(data["init_parameters"], keys=["api_key"])
        return default_from_dict(cls, data)

    def _call_api(self, urls: List[str]) -> List[Document]:
        """
        Calls the Valyu Contents API using the Valyu SDK.
        Note: The Contents API accepts multiple URLs (max 10) per request.
        """
        # Use the Valyu SDK's contents method with input validation
        response = self.valyu_client.contents(
            urls=urls,
            summary=self.summary,
            extract_effort=self.extract_effort,
            response_length=self.response_length,
        )

        # Check if the request was successful
        if not response.success:
            error_msg = response.error or "Unknown error"
            raise ComponentError(f"Valyu API returned error: {error_msg}")

        # Parse the ContentsResponse format
        documents = []
        for result in response.results:
            # Handle different content types (str, int, float)
            content = result.content
            if not isinstance(content, str):
                content = str(content)

            # Prepare metadata
            meta = {
                "url": result.url,
                "title": result.title,
                "length": result.length,
                "source": result.source,
                "data_type": result.data_type,
            }

            doc = Document(content=content, meta=meta)
            documents.append(doc)

        logger.debug(
            "ValyuContentFetcher returned {number_documents} documents for {number_urls} URLs",
            number_documents=len(documents),
            number_urls=len(urls),
        )

        return documents

    @component.output_types(documents=List[Document])
    def run(
        self,
        urls: Optional[List[str]] = None,
    ) -> Dict[str, List[Document]]:
        """
        Extract content from URLs using the Valyu Content API.

        :param urls: List of URLs to fetch content from
        :param documents: List of Documents with URLs in their metadata
        :returns: Dictionary with 'documents' key containing list of Document objects with extracted content
        """

        # Remove duplicates while preserving order
        urls_to_fetch = list(dict.fromkeys(urls))

        if not urls_to_fetch:
            return {"documents": []}

        # Batch process URLs (max 10 per request)
        fetched_documents = []
        # Process in batches of 10 (API limit)
        for i in range(0, len(urls_to_fetch), 10):
            batch = urls_to_fetch[i : i + 10]
            try:
                docs = self._call_api(batch)
                fetched_documents.extend(docs)
            except Exception as e:
                logger.warning(f"Failed to fetch content for batch {i//10 + 1}: {str(e)}")
                continue

        return {"documents": fetched_documents}
