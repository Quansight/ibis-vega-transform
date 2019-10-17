import jaeger_client


__all__ = ["tracer"]


def init_jaeger_tracer(service_name="ibis_vega_transform"):
    config = jaeger_client.Config(
        config={"sampler": {"type": "const", "param": 1}, "logging": True},
        service_name=service_name,
        validate=True,
    )
    return config.initialize_tracer()


tracer = init_jaeger_tracer()
