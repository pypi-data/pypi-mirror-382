# Twingly::PYAMQP

[![GitHub Build Status](https://github.com/twingly/twingly-amqp/workflows/CI/badge.svg)](https://github.com/twingly/twingly-amqp/actions)

A Python implementation of the [twingly-amqp gem](https://github.com/twingly/twingly-amqp) for subscribing and publishing messages via RabbitMQ.

## Usage

Environment variables:

- `RABBITMQ_N_HOST` - Defaults to `localhost`
- `AMQP_USERNAME` - Defaults to `guest`
- `AMQP_PASSWORD` - Defaults to `guest`

## Docs

### AMQPconfig

Used to configure `RabbitMQ` host, port, user, password, and ssl. Arguments take precedence over environment variables and should only be used to override environment or default values, since env variables and default values are used if no AMQPconfig is provided.

Arguments

- rabbitmq_host
- rabbitmq_port
- amqp_user
- amqp_password
- ssl

### Publisher

#### Arguments

##### Constructor

| Argument            | Type                 | Default | Description                                                                                                                                                                                                         |
| ------------------- | -------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exchange_name`     | `str \| None`        | `None`  | The name of the exchange to route the messages to. Leave empty to publish to default exchange.                                                                                                                      |
| `routing_key`       | `str \| None`        | `None`  | The routing key used for directing the message.                                                                                                                                                                     |
| `config`            | `AMQPconfig \| None` | `None`  | Optional override configuration for AMQP connection settings.                                                                                                                                                       |
| `publish_args`      | `dict \| None`       | `None`  | Additional arguments that match the publish method arguments of Kombu's Producer.                                                                                                                                   |
| `exchange_opts`     | `dict \| None`       | `None`  | Exchange options.                                                                                                                                                                                                   |
| `max_retries`       | `int \| None`        | `None`  | Number of attempts to reconnect and publish.                                                                                                                                                                        |
| `compress_fields`   | `list[str] \| None`  | `None`  | List of fields to compress before publishing.                                                                                                                                                                       |
| `compression_level` | `int \| None`        | `None`  | level is the compression level – an integer from 0 to 9 or -1. A value of 1 (Z_BEST_SPEED) is fastest and produces the least compression, while a value of 9 (Z_BEST_COMPRESSION) is slowest and produces the most. |

##### Methods

###### publish

| Argument       | Type           | Default | Description                                  |
| -------------- | -------------- | ------- | -------------------------------------------- |
| `payload`      | `object`       | No      | The message to publish to the exchange.      |
| `routing_key`  | `str \| None`  | `None`  | Optionally override the default routing key. |
| `publish_args` | `dict \| None` | `None`  | Additional publishing arguments.             |

#### Example Usage

```python
# Create an instance of Publisher with default values
publisher = Publisher(compress_fields=["payload"])

# Create an instance of Publisher with a specific routing key
publisher = Publisher(exchange_name="custom_exchange", routing_key="custom_routing_key")

# Publish messages
publisher.publish({"message": "hello, RabbitMQ"})  # Uses the routing key specified at instantiation
publisher.publish({"message": "hello, RabbitMQ"}, routing_key="override_routing_key") # Overrides routing key

# Publish message with additional arguments
publisher.publish({"message": "hello, RabbitMQ"}, publish_args={"priority": 7})
```

---

#### Compression

The `Publisher` class supports compressing specified fields in the message payload using zlib compression. This is particularly useful for reducing the size of large text fields before sending them over the network.

###### Limitations

- Only fields of type `str` are supported for compression. Attempting to compress fields of other types will raise a `TypeError`.
- The payload must be an indexable object (like a dictionary) for compression to work, as fields are accessed via `payload[field]`.

---

### Subscription

#### Arguments

##### Constructor

| Argument            | Type                           | Default | Description                                                                  |
| ------------------- | ------------------------------ | ------- | ---------------------------------------------------------------------------- |
| `queue_names`       | `str \| list[str]`             | No      | The name of the queue(s) to subscribe to. Accepts a single name or a list.   |
| `config`            | `AMQPconfig \| None`           | `None`  | Optional override configuration for AMQP connection settings.                |
| `exchange_name`     | `str \| None`                  | `None`  | Name of `Exchange`                                                           |
| `bindings`          | `dict[str, list[str]] \| None` | `None`  | Bind `Exchange` to `Queue`, dict queue name keys and a list of routing keys. |
| `queue_opts`        | `dict \| None`                 | `None`  | Optional queue options such as `Durable`, etc.                               |
| `exchange_opts`     | `dict \| None`                 | `None`  | Optional exchange options                                                    |
| `heartbeat`         | `int`                          | `30`    | Hearbeat to check the connection.                                            |
| `compressed_fields` | `list[str] \| None`            | `None`  | Optional list of fields to decompress when receiving messages.               |

##### Methods

###### subscribe

| Argument        | Type                                                                   | Default | Description                                                                                                                                                                                 |
| --------------- | ---------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `callbacks`     | `Callable[[str, object], None] \| list[Callable[[str, object], None]]` | No      | The function(s) to process incoming messages.                                                                                                                                               |
| `blocking`      | `bool`                                                                 | `True`  | If `True`, blocks the main thread while consuming messages.                                                                                                                                 |
| `consumer_args` | `dict \| None`                                                         | `None`  | Additional arguments that match [Kombu's Consumer](https://docs.celeryq.dev/projects/kombu/en/stable/userguide/consumers.html#:~:text=Message%20consumer.-,Arguments,-%3A%C2%B6) arguments. |

Raises `RuntimeError` if a subscription is already active.

###### cancel

| Argument | Type | Default | Description                                                   |
| -------- | ---- | ------- | ------------------------------------------------------------- |
| None     | -    | -       | Cancels the active subscription and stops consuming messages. |

###### purge_queue

| Argument   | Type | Default | Description            |
| ---------- | ---- | ------- | ---------------------- |
| queue_name | str  | -       | Name of queue to purge |

#### Example Usage

```python
# Create an instance of Subscription for a single queue
subscription = Subscription(queue_names="task_queue")

# Create an instance of Subscription for multiple queues
subscription = Subscription(queue_names=["queue1", "queue2"])

# Subscribe to messages in blocking mode
subscription.subscribe(callback=Callable[[str, object], None])

# Subscribe to messages in non-blocking mode with a timeout
subscription.subscribe(callback=Callable[[str, object], None], blocking=False, timeout=5,consumer_args={"no_ack": True, "prefetch_count": 5})

# Cancel the subscription
subscription.cancel()
```

#### Decompression

The `Subscription` class supports decompressing specified fields in incoming message payloads that were previously compressed using zlib compression. If a message contains `compressed_fields` in its headers, those fields will be decompressed upon receipt. The user can also specify a default list of fields to decompress when initializing the `Subscription` instance.
