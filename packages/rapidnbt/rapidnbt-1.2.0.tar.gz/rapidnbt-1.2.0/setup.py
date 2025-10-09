import os
import shutil
import subprocess
from setuptools import Distribution, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py

PACKAGE_NAME = "rapidnbt"
EXTENSION_FILENAME = "_NBT"


class XMakeBuild(build_ext):
    def _clean(self):
        for root, _, files in os.walk(f"./{PACKAGE_NAME}"):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_path.endswith((".so", ".pyd")):
                    os.remove(file_path)

    def _copy_binary(self):
        shutil.copy(
            f"./build/bin/{EXTENSION_FILENAME}",
            os.path.join(
                f"./{PACKAGE_NAME}", self.get_ext_filename(EXTENSION_FILENAME)
            ),
        )

    def run(self):
        self._clean()
        subprocess.run(["xmake", "f", "--mode=release", "-y", "--root"], check=True)
        subprocess.run(["xmake", "--all", "-y", "--root"], check=True)
        self._copy_binary()


class XmakeDistribution(Distribution):
    def has_ext_modules(self):
        return True


class XmakeCommand(build_py):
    def run(self):
        self.run_command("build_ext")
        super().run()


setup(
    cmdclass={
        "build_ext": XMakeBuild,
        "build_py": XmakeCommand,
    },
    distclass=XmakeDistribution,
)
