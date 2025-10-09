from __future__ import annotations

from typing import List, Optional

import pydantic


class ManifestConfig(pydantic.BaseModel):
    media_type: Optional[str] = pydantic.Field(alias="mediaType")
    digest: Optional[str]
    size: Optional[int]


class ManifestLayer(pydantic.BaseModel):
    media_type: str = pydantic.Field(alias="mediaType")
    digest: Optional[str]
    size: Optional[int]


class ManifestPlatform(pydantic.BaseModel):
    architecture: Optional[str]
    os: Optional[str]
    os_version: Optional[str]
    variant: Optional[str]

    def as_string(self) -> str:
        parts = []
        if self.os:
            parts.append(self.os)
        if self.os_version:
            parts.append(self.os_version)
        if self.architecture:
            parts.append(self.architecture)
        if self.variant:
            parts.append(self.variant)
        return "/".join(parts)


class ImageVariantManifest(pydantic.BaseModel):
    media_type: str = pydantic.Field(alias="mediaType")
    size: int
    digest: str
    platform: Optional[ManifestPlatform]


class Manifest(pydantic.BaseModel):
    media_type: str = pydantic.Field(alias="mediaType")
    schema_version: int = pydantic.Field(alias="schemaVersion")
    layers: Optional[List[ManifestLayer]]
    manifests: Optional[List[ImageVariantManifest]]
    config: Optional[ManifestConfig]
