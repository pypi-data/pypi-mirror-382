from dataclasses import dataclass, field

from avatar_yaml.models.common import Metadata, ModelKind


@dataclass(frozen=True)
class AvatarMetadataSpec:
    display_name: str | None


@dataclass(frozen=True)
class AvatarMetadata:
    kind: ModelKind
    metadata: Metadata
    spec: AvatarMetadataSpec | None = None
    annotations: dict[str, str] = field(default_factory=dict)


def get_metadata(
    display_name: str | None = None, annotations: dict[str, str] = {}
) -> AvatarMetadata:
    return AvatarMetadata(
        kind=ModelKind.METADATA,
        metadata=Metadata(name=f"avatar-metadata-{display_name}"),
        spec=AvatarMetadataSpec(display_name=display_name),
        annotations=annotations,
    )
