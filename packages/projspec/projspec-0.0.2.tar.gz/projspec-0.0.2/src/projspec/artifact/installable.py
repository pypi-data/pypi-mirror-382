import logging
import os.path
import subprocess

from projspec.artifact import BaseArtifact

logger = logging.getLogger("projspec")


class Wheel(BaseArtifact):
    """An installable python wheel file

    Note that in general there may be a set of wheels for different platforms.
    The actual name of the wheel file depends on platform, vcs config
    and maybe other factors. We just check if the dist/ directory is
    populated.

    This output is intended to be _local_ - pushing to a remote location (e.g., pypi)
    is call publishing.
    """

    def _is_done(self) -> bool:
        return True

    def _is_clean(self) -> bool:
        files = self.proj.fs.glob(f"{self.proj.url}/dist/*.whl")
        return len(files) == 0

    def clean(self):
        files = self.proj.fs.glob(f"{self.proj.url}/dist/*.whl")
        self.proj.fs.rm(files)


class CondaPackage(BaseArtifact):
    """An installable python wheel file

    Note that in general, there may be a set of wheels for different platforms.
    The actual name of the wheel file depends on the platform, vcs config
    and maybe other factors. We just check if the dist/ directory is
    populated.

    This output is intended to be _local_ - pushing to a remote location (e.g., pypi)
    is call publishing.
    """

    def __init__(self, path=None, name=None, **kwargs):
        super().__init__(**kwargs)
        self.path: str | None = path
        self.name = name

    def _make(self, *args, **kwargs):
        import re

        logger.debug(" ".join(self.cmd))
        out = subprocess.check_output(self.cmd).decode("utf-8")
        if fn := re.match(r"'(.*?\.conda)'\n", out):
            if os.path.exists(fn.group(1)):
                self.path = fn.group(1)

    def _is_done(self) -> bool:
        return True

    def _is_clean(self) -> bool:
        return self.path is None or not self.proj.fs.glob(self.path)

    def clean(self):
        if self.path is not None:
            self.proj.fs.rm(self.path)
