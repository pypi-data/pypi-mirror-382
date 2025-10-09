from typing import List, Optional

from dockertown.components.buildx.imagetools.models import ImageVariantManifest
from dockertown.utils import DockerCamelModel


class ManifestListInspectResult(DockerCamelModel):
    name: Optional[str] = None
    schema_version: Optional[int] = None  
    media_type: Optional[str] = None
    manifests: Optional[List[ImageVariantManifest]] = None
