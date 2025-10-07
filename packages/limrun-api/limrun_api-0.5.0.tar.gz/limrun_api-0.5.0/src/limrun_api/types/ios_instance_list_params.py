# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["IosInstanceListParams"]


class IosInstanceListParams(TypedDict, total=False):
    label_selector: Annotated[str, PropertyInfo(alias="labelSelector")]
    """
    Labels filter to apply to instances to return. Expects a comma-separated list of
    key=value pairs (e.g., env=prod,region=us-west).
    """

    region: str
    """Region where the instance is scheduled on."""

    state: Literal["unknown", "creating", "ready", "terminated"]
    """State filter to apply to instances to return."""
