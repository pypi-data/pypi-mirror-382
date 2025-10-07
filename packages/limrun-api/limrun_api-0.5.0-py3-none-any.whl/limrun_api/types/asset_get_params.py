# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AssetGetParams"]


class AssetGetParams(TypedDict, total=False):
    include_download_url: Annotated[bool, PropertyInfo(alias="includeDownloadUrl")]
    """Toggles whether a download URL should be included in the response"""

    include_upload_url: Annotated[bool, PropertyInfo(alias="includeUploadUrl")]
    """Toggles whether an upload URL should be included in the response"""
