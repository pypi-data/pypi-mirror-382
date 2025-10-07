"""
A module for common configuration interfaces.
"""

# built-in
from pathlib import Path
from sys import executable
from typing import Any, Dict, NamedTuple, Optional, Set, Type, TypeVar

# third-party
from vcorelib.dict import merge
from vcorelib.dict.codec import BasicDictCodec as _BasicDictCodec
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io import DEFAULT_INCLUDES_KEY
from vcorelib.io import JsonObject as _JsonObject
from vcorelib.paths import Pathlike, find_file, normalize

# internal
from yambs import PKG_NAME
from yambs.dependency.config import Dependency
from yambs.schemas import YambsDictCodec as _YambsDictCodec

T = TypeVar("T", bound="CommonConfig")
DEFAULT_CONFIG = f"{PKG_NAME}.yaml"


class Project(NamedTuple):
    """An object for managing project metadata."""

    name: str
    major: int
    minor: int
    patch: int

    # GitHub attributes.
    repo: str
    owner: Optional[str]

    @staticmethod
    def create(data: _JsonObject) -> "Project":
        """Create a project instance from JSON data."""

        ver = data["version"]

        name: str = data["name"]  # type: ignore
        github: Dict[str, str] = data.get("github", {})  # type: ignore
        github.setdefault("repo", name)

        return Project(
            name,
            ver["major"],  # type: ignore
            ver["minor"],  # type: ignore
            ver["patch"],  # type: ignore
            github["repo"],
            github.get("owner"),
        )

    @property
    def version(self) -> str:
        """Get this project's version string."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def __str__(self) -> str:
        """Get this project as a string."""
        return f"{self.name}-{self.version}"


class CommonConfig(_YambsDictCodec, _BasicDictCodec):
    """A common, base configuration."""

    data: Dict[str, Any]

    root: Path
    src_root: Path
    build_root: Path
    ninja_root: Path
    dist_root: Path
    third_party_root: Path

    file: Optional[Path]

    dependencies: Set[Dependency]

    def directory(
        self, name: str, mkdir: bool = True, root: Path = None
    ) -> Path:
        """Get a configurable directory."""

        name_root = Path(str(self.data[name]))
        if not name_root.is_absolute():
            if root is None:
                root = self.root
            name_root = root.joinpath(name_root)

        if mkdir:
            name_root.mkdir(parents=True, exist_ok=True)

        return name_root

    def init(self, data: _JsonObject) -> None:
        """Initialize this instance."""

        self.data = data
        self.root = Path(data["root"])  # type: ignore

        self.data["config_file"] = str(DEFAULT_CONFIG)
        self.data["python"] = str(Path(executable).name)
        self.data["entry"] = f"{self.data['python']} -m {PKG_NAME}"

        self.src_root = self.directory("src_root")
        self.build_root = self.directory("build_root")
        self.ninja_root = self.directory("ninja_out")
        self.dist_root = self.directory("dist_out")
        self.third_party_root = self.directory("third_party_root")

        self.file = None

        self.project = Project.create(data["project"])  # type: ignore

        # Collect project dependency data.
        self.dependencies: Set[Dependency] = set()
        for dep in data.get("dependencies", []):  # type: ignore
            new_dep = Dependency(data=dep, verify=False)  # type: ignore
            new_dep.github.setdefault("owner", self.project.owner)
            self.dependencies.add(new_dep)

    @property
    def third_party_script(self) -> Path:
        """Get the path to the third-party build script."""
        return self.ninja_root.joinpath("third_party.sh")

    @classmethod
    def load(
        cls: Type[T],
        path: Pathlike = DEFAULT_CONFIG,
        package_config: str = DEFAULT_CONFIG,
        root: Pathlike = None,
    ) -> T:
        """Load a configuration."""

        src_config = find_file(package_config, package=PKG_NAME)
        assert src_config is not None

        path = normalize(path)

        data = merge(
            _ARBITER.decode(
                src_config,
                includes_key=DEFAULT_INCLUDES_KEY,
                require_success=True,
            ).data,
            _ARBITER.decode(path, includes_key=DEFAULT_INCLUDES_KEY).data,
            # Always allow the project-specific configuration to override
            # package data.
            expect_overwrite=True,
        )

        if root is not None:
            data["root"] = str(normalize(root))

        result = cls.create(data)

        if path.is_file():
            result.file = path
            result.data["config_file"] = str(path)

        # ifgen configuration not required.
        if "ifgen_config" in data and not Path(data["ifgen_config"]).is_file():
            del data["ifgen_config"]

        return result
