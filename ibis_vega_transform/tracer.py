import os
import jaeger_client

__all__ = ["tracer"]


jaeger_config = jaeger_client.Config(
    config={
        "sampler": {"type": "const", "param": 1},
        "logging": True,
        # Increase max length of logs so we can save vega lite specs
        "max_tag_value_length": 1000 * 100,
        # Send each trace one by one, dont wait for next
        # Need this b/c eventloop stops once cell is done executing
        # in jupyter
        "reporter_batch_size": 1,
    },
    service_name=os.environ.get("JAEGER_SERVICE_NAME", "kernel"),
    validate=True,
)

tracer = jaeger_config.initialize_tracer()
