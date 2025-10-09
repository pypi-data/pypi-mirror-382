"""
This module defines the available runtime environments supported by the
Bisslog framework. Each runtime represents a specific type of application
or execution context for which configuration and setup can be defined.
"""
from enum import Enum


class RuntimeType(str, Enum):
    """
    Enumeration of supported runtime types for configuration and setup.

    Each member represents a distinct execution context or service
    environment where Bisslog can be initialized or run.

    Attributes
    ----------
    CLI : RuntimeType
        Command-line interface execution context.
    FLASK : RuntimeType
        Flask web application runtime.
    DJANGO : RuntimeType
        Django web application runtime.
    FASTAPI : RuntimeType
        FastAPI web application runtime.
    LAMBDA : RuntimeType
        AWS Lambda function execution.
    RABBITMQ : RuntimeType
        RabbitMQ consumer or publisher context.
    KAFKA : RuntimeType
        Kafka consumer or producer context.
    REDIS : RuntimeType
        Redis-based message queue or worker.
    CRON : RuntimeType
        Scheduled job execution context (e.g., cron jobs).
    """
    CLI = "cli"
    FLASK = "flask"
    DJANGO = "django"
    FASTAPI = "fastapi"
    LAMBDA = "lambda"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
    REDIS = "redis"
    CRON = "cron"
