"""
OpenAI-based embedder implementation.
"""

import asyncio
import logging
import time
from typing import Any
from uuid import uuid4

import openai

from memmachine.common.data_types import ExternalServiceAPIError
from memmachine.common.metrics_factory.metrics_factory import MetricsFactory

from .embedder import Embedder

logger = logging.getLogger(__name__)


class OpenAIEmbedder(Embedder):
    """
    Embedder that uses OpenAI's embedding models
    to generate embeddings for inputs and queries.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize an OpenAIEmbedder with the provided configuration.

        Args:
            config (dict[str, Any]):
                Configuration dictionary containing:
                - api_key (str):
                  API key for accessing the OpenAI service.
                - model (str, optional):
                  Name of the OpenAI embedding model to use
                  (default: "text-embedding-3-small").
                - metrics_factory (MetricsFactory, optional):
                  An instance of MetricsFactory
                  for collecting usage metrics.
                - user_metrics_labels (dict[str, str], optional):
                  Labels to attach to the collected metrics.

        Raises:
            ValueError:
                If configuration argument values are missing or invalid.
            TypeError:
                If configuration argument values are of incorrect type.
        """
        super().__init__()

        self._model = config.get("model", "text-embedding-3-small")

        api_key = config.get("api_key")
        if api_key is None:
            raise ValueError("Embedder API key must be provided")

        self._client = openai.AsyncOpenAI(api_key=api_key)

        metrics_factory = config.get("metrics_factory")
        if metrics_factory is not None and not isinstance(
            metrics_factory, MetricsFactory
        ):
            raise TypeError("Metrics factory must be an instance of MetricsFactory")

        self._collect_metrics = False
        if metrics_factory is not None:
            self._collect_metrics = True
            self._user_metrics_labels = config.get("user_metrics_labels", {})
            label_names = self._user_metrics_labels.keys()

            self._prompt_tokens_usage_counter = metrics_factory.get_counter(
                "embedder_openai_usage_prompt_tokens",
                "Number of tokens used by prompts to OpenAI embedder",
                label_names=label_names,
            )
            self._total_tokens_usage_counter = metrics_factory.get_counter(
                "embedder_openai_usage_total_tokens",
                "Number of tokens used by requests to OpenAI embedder",
                label_names=label_names,
            )
            self._latency_summary = metrics_factory.get_summary(
                "embedder_openai_latency_seconds",
                "Latency in seconds for OpenAI embedder requests",
                label_names=label_names,
            )

    async def ingest_embed(
        self,
        inputs: list[Any],
        max_attempts: int = 1,
    ) -> list[list[float]]:
        return await self._embed(inputs, max_attempts)

    async def search_embed(
        self,
        queries: list[Any],
        max_attempts: int = 1,
    ) -> list[list[float]]:
        return await self._embed(queries, max_attempts)

    async def _embed(
        self,
        inputs: list[Any],
        max_attempts: int = 1,
    ) -> list[list[float]]:
        if not inputs:
            return []
        if max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer")

        inputs = [input.replace("\n", " ") if input else "\n" for input in inputs]

        embed_call_uuid = uuid4()

        start_time = time.monotonic()

        sleep_seconds = 1
        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug(
                    "[call uuid: %s] "
                    "Attempting to create embeddings using %s OpenAI model: "
                    "on attempt %d with max attempts %d",
                    embed_call_uuid,
                    self._model,
                    attempt,
                    max_attempts,
                )
                response = await self._client.embeddings.create(
                    input=inputs, model=self._model
                )
                break
            except (
                openai.RateLimitError,
                openai.APITimeoutError,
                openai.APIConnectionError,
            ) as e:
                # Exception may be retried.
                if attempt >= max_attempts:
                    error_message = (
                        f"[call uuid: {embed_call_uuid}] "
                        "Giving up creating embeddings "
                        f"after failed attempt {attempt} "
                        f"due to retryable {type(e).__name__}: "
                        f"max attempts {max_attempts} reached"
                    )
                    logger.error(error_message)
                    raise ExternalServiceAPIError(error_message)

                logger.info(
                    "[call uuid: %s] "
                    "Retrying creating embeddings in %d seconds "
                    "after failed attempt %d due to retryable %s...",
                    embed_call_uuid,
                    sleep_seconds,
                    attempt,
                    type(e).__name__,
                )
                await asyncio.sleep(sleep_seconds)
                sleep_seconds *= 2
                continue
            except (openai.APIError, openai.OpenAIError) as e:
                error_message = (
                    f"[call uuid: {embed_call_uuid}] "
                    "Giving up creating embeddings "
                    f"after failed attempt {attempt} "
                    f"due to non-retryable {type(e).__name__}"
                )
                logger.error(error_message)
                if isinstance(e, openai.APIError):
                    raise ExternalServiceAPIError(error_message)
                else:
                    raise RuntimeError(error_message)

        end_time = time.monotonic()
        logger.debug(
            "[call uuid: %s] Embeddings created in %.3f seconds",
            embed_call_uuid,
            end_time - start_time,
        )

        if self._collect_metrics:
            self._prompt_tokens_usage_counter.increment(
                value=response.usage.prompt_tokens,
                labels=self._user_metrics_labels,
            )
            self._total_tokens_usage_counter.increment(
                value=response.usage.total_tokens,
                labels=self._user_metrics_labels,
            )
            self._latency_summary.observe(
                value=end_time - start_time,
                labels=self._user_metrics_labels,
            )

        return [datum.embedding for datum in response.data]
