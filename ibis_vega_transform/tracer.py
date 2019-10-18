import jaeger_client

import os

__all__ = ["tracer"]


jaeger_config = jaeger_client.Config(
    config={"sampler": {"type": "const", "param": 1}, "logging": True},
    service_name=os.environ.get("JAEGER_SERVICE_NAME", "kernel"),
    validate=True,
)

tracer = jaeger_config.initialize_tracer()
