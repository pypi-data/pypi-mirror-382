from __future__ import annotations

import logging
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import ProxyTracerProvider

from .decorators import with_decorators
from .exporters import (
    Exporter,
    ExportersRegistry,
)
from .integrations import apply_integrations
from .processors import AttributeProcessor
from .sdk import VerseSDK


class VerseSDKBuilder:
    exporters = ExportersRegistry()

    _initialized: bool = False
    _sdk: VerseSDK | None
    _tracer: trace.Tracer | None

    def __getattr__(self, name: str) -> Any:
        """Dynamically access methods from the SDK."""
        if not self._sdk:
            raise ValueError("SDK not initialized")

        return getattr(self._sdk, name)

    def flush(self, timeout_ms: int = 30000) -> None:
        """
        Flush all pending traces to exporters.

        Args:
            timeout_ms: Maximum time to wait for flush in milliseconds
        """
        try:
            if not self._initialized:
                return

            provider = trace.get_tracer_provider()
            if isinstance(provider, ProxyTracerProvider):
                provider.force_flush(timeout_millis=timeout_ms)
        except Exception as e:
            logging.warning("Error flushing traces", exc_info=e)

    def init(
        self,
        app_name: str = "verse_sdk_observability",
        environment: str | None = "development",
        exporters: list[Exporter] | None = None,
        vendor: str | None = None,
        version: str | None = "1.0.0",
    ) -> VerseSDK:
        """
        Lazily initialize the observability client.

        Args:
            app_name: Service name for tracing
            exporters: Exporter name(s) or None for auto-detection
            environment: Deployment environment (e.g., "production", "staging")
            version: Service version

        Returns:
            VerseSDK w/ decorations
        """
        try:
            if self._initialized:
                return self._sdk

            resource = Resource.create(
                {
                    "deployment.environment": environment,
                    "service.name": app_name,
                    "service.version": version,
                }
            )

            provider = TracerProvider(resource=resource)

            provider.add_span_processor(AttributeProcessor())

            for exporter in exporters:
                try:
                    provider.add_span_processor(
                        exporter.create_span_processor(resource)
                    )
                    logging.info(
                        "Added span processor `%s`",
                        exporter.__class__.__name__,
                    )
                except Exception as e:
                    logging.warning(
                        "Error adding span processor `%s`",
                        exporter.__class__.__name__,
                        exc_info=e,
                    )

            trace.set_tracer_provider(provider)

            self._tracer = trace.get_tracer(app_name)
            self._sdk = VerseSDK(self._tracer)
            self._sdk = with_decorators(self._sdk)
            self._initialized = True

            apply_integrations(self._sdk, vendor)
            logging.info("🚀 VerseSDK initialized")

            return self._sdk
        except Exception as e:
            logging.error("Error initializing SDK", exc_info=e)
            raise e
