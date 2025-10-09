"""Tools for parsing semantic release versions (strings)."""

import logging
import re
import time
from pathlib import Path
from typing import List, Tuple

import requests
from dateutil import parser

LOGGER = logging.getLogger(__name__)


########################################################################################
# BASIC SEMVER-PARSING TOOLS
########################################################################################

# NOTE: for security, limit the regex section lengths (with trusted input we'd use + and *)
# https://cwe.mitre.org/data/definitions/1333.html
RE_VERSION_X_Y_Z = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}$")
RE_VERSION_X_Y = re.compile(r"\d{1,3}\.\d{1,3}$")
RE_VERSION_X = re.compile(r"\d{1,3}$")

RE_VERSION_PREFIX_V = re.compile(r"(v|V)\d{1,3}(\.\d{1,3}(\.\d{1,3})?)?$")


def strip_v_prefix(docker_tag: str) -> str:
    """Remove the v-prefix for semver tags.

    Examples:
        v4     -> 4
        v5.1   -> 5.1
        v3.6.9 -> 3.6.9

        Also...
        6.0    -> 6.0
        vfoo   -> vfoo
    """
    if RE_VERSION_PREFIX_V.fullmatch(docker_tag):
        docker_tag = docker_tag.lstrip("vV")  # handle both 'v' and 'V'

    if not docker_tag or not docker_tag.strip():
        raise ValueError(docker_tag)

    return docker_tag


########################################################################################
# PYTHON VERSION TOOLS
########################################################################################


def get_latest_py3_release() -> Tuple[int, int]:
    """Return the latest python3 release version (supported by GitHub) as
    tuple."""
    url = "https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json"
    LOGGER.info(f"querying {url}")

    manifest = requests.get(url).json()
    manifest = [d for d in manifest if d["stable"]]  # only stable releases

    manifest = sorted(  # sort by version
        manifest,
        key=lambda d: [int(y) for y in d["version"].split(".")],
        reverse=True,
    )

    version = manifest[0]["version"]
    LOGGER.info(f"latest is {version}")

    return int(version.split(".")[0]), int(version.split(".")[1])


class PythonVersionNotFoundException(Exception):
    """Raised when a specific version of Python is not found."""


def get_python_eol_ts(python_version: str) -> float:
    """Return the end-of-life timestamp of a python version.

    See https://devguide.python.org/versions/ or https://endoflife.date/python
    """
    url = "https://endoflife.date/api/v1/products/python/"
    LOGGER.info(f"querying {url}")

    resp = requests.get(url).json()

    LOGGER.info(f"finding info on {python_version}")
    try:
        info = next(
            p for p in resp["result"]["releases"] if p["name"] == python_version
        )
    except StopIteration:
        raise PythonVersionNotFoundException(python_version)

    return parser.parse(info["eolFrom"]).timestamp()


def is_python_eol(python_version: str) -> bool:
    """Return whether this python version is end of life.

    See https://devguide.python.org/versions/ or https://endoflife.date/python
    """
    return time.time() > get_python_eol_ts(python_version)


########################################################################################
# PYTHON PROJECT TOOLS
########################################################################################


def list_all_majmin_versions(
    major: int,
    semver_range: str,
    max_minor: int = 99,
) -> List[Tuple[int, int]]:
    """Get a list of the matching major-minor versions for the semver range.

    Example:
        major: 3  semver_range: >=3.5.1,<3.9    max_minor: default  -> [3.6, 3.7, 3.8]
        major: 3  semver_range: >=3.5.1         max_minor: 8        -> [3.6, 3.7, 3.8]
        major: 3  semver_range: >=3,<3.6,!=3.3  max_minor: default  -> [3.0, 3.1, 3.2, 3.4, 3.5]
    """

    # import parsing package -- only used by this function
    try:
        import semantic_version  # type: ignore[import-untyped]
    except (ImportError, ModuleNotFoundError) as _exc:
        raise ImportError(
            "the 'semver' option must be installed in order to use 'semver_parser_tools'"
        ) from _exc

    # parse
    spec = semantic_version.SimpleSpec(semver_range.replace(" ", ""))

    # iterate
    filtered = spec.filter(
        semantic_version.Version(f"{major}.{i}.0") for i in range(max_minor + 1)
    )
    all_of_em = [(int(v.major), int(v.minor)) for v in filtered]

    LOGGER.info(f"matching major-minor versions: {all_of_em}")
    return all_of_em


def get_py_semver_range_for_project(project_dir: Path = Path(".")) -> str:
    """Get the semver range for a given project by parsing pyproject.toml or setup.cfg.

    Ex: ">=3.9,<3.11" or any other valid semver range expression
    """

    if (project_dir / "pyproject.toml").is_file():
        # ex: requires-python = ">=3.8, <3.13"
        # ex: requires-python  =  ">=3.9, <3.14"  # a comment
        pat = re.compile(r'requires-python\s*=\s*"(?P<semver_range>[^"]+)"(?:\s*#.*)?$')
        with open(project_dir / "pyproject.toml") as f:
            for line in f:
                if m := pat.match(line):
                    return m.group("semver_range").strip()
        raise Exception("could not find `requires-python` entry in pyproject.toml")

    if (project_dir / "setup.cfg").is_file():
        # ex: python_requires = >=3.8, <3.13
        # ex: python_requires  =  >=3.8, <3.13  # a comment
        pat = re.compile(r"python_requires\s*=\s*(?P<semver_range>[^#]+?)(?:\s*#.*)?$")
        with open(project_dir / "setup.cfg") as f:
            for line in f:
                if m := pat.match(line):
                    return m.group("semver_range").strip()
        raise Exception("could not find `python_requires` entry in setup.cfg")

    else:
        raise Exception("could not find pyproject.toml nor setup.cfg")
