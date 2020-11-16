import copy
import re
import typing

import opentracing

from .globals import DATA_NAME_PREFIX, _expr_map, debug
from .tracer import tracer

__all__ = ["compiler_target_function"]

# An empty vega spec to send when we get invalid data.
EMPTY_VEGA = {
    "$schema": "https://vega.github.io/schema/vega/v5.json",
    "description": "An empty vega v5 spec",
    "width": 500,
    "height": 200,
    "padding": 5,
    "autosize": "pad",
    "signals": [],
    "data": [],
    "scales": [],
    "projections": [],
    "axes": [],
    "legends": [],
    "marks": [],
}


def compiler_target_function(comm, msg):
    """
    A function that takes a vega spec and converts its vega-transforms
    to ibis transforms, which will later be able to lazily evaluate
    upon user interactions.
    """
    data = msg["content"]["data"]
    spec = data["spec"]
    injected_span = data["span"]
    root_span = data["rootSpan"]

    root_ref = opentracing.child_of(
        (tracer.extract(opentracing.Format.TEXT_MAP, injected_span))
    )

    with tracer.start_span("compile-vega", references=root_ref) as span:
        span.log_kv({"vega-spec:initial": spec})
        debug("vega-spec:initial", spec)

        try:
            with tracer.start_span("transform-vega", child_of=span) as transform_span:
                updated_spec = _transform(spec, root_span)
                transform_span.log_kv({"vega-spec:transformed": updated_spec})
                span.log_kv({"vega-spec:transformed": updated_spec})

            comm.send(updated_spec)
        except ValueError as e:
            # If there was an error transforming the spec, which can happen
            # if we don't support all the required transforms, or if
            # the spec references an old, unavailable ibis expression,
            # then send an empty vega spec.
            comm.send(EMPTY_VEGA)
            raise e


def _transform(
    spec: typing.Dict[str, typing.Any], root_span: object
) -> typing.Dict[str, typing.Any]:
    """
    Transform a vega spec into one that uses the `queryibis` transform
    in the place of vega transforms.
    """
    new = copy.deepcopy(spec)  # make a copy of the spec
    _transforms = {}  # Store references to ibis query transforms
    _root_expressions = {}  # Keep track of the sources backed in ibis expressions

    # We iteratively pass through the data, looking
    # for named ibis data sources and data sources that
    # reference our named sources. When we can pass through
    # the entire set of data without encountering one,
    # then we are done.
    done = False
    while not done:
        for data in new["data"]:
            # First check for named data which matches an initial
            # ibis expression passed in directly via altair.
            name = data.get("name", "")
            if _is_ibis(name) and name not in _root_expressions:
                key = _retrieve_expr_key(name)
                new_transform = {"type": "queryibis", "name": key, "span": root_span}
                # If the named data has transforms, set them
                # in the ibis transform, and keep a reference
                # to them in case we need to incorporate them
                # into downstream data attributes.
                old_transform = data.get("transform", None)
                if old_transform:
                    _transforms[name] = old_transform
                    new_transform["transform"] = old_transform
                data["transform"] = [new_transform]
                _root_expressions[name] = name
                break

            # Next check to see if the data sources an upstream data set.
            # If it is one of ours, transform that as well.
            source = data.get("source", "")
            if source and source in _root_expressions:
                del data["source"]
                source_transforms = _transforms.get(source, [])
                old_transforms = data.get("transform", [])

                # Rename "signal" to "signal_" because if vega
                # sees a "signal" key on an object it will try to resolve it, instead of passing
                # it into the transform
                for t in old_transforms:
                    if "signal" in t:
                        t["signal_"] = t["signal"]
                        del t["signal"]

                new_transforms = source_transforms + old_transforms
                data["transform"] = [
                    {
                        "type": "queryibis",
                        "name": _retrieve_expr_key(_root_expressions[source]),
                        "span": root_span,
                        "data": "{"
                        + ", ".join(
                            f"{field}: data('{field}')"
                            for field in _extract_used_data(new_transforms)
                        )
                        + "}",
                        "transform": new_transforms,
                    }
                ]
                _root_expressions[name] = _root_expressions[source]
                _transforms[name] = new_transforms
                break
        # If we make it through the data sources without a `break`
        # statement, there are no more data sources to transform,
        # so we are done.
        else:
            done = True

    return _cleanup_spec(new)


def _extract_used_data(transforms) -> typing.Set[str]:
    """
    Given a list of transforms, returns a set of the data fields they depend on.
    """
    return {m.group(1) for m in re.finditer(r'data\("(.+?)"\)', str(transforms))}


assert (
    _extract_used_data(
        [
            {
                "type": "filter",
                "expr": '!(length(data("Filter_store"))) || (vlSelectionTest("Filter_store", datum))',
            }
        ]
    )
    == {"Filter_store"}
)


def _is_ibis(name: str) -> bool:
    """
    Test whether a vega data name refers to one of the ibis expressions.
    """
    return name.startswith(DATA_NAME_PREFIX)


def _retrieve_expr_key(name: str) -> typing.Optional[str]:
    if not name.startswith(DATA_NAME_PREFIX):
        return None
    key = name[len(DATA_NAME_PREFIX) :]
    if key not in _expr_map:
        raise ValueError(f"Unrecognized ibis data name {name}")
    return key


def _cleanup_spec(spec):
    """
    Goes through the spec and removes data sources that are not referenced
    anywhere else in the spec. Does this by turning the spec into a string
    and seeing if the name of the data is in the string.
    """

    nonreferenced_data = []
    for data in spec["data"]:
        name = data["name"]
        # create a vesion of the spec where this data is removed
        without_this_data = copy.deepcopy(spec)
        without_this_data["data"].remove(data)
        has_reference = name in str(without_this_data)
        if not has_reference:
            nonreferenced_data.append(data)

    new = copy.deepcopy(spec)
    new["data"] = [data for data in new["data"] if data not in nonreferenced_data]
    return new
