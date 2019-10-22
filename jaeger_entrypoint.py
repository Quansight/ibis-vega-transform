# https://jupyter-server-proxy.readthedocs.io/en/latest/server-process.html
def setup_jaeger_proxy():
    return {
        "command": ["python", "-m", "ibis_vega_transform.tracing_server"],
        "environment": {"PORT": "{port}", "JAEGER_SERVICE_NAME": "browser"},
        "launcher_entry": {"enabled": False},
    }


def setup_jaeger_all():
    return {
        "command": [
            "jaeger-all-in-one",
            "--query.port",
            "{port}",
            "--query.base-path",
            "{base_url}jaeger",
        ],
        "absolute_url": True,
        "launcher_entry": {
            "enabled": True,
            "icon_path": "./docs/jaeger.svg",
            "title": "Jaeger",
        },
    }
