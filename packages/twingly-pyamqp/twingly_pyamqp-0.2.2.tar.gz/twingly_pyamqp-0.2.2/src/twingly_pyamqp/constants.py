DEFAULT_QUEUE_OPTS = {
    "durable": True,
    "queue_arguments": {"x-queue-type": "quorum"},
}

DEFAULT_EXCHANGE_OPTS = {"durable": True}
