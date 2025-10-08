import os

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            import re
            # Using SemVer Pattern
            PATTERN = r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
            match = re.search(PATTERN, line)
            if match is not None:
                return match.group()
            else:
                raise RuntimeError("Malformed version string")
    else:
        raise RuntimeError("Unable to find version string.")


setuptools.setup(
    version=get_version('src/colorls/__init__.py'),
    # packages=find_packages(where="src"),
    # package_dir={"": "src"},

)
