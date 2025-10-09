import os

from dotenv import load_dotenv

load_dotenv()


class AMQPconfig:
    def __init__(
        self,
        rabbitmq_hosts: str | None = None,
        rabbitmq_port: int | None = None,
        amqp_user: str | None = None,
        amqp_password: str | None = None,
        *,
        ssl: bool = False,
    ):
        self.ssl = ssl
        hosts_env = rabbitmq_hosts or os.getenv("RABBITMQ_N_HOST", "localhost")
        self.hosts = [h.strip() for h in hosts_env.split(",")]

        self.rabbitmq_port = rabbitmq_port or int(os.getenv("RABBITMQ_PORT", "5672"))
        self.amqp_user = amqp_user or os.getenv("AMQP_USERNAME", "guest")
        self.amqp_password = amqp_password or os.getenv("AMQP_PASSWORD", "guest")

    def connection_urls(self) -> str:
        scheme = "amqps" if self.ssl else "amqp"
        urls = [
            f"{scheme}://{self.amqp_user}:{self.amqp_password}@{host}:{self.rabbitmq_port}"
            for host in self.hosts
        ]
        return ";".join(urls)
