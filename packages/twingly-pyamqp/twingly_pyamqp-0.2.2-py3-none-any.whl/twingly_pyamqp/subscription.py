import logging
import threading
from collections.abc import Callable
from zlib import decompress

from kombu import Connection, Exchange, Queue, binding
from kombu.mixins import ConsumerMixin

from twingly_pyamqp.amqp_config import AMQPconfig
from twingly_pyamqp.constants import DEFAULT_EXCHANGE_OPTS, DEFAULT_QUEUE_OPTS


class Subscription(ConsumerMixin):
    def __init__(
        self,
        queue_names: list[str],
        exchange_name: str | None = None,
        bindings: dict[str, list[str]] | None = None,
        config: AMQPconfig = None,
        queue_opts: dict | None = None,
        exchange_opts: dict | None = None,
        **kwargs,
    ):
        if not isinstance(queue_names, list):
            msg = "queue_names must be a list of strings"
            raise TypeError(msg)

        if not queue_names:
            msg = "Must provide at least one queue name"
            raise ValueError(msg)

        if not all(isinstance(queue, str) for queue in queue_names):
            msg = "All queue names must be strings"
            raise TypeError(msg)

        self.logger = logging.getLogger(__name__)
        self.config = config or AMQPconfig()
        self.thread = None
        self.compressed_fields = kwargs.get("compressed_fields", [])
        heartbeat = kwargs.get("heartbeat", 30)

        self.connection = Connection(
            self.config.connection_urls(), heartbeat=heartbeat, ssl=self.config.ssl
        )
        if queue_opts is None:
            queue_opts = DEFAULT_QUEUE_OPTS
        if exchange_opts is None:
            exchange_opts = DEFAULT_EXCHANGE_OPTS

        self.exchange = Exchange(exchange_name or "", **exchange_opts)
        self.bindings = self._get_bindings(bindings)

        self.queues = [
            Queue(
                name,
                exchange=self.exchange,
                bindings=self.bindings.get(name),
                **queue_opts,
            )
            for name in queue_names
        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_consumers(self, Consumer, _):  # noqa: N803 - Consumer arg is a class required by ConsumerMixin
        return [
            Consumer(queues=self.queues, callbacks=self.callbacks, **self.consumer_args)
        ]

    def consume(self, *args, **kwargs):
        consume = self.connection.ensure(self.connection, super().consume)
        return consume(*args, **kwargs)

    def subscribe(
        self,
        callbacks: list[Callable[[str, object], None]],
        consumer_args: dict | None = None,
        *,
        blocking: bool = True,
    ) -> None:
        if not callbacks:
            msg = "Must provide at least one callback"
            raise ValueError(msg)
        if self.thread and self.thread.is_alive():
            msg = "Consumer is already running; call cancel() before subscribing again"
            raise RuntimeError(msg)

        self.callbacks = [self._decompress_fields, *callbacks]
        self.consumer_args = consumer_args or {}

        if blocking:
            self.run()
        else:
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def cancel(self) -> None:
        self.should_stop = True

        if self.thread:
            self.thread.join()
            self.thread = None

        self.should_stop = False

    def purge_queue(self, queue_name: str):
        self.logger.info(f"Purging queue: {queue_name}")
        self.connection.channel().queue_purge(queue=queue_name)

    def _get_bindings(self, bindings):
        if not bindings:
            return {}

        return {
            queue_name: [binding(self.exchange, routing_key=rk) for rk in routing_keys]
            for queue_name, routing_keys in bindings.items()
        }

    def _decompress_fields(self, body: object, message) -> None:
        for field in set(
            self.compressed_fields + message.headers.get("compressed_fields", [])
        ):
            if field in body:
                body[field] = decompress(body[field]).decode("utf-8")

    def close(self):
        self.cancel()
        self.connection.close()
        self.logger.info("Subscription closed.")
