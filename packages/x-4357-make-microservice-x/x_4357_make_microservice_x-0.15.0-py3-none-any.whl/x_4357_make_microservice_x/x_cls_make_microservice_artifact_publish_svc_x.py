from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Protocol


@dataclass(slots=True)
class BuildArtifacts:
    sdist: Path
    wheel: Path


class BuildSpec(Protocol):
    project: str
    version: str
    metadata: Mapping[str, str]


class PublishOutcome(Protocol):
    version: str
    artifacts: Mapping[str, Path]


BuildFn = Callable[[BuildSpec], BuildArtifacts]
VerifierFn = Callable[[BuildArtifacts], None]
DifferFn = Callable[[str, BuildArtifacts], None]
PublisherFn = Callable[[BuildArtifacts, str], PublishOutcome]


class x_cls_make_microservice_artifact_publish_svc_x:
    """Type-driven orchestrator for deterministic artifact publishing."""

    def __init__(
        self,
        build_fn: BuildFn,
        verify_reproducibility: VerifierFn,
        diff_release: DifferFn,
        publish_fn: PublisherFn,
    ) -> None:
        self._build = build_fn
        self._verify = verify_reproducibility
        self._diff = diff_release
        self._publish = publish_fn

    def publish(self, spec: BuildSpec, sign_key: str) -> PublishOutcome:
        artifacts = self._build(spec)
        if not artifacts.sdist.exists() or not artifacts.wheel.exists():
            raise FileNotFoundError(
                f"Build outputs missing for {spec.project} {spec.version}"
            )
        self._verify(artifacts)
        self._diff(spec.project, artifacts)
        result = self._publish(artifacts, sign_key)
        if result.version != spec.version:
            raise ValueError(
                f"Version drift detected: spec={spec.version} published={result.version}"
            )
        return result
