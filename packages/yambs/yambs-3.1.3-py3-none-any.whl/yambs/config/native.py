"""
A module implementing a configuration interface for native builds.
"""

# third-party
from vcorelib.paths import Pathlike

# internal
from yambs.config.common import DEFAULT_CONFIG, CommonConfig


class Native(CommonConfig):
    """The top-level configuration object for the package."""

    def has_variant(self, name: str) -> bool:
        """Determine whether or not"""
        return name in self.data.get("variants", {})


def load_native(
    path: Pathlike = DEFAULT_CONFIG, root: Pathlike = None
) -> Native:
    """Load a native configuration object."""
    return Native.load(path=path, root=root, package_config="native.yaml")
