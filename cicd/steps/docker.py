import platform
from collections.abc import Iterator
from datetime import datetime
from logging import Logger
from pathlib import Path

from dateutil import tz
from mpyl import Repository, RepoConfig
from mpyl.steps import Step, Meta, ArtifactType, Input, Output
from mpyl.steps.models import input_to_artifact, ArchiveSpec
from mpyl.utilities.docker import DockerImageSpec
from python_on_whales import Image, docker
from rich.filesize import decimal

DIRNAME = Path(__file__).parent


def _get_version(repo: Repository) -> str:
    branch = repo.get_branch
    if branch == "master":
        tags = repo._repo.tags
        head_commit = repo._repo.head.commit
        tag = next(t.name for t in tags if t.commit == head_commit)
        if tag is None:
            raise ValueError("No tag found for HEAD on master")
        return tag
    return branch.split("/")[-1].lower()

def _get_architecture() -> str:
    if platform.uname().processor == "arm":
        return "arm64"
    return "amd64"


def build_docker(logger: Logger, service_jar_path: Path, service: str, repo: Repository, context: Path = Path()) -> (str, Image | None):
    """Build a Docker image for wrapping the given service's .jar."""
    docker_file = Path(DIRNAME, "jre.Dockerfile")
    if not docker_file.exists():
        raise FileNotFoundError(f"Docker definition file {docker_file} does not exist")

    if not service_jar_path.exists():
        raise FileNotFoundError(f"Service .jar not found at {service_jar_path}")

    args = {"SERVICE": service, "ARCHIVE": service_jar_path, "GIT_COMMIT": repo.get_sha, "BUILD_DATETIME": f"{datetime.now(tz=tz.gettz())}"}

    tag = f"{service.lower()}:{_get_version(repo)}-{_get_architecture()}"
    image: Image = docker.legacy_build(file=docker_file, tags=[tag], build_args=args,
                                       context_path=context)
    if isinstance(image, Iterator):
        raise TypeError("Log stream not expected")
    logger.info(f"Built '{tag}' from {docker_file} with {args} and architecture {image.architecture}")
    logger.info(f"Image id: '{image.id}', size: {decimal(image.size)}")

    return tag, image

class AssembleDocker(Step):
    def __init__(self, logger: Logger) -> None:
        super().__init__(
            logger,
            Meta(
                name="Docker Wrap",
                description="Wrap a .jar in a JDK docker image",
                version="0.0.1",
                stage="assemble",
            ),
            produced_artifact=ArtifactType.DOCKER_IMAGE,
            required_artifact=ArtifactType.ARCHIVE,
        )

    def execute(self, step_input: Input) -> Output:
        execution = step_input.project_execution
        self._logger.info(f"Building project {execution.name}")

        archive_spec: ArchiveSpec = step_input.as_spec(ArchiveSpec)
        with Repository(RepoConfig.from_config(step_input.run_properties.config)) as repo:
            tag, image = build_docker(self._logger, Path(archive_spec.archive_path), execution.project.name, repo)

        artifact = input_to_artifact(
            artifact_type=ArtifactType.DOCKER_IMAGE,
            step_input=step_input,
            spec=DockerImageSpec(image=tag),
        )

        return Output(
            success=True,
            message=f"Built {execution.name}",
            produced_artifact=artifact,
        )