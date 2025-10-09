"""
Provides reusable serialization components for Kafka clients with:
- Schema Registry integration
- Bidirectional Avro serialization
- Schema caching
- Model class resolution
- Error handling
"""

import json
import logging
import struct
from functools import lru_cache
from typing import TypeVar

from confluent_kafka import Message
from confluent_kafka.schema_registry import SchemaRegistryClient

from otteroad.avro.model import AvroEventModel
from otteroad.utils import LoggerAdapter, LoggerProtocol

EventModel = TypeVar("EventModel", bound=AvroEventModel)


class AvroSerializerMixin:
    """
    Mixin class providing Avro serialization capabilities for Kafka clients.

    Features:
    - Schema Registry integration
    - Message serialization/deserialization
    - Schema caching for performance
    - Automatic model class resolution
    - Comprehensive error handling

    Args:
        schema_registry_client: Schema Registry client instance
        logger: Custom logger instance (default: module logger)
    """

    def __init__(
        self,
        schema_registry_client: SchemaRegistryClient,
        *args,
        logger: LoggerProtocol | LoggerAdapter | None = None,
        **kwargs,
    ):
        """
        Initialize serializer with Schema Registry client.

        Args:
            schema_registry_client: Configured Schema Registry client
            logger: Custom logger implementation
        """
        super().__init__(*args, **kwargs)
        self._logger = LoggerAdapter(logger or logging.getLogger(__name__))
        if isinstance(logger, LoggerAdapter):
            self._logger = logger
        self.schema_registry = schema_registry_client
        self._schema_cache: dict[int, type[AvroEventModel]] = {}

    @lru_cache(maxsize=100)
    def _get_schema_str(self, schema_id: int) -> str:  # pylint: disable=missing-raises-doc
        """
        Retrieve schema string from Schema Registry with caching.

        Args:
            schema_id: Schema Registry schema ID

        Returns:
            str: Avro schema JSON string

        Raises:
            SchemaRegistryError: If schema retrieval fails
        """
        try:
            return self.schema_registry.get_schema(schema_id).schema_str
        except Exception as e:
            self._logger.error("Schema fetch failed", schema_id=schema_id, error=repr(e), exc_info=True)
            raise

    def _get_model_class(self, schema_id: int) -> type[EventModel]:
        """
        Resolve AvroEventModel class from schema ID.

        Args:
            schema_id: Schema Registry schema ID

        Returns:
            type[AvroEventModel]: Corresponding model class

        Raises:
            ValueError: If no matching model class found
        """
        if schema_id not in self._schema_cache:
            schema_str = self._get_schema_str(schema_id)
            # Search through all registered subclasses
            for model in AvroEventModel.__subclasses__():
                if json.dumps(model.avro_schema(), separators=(",", ":")) == schema_str:
                    self._schema_cache[schema_id] = model
                    self._logger.debug("Cached model", model=model.__name__, schema_id=schema_id)
                    break
            else:
                self._logger.warning("No registered model for given schema", schema_id=schema_id)
                return None

        return self._schema_cache[schema_id]

    def serialize_message(self, event: EventModel) -> bytes:
        """
        Serialize AvroEventModel instance to Confluent wire format.

        Args:
            event: Event model instance to serialize

        Returns:
            bytes: Serialized message bytes with header

        Raises:
            RuntimeError: If serialization fails
        """
        try:
            self._logger.debug("Serializing...", event_model=type(event).__name__)
            return event.serialize(self.schema_registry)
        except Exception as e:
            error_msg = f"Serialization failed for {type(event).__name__}: {repr(e)}"
            self._logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def deserialize_message(self, message: Message) -> AvroEventModel | None:
        """
        Deserialize Kafka message to AvroEventModel instance.

        Args:
            message: Raw Kafka message

        Returns:
            AvroEventModel | None: Deserialized event instance or None if message was not registered

        Raises:
            RuntimeError: If deserialization fails
            ValueError: For invalid message format
        """
        try:  # pylint: disable=too-many-try-statements
            self._logger.debug("Deserializing message", topic=message.topic())
            value = message.value()

            if not value or len(value) < 5:
                self._logger.warning("Invalid message: missing or incomplete value")
                return None

            # Extract Confluent header (magic byte + schema ID)
            magic, schema_id = struct.unpack(">bI", value[:5])
            if magic != 0:
                self._logger.warning(f"Invalid magic byte: {magic}")
                return None

            self._logger.debug("Deserializing schema", schema_id=schema_id)
            model_class = self._get_model_class(schema_id)
            if model_class is None:
                return None
            return model_class.deserialize(value, self.schema_registry)

        except Exception as e:
            error_msg = f"Deserialization failed: {repr(e)}"
            self._logger.error(
                "Deserialization error",
                topic=message.topic(),
                partition=message.partition(),
                offset=message.offset(),
                error=repr(e),
                exc_info=True,
            )
            raise RuntimeError(error_msg) from e
