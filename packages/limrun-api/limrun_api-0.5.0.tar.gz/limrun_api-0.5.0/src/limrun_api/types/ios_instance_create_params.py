# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["IosInstanceCreateParams", "Metadata", "Spec", "SpecClue", "SpecInitialAsset"]


class IosInstanceCreateParams(TypedDict, total=False):
    wait: bool
    """Return after the instance is ready to connect."""

    metadata: Metadata

    spec: Spec


class Metadata(TypedDict, total=False):
    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    labels: Dict[str, str]


class SpecClue(TypedDict, total=False):
    kind: Required[Literal["ClientIP"]]

    client_ip: Annotated[str, PropertyInfo(alias="clientIp")]


class SpecInitialAsset(TypedDict, total=False):
    kind: Required[Literal["App"]]

    source: Required[Literal["URL", "AssetName"]]

    asset_name: Annotated[str, PropertyInfo(alias="assetName")]

    url: str


class Spec(TypedDict, total=False):
    clues: Iterable[SpecClue]

    hard_timeout: Annotated[str, PropertyInfo(alias="hardTimeout")]
    """
    After how many minutes should the instance be terminated. Example values 1m,
    10m, 3h. Default is "0" which means no hard timeout.
    """

    inactivity_timeout: Annotated[str, PropertyInfo(alias="inactivityTimeout")]
    """
    After how many minutes of inactivity should the instance be terminated. Example
    values 1m, 10m, 3h. Default is 3m. Providing "0" disables inactivity checks
    altogether.
    """

    initial_assets: Annotated[Iterable[SpecInitialAsset], PropertyInfo(alias="initialAssets")]

    region: str
    """The region where the instance will be created.

    If not given, will be decided based on scheduling clues and availability.
    """
