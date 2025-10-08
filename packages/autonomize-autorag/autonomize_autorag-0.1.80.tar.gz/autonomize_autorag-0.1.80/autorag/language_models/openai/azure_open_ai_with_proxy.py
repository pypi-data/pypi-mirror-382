"""Azure OpenAI Language Model with Proxy implementation using the OpenAI client for Azure."""

# pylint: disable=line-too-long, duplicate-code

import os
from typing import Optional

import httpx

try:
    from openai import AsyncOpenAI, OpenAI
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate openai package. "
        'Please install it with `pip install "autonomize-autorag[openai]"`.'
    ) from err

from autorag.language_models.openai.base_openai import OpenAILanguageModel


class AzureOpenAILanguageModelWithProxy(OpenAILanguageModel):
    """
    Azure OpenAI Language Model implementation using the OpenAI client for Azure.

    This class utilizes Azure's OpenAI API to generate chat completions for text data.
    It allows specifying the API key, base URL, and version, either directly or via
    environment variables.

    Example:
    .. code-block:: python

        from autorag.language_models import AzureOpenAILanguageModel

        model_name = "gpt-4o"
        llm = AzureOpenAILanguageModel()

        llm.generate(
            messages=[{"role": "user", "content": "What is RAG?"}],
            model=model_name
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        proxy_api_endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
        http_client: httpx.Client | None = None,
        async_http_client: httpx.AsyncClient | None = None,
    ):
        """
        Initializes the Azure OpenAI client.

        Args:
            api_key (Optional[str]): Azure OpenAI API key. Not used, syntax requirement
            proxy_api_endpoint (Optional[str]): Endpoint for the proxy behind which open ai is used.
            api_version (Optional[str]): Azure OpenAI API version
            use_managed_identity (bool): If True,
        """
        super().__init__(api_key=api_key)

        self.azure_endpoint = proxy_api_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = api_version or os.getenv("OPENAI_API_VERSION")

        if not self.azure_endpoint:
            raise ValueError(
                "The Azure endpoint URL must be set either by passing 'azure_endpoint' or by setting the 'AZURE_OPENAI_ENDPOINT' environment variable."
            )

        if not self.api_version:
            raise ValueError(
                "The API version must be set either by passing 'api_version' or by setting the 'OPENAI_API_VERSION' environment variable."
            )

        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.azure_endpoint,
            http_client=http_client,
        )
        self._aclient = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.azure_endpoint,
            http_client=async_http_client,
        )
