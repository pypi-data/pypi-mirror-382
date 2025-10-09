from typing import List

from dockertown.components.buildx.imagetools.models import ImageVariantManifest
from dockertown.utils import DockerCamelModel, all_fields_optional


@all_fields_optional
class ManifestListInspectResult(DockerCamelModel):
    name: str
    schema_version: int
    media_type: str
    manifests: List[ImageVariantManifest]
