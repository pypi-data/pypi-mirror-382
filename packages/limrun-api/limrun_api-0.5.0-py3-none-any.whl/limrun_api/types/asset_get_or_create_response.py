# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["AssetGetOrCreateResponse"]


class AssetGetOrCreateResponse(BaseModel):
    id: str

    name: str

    signed_download_url: str = FieldInfo(alias="signedDownloadUrl")

    signed_upload_url: str = FieldInfo(alias="signedUploadUrl")

    md5: Optional[str] = None
    """Returned only if there is a corresponding file uploaded already."""
