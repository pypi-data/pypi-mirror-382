import os


class Config:
    def __init__(
            self,
            inner_llm_url: str = "localhost:8670",
            redis_host: str = "localhost",
            redis_port: int = 6379,
            redis_prefix_for_status: str = "job-status",
            redis_prefix_for_answer: str = "job-answer",
            rabbit_host: str = "localhost",
            rabbit_port: int = 5672,
            rabbit_login: str = "admin",
            rabbit_password: str = "admin",
            queue_name: str = "llm-api-queue",
            queue_durable: bool=True,
            base_priority: int=1,
            timeout: int = 300

    ):
        self.inner_lln_url = inner_llm_url
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_prefix_for_status = redis_prefix_for_status
        self.redis_prefix_for_answer = redis_prefix_for_answer
        self.rabbit_host = rabbit_host
        self.rabbit_port = rabbit_port
        self.rabbit_login = rabbit_login
        self.rabbit_password = rabbit_password
        self.queue_name = queue_name
        self.queue_durable = queue_durable
        self.base_priority = base_priority
        self.timeout = timeout

    @classmethod
    def read_from_env(cls) -> 'Config':
        return Config(
            os.environ.get("INNER_LLM_URL"),
            os.environ.get("REDIS_HOST"),
            int(os.environ.get("REDIS_PORT")),
            os.environ.get("REDIS_PREFIX_FOR_STATUS"),
            os.environ.get("REDIS_PREFIX_FOR_ANSWER"),
            os.environ.get("RABBIT_MQ_HOST"),
            int(os.environ.get("RABBIT_MQ_PORT")),
            os.environ.get("RABBIT_MQ_LOGIN"),
            os.environ.get("RABBIT_MQ_PASSWORD"),
            os.environ.get("QUEUE_NAME"),
            bool(os.environ.get("QUEUE_DURABLE")),
            int(os.getenv("BASE_PRIORITY")),
            int(os.getenv("TIMEOUT"))
        )

    @classmethod
    def read_from_env_file(cls, path: str) -> 'Config':
        with open(path) as file:
            lines = file.readlines()
        env_vars = {}
        for line in lines:
            key, value = line.split("=")
            env_vars[key] = value
        return Config(
            env_vars.get("INNER_LLM_URL"),
            env_vars.get("REDIS_HOST"),
            int(env_vars.get("REDIS_PORT")),
            env_vars.get("REDIS_PREFIX_FOR_STATUS"),
            env_vars.get("REDIS_PREFIX_FOR_ANSWER"),
            env_vars.get("RABBIT_MQ_HOST"),
            int(env_vars.get("RABBIT_MQ_PORT")),
            env_vars.get("RABBIT_MQ_LOGIN"),
            env_vars.get("RABBIT_MQ_PASSWORD"),
            env_vars.get("QUEUE_NAME"),
            bool(env_vars.get("QUEUE_DURABLE")),
            int(env_vars.get("BASE_PRIORITY")),
            int(env_vars.get("TIMEOUT"))
        )
