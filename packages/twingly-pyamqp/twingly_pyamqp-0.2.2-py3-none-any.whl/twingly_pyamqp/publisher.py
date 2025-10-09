import logging
from zlib import Z_BEST_SPEED, compress

from kombu import Connection, Exchange

from twingly_pyamqp.amqp_config import AMQPconfig
from twingly_pyamqp.constants import DEFAULT_EXCHANGE_OPTS


class Publisher:
    def __init__(
        self,
        exchange_name: str | None = None,
        routing_key: str | None = None,
        config: AMQPconfig = None,
        exchange_opts: dict | None = None,
        heartbeat: int = 60,
        **kwargs,
    ):
        self.logger = logging.getLogger(__name__)
        self.config = config or AMQPconfig()
        self.connection = Connection(self.config.connection_urls(), heartbeat=heartbeat)
        self.exchange = Exchange(
            exchange_name or "", **(exchange_opts or DEFAULT_EXCHANGE_OPTS)
        )
        self.routing_key = routing_key
        self.max_retries = kwargs.get("max_retries")
        self.compress_fields = kwargs.get("compress_fields", [])
        self.compression_level = kwargs.get("compression_level", Z_BEST_SPEED)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def publish(
        self,
        payload: object,
        routing_key: str | None = None,
        publish_args: dict | None = None,
    ):
        key = routing_key or self.routing_key

        self._compress_fields(payload, self.compression_level)

        producer = self.connection.Producer()
        publish = self.connection.ensure(
            producer,
            producer.publish,
            errback=self.on_connection_error,
            max_retries=self.max_retries,
        )
        if publish_args is None:
            publish_args = {}
        if self.compress_fields:
            headers = publish_args.setdefault("headers", {})
            headers["compressed_fields"] = self.compress_fields

        publish(
            payload,
            exchange=self.exchange,
            routing_key=key,
            **(publish_args),
        )

    def on_connection_error(self, exc: Exception, _):
        self.logger.error(f"Connection error occurred: {exc}")

    def close(self):
        self.connection.close()
        self.logger.info("Publisher closed.")

    def _compress_fields(self, payload: object, compression: int) -> None:
        for field in self.compress_fields:
            if field in payload:
                if not isinstance(payload[field], str):
                    msg = f"Compression only supported for 'string' fields, but field '{field}' is of type {type(payload[field]).__name__}"
                    raise TypeError(msg)
                payload[field] = compress(
                    payload[field].encode("utf-8"), level=compression
                )
