import os
import re

from setuptools import Distribution, setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.build_py import build_py


def get_version(root):
    src = os.path.join(root, "src", "qerent_keyring", "__init__.py")

    with open(src, "r", encoding="utf-8", errors="strict") as f:
        txt = f.read()

    m = re.search(r"__version__\s*=\s*['\"](.+?)['\"]", txt)
    return m.group(1) if m else "0.1.0"


class BuildKeyring(build_py):
    def run(self):
        super().run()


class BuildKeyringPlatformWheel(bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        self.root_is_pure = False


class KeyringDistribution(Distribution):
    def has_ext_modules(self):
        return True


if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))

    setup(
        version=get_version(root),
        cmdclass={
            "build_py": BuildKeyring,
            "bdist_wheel": BuildKeyringPlatformWheel,
        },
        distclass=KeyringDistribution,
    )
