"""
Python HTTP server to record traces from the browser.

We won't need this anymore once jaeger supports clien side reporting.
"""

import os
import typing

import opentracing
from mypy_extensions import TypedDict
from typing_extensions import Literal

import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from .tracer import tracer

app = Starlette(debug=True)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

SPANS: typing.Dict[str, opentracing.Span] = {}

StartSpanExtractRequest = TypedDict(
    "StartSpanExtractRequest",
    {
        "name": str,
        "reference": dict,
        "relationship": typing.Union[Literal["child_of"], Literal["follows_from"]],
    },
)

StartSpanRequest = TypedDict(
    "StartSpanRequest",
    {
        "name": str,
        "reference": dict,
        "relationship": typing.Union[Literal["child_of"], Literal["follows_from"]],
    },
)

SpanID = TypedDict("SpanID", {"id": str})


def get_span(id_: str) -> opentracing.Span:
    try:
        return SPANS[id_]
    except KeyError:
        raise HTTPException(500, detail=f"id={id_}, spans={SPANS}")


@app.route("/start-span-extract", methods=["POST"])
async def start_span_extract(request):
    j: StartSpanExtractRequest = await request.json()
    ref = getattr(opentracing, j["relationship"])(
        (tracer.extract(opentracing.Format.TEXT_MAP, j["reference"]))
    )
    span = tracer.start_span(j["name"], references=ref)
    h = str(hash(span))
    SPANS[h] = span
    return JSONResponse({"id": h})


@app.route("/start-span", methods=["POST"])
async def start_span(request):
    j: StartSpanRequest = await request.json()
    ref = getattr(opentracing, j["relationship"])(
        get_span(j["reference"]["id"]).context
    )
    span = tracer.start_span(j["name"], references=ref)
    h = str(hash(span))
    SPANS[h] = span
    return JSONResponse({"id": h})


@app.route("/inject-span", methods=["POST"])
async def inject_span(request):
    j: SpanID = await request.json()
    injected_span = {}
    tracer.inject(get_span(j["id"]), opentracing.Format.TEXT_MAP, injected_span)
    return JSONResponse(injected_span)


@app.route("/finish-span", methods=["POST"])
async def finish_span(request):
    j: SpanID = await request.json()
    id_ = j["id"]
    get_span(id_).finish()
    del SPANS[id_]
    return JSONResponse({})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))
