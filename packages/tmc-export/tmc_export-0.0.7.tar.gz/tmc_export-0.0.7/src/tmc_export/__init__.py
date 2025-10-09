from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import enum
import io
import json
import logging
import os
import platform
import sys
import tempfile
import typing
import contextlib
from urllib.parse import urlparse
import urllib.request
import urllib.error
import zipfile
from textwrap import dedent
from packaging.version import parse as parse_version, Version
from packaging.specifiers import Specifier
from dataclasses import dataclass, field
from typing import (
    Any,
    Iterable,
    Literal,
    NamedTuple,
    Protocol,
    TextIO,
    TypedDict,
    Union,
)
from urllib.request import url2pathname, urlopen
import requests  # type:ignore
import yaml  # type:ignore
from typing_extensions import TypeAlias
import shutil

log = logging.getLogger("tmc_export")

IPlatform: TypeAlias = Literal["osx", "linux", "windows"]
IProcessor: TypeAlias = Literal["x", "arm"]

iurl: TypeAlias = str
iversion: TypeAlias = str

DATA_URL = os.environ.get(
    "TMC_EXPORT_DATA_URL",
    "https://gitlab.lam.fr/efisoft/efisoft_public/-/raw/main/data/tmc2fcs.json?ref_type=heads&inline=false",
)

HOME_DIR = os.environ.get("HOME", ".")
CONFIG_DIR = os.path.join(HOME_DIR, ".tmc_export")
TMC_BIN_NAME = "tmc2fcs_generator"
TPLS_FILE = "tpls.json"
PKG_SUBDIRECTORY = "packages"
GENERATOR_SUBDIRECTORY = "generators"
DEFAULT_MD_STYLE = "zenburn"
X64_PROC = "x"
ARM_PROC = "arm"


if sys.argv:
    PROG_NAME = os.path.basename(sys.argv[0])
else:
    PROG_NAME = "tmcExport"


class IRepoZipData(Protocol):
    def get_url(self) -> str: ...

    def get_target_file_name(self) -> str: ...

    def get_target_dir_name(self) -> str: ...


class BinaryType(enum.StrEnum):
    OSX = "osx"
    LINUX = "linux"
    WINDOW = "windows"


@dataclass
class UrlZipData:
    url: iurl
    target_dir: str | None = None

    def get_url(self) -> str:
        return self.url

    def get_target_file_name(self) -> str:
        *_, name = self.get_url().split("/")
        return name

    def get_target_dir_name(self) -> str:
        if self.target_dir:
            return self.target_dir
        *_, name = self.get_url().split("/")
        return name.removesuffix(".zip")


def download_zip(url: str, to: str) -> None:
    req = get_request(url)
    fd = io.BytesIO()
    for chunk in req.iter_content(chunk_size=128):
        fd.write(chunk)
    log.info("Unzip template package")
    with zipfile.ZipFile(fd, "r") as zip_ref:
        zip_ref.extractall(to)


class LocalFileAdapter(requests.adapters.BaseAdapter):  # type: ignore
    """Protocol Adapter to allow Requests to GET file:// URLs

    @todo: Properly handle non-empty hostname portions.
    """

    @staticmethod
    def _chkpath(method: str, path: str) -> tuple[int, str]:
        """Return an HTTP status for the given filesystem path."""
        if method.lower() in ("put", "delete"):
            return 501, "Not Implemented"  # TODO
        elif method.lower() not in ("get", "head"):
            return 405, "Method Not Allowed"
        elif os.path.isdir(path):
            return 400, "Path Not A File"
        elif not os.path.isfile(path):
            return 404, "File Not Found"
        elif not os.access(path, os.R_OK):
            return 403, "Access Denied"
        else:
            return 200, "OK"

    def send(self, req: requests.PreparedRequest, **kwargs: Any) -> requests.Response:
        """Return the file specified by the given request

        @type req: C{PreparedRequest}
        @todo: Should I bother filling `response.headers` and processing
               If-Modified-Since and friends using `os.stat`?
        """
        path = os.path.normcase(os.path.normpath(url2pathname(req.path_url)))
        response = requests.Response()

        response.status_code, response.reason = self._chkpath(str(req.method), path)
        if response.status_code == 200 and str(req.method).lower() != "head":
            try:
                response.raw = open(path, "rb")
            except (OSError, IOError) as err:
                response.status_code = 500
                response.reason = str(err)

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = str(req.url)

        response.request = req
        response.connection = self

        return response

    def close(self) -> None:
        pass


def get_request(url: str) -> requests.Response:
    requests_session = requests.session()
    requests_session.mount("file://", LocalFileAdapter())
    return requests_session.get(url, stream=True)


########################################


class _IDictTemplateDependenciesData(TypedDict):
    package: str
    templates: list[str]
    version: str


@dataclass
class TemplateDependencyInfo:
    package: str
    version: Specifier
    templates: list[str] = field(default_factory=list)

    @classmethod
    def from_data(cls, data: _IDictTemplateDependenciesData) -> TemplateDependencyInfo:
        return cls(
            package=data["package"],
            version=Specifier(data["version"]),
            templates=list(data["templates"]),
        )


class _IDictTplInfoData(TypedDict):
    """Template Informations as it should appears in template sources json file"""

    include_dirs: list[str]
    template_dir: str
    pre_init: str
    post_init: str
    dependencies: list[_IDictTemplateDependenciesData]
    post_process: str | None
    description_file: str | None
    parameters_file: str | None


@dataclass
class TemplateInfo:
    """Parsed template information"""

    package: str
    name: str
    path: str
    template_dir: str
    include_dirs: list[str] = field(default_factory=list)
    pre_init: str = ""
    post_init: str = ""
    dependencies: list[TemplateDependencyInfo] = field(default_factory=list)
    post_process: str | None = None
    description_file: str | None = None
    parameters_file: str | None = None
    relative_path: str = "."

    @classmethod
    def from_data(
        cls,
        path: str,
        source: str,
        name: str,
        data: _IDictTplInfoData,
        relative_path: str = ".",
    ) -> TemplateInfo:
        return cls(
            source,
            name,
            path,
            template_dir=data["template_dir"],
            include_dirs=data["include_dirs"],
            pre_init=data["pre_init"],
            post_init=data["post_init"],
            dependencies=[
                TemplateDependencyInfo.from_data(d) for d in data["dependencies"]
            ],
            post_process=data.get("post_process", None),
            description_file=data.get("description_file", None),
            parameters_file=data.get("parameters_file", None),
            relative_path=relative_path,
        )

    @classmethod
    def from_file(cls, file: str, source: str, name: str) -> TemplateInfo:
        path, _ = os.path.split(file)
        with open(file) as f:
            data = json.load(f)
        return cls.from_data(path, source, name, data)

    def get_description(self, packages: InstalledPackages, short: bool = False) -> str:
        if not self.description_file:
            if short:
                return ""
            return f"template {self.name!r} in package {self.package!r}. No description"
        with open(os.path.join(self.path, self.description_file)) as f:
            if short:
                return f.readline()
            else:
                content = f.read()
                if "__PARAMETERS__" in content:
                    content = content.replace(
                        "__PARAMETERS__", self.dump_parameters_md(packages, True)
                    )
                return content

    def dump_parameters_md(
        self, packages: InstalledPackages, isroot: bool = False
    ) -> str:
        txt = []
        parameters = self.get_parameters()

        if not isroot:
            if len(parameters):
                txt.append(f"### from {self.name} (pkg {self.package})")
        txt.append(parameters.dump_md())

        for dep in reversed(self.dependencies):
            if dep.package == ".":
                pkg = packages.get_package(self.package)
            else:
                pkg = packages.get_package(dep.package)
            for tplname in dep.templates:
                tpl = pkg.get_template(tplname)
                txt.append(tpl.dump_parameters_md(packages))
        return "\n\n".join(txt)

    def get_parameters(self) -> TemplateParameters:
        if self.parameters_file is None:
            return TemplateParameters()
        with open(os.path.join(self.path, self.parameters_file)) as f:
            data = yaml.load(f, yaml.CLoader)
        return TemplateParameters.from_data(data)


class _IDictTemplateParameter(TypedDict):
    type: str
    description: str
    default: str


@dataclass
class TemplateParameter:
    name: str
    type_: str = ""
    description: str = ""
    default: str = ""

    @classmethod
    def from_data(cls, name: str, data: _IDictTemplateParameter) -> TemplateParameter:
        return cls(
            name,
            type_=data.get("type", ""),
            description=data.get("description", ""),
            default=data.get("default", ""),
        )

    def dump_md(self) -> str:

        txt = [
            f"- `{self.name}` ({self.type_})  ",
        ]
        if self.default:
            txt.append(f"  > default: `{self.default}`   \n  ")
        if self.description:
            txt.append("  " + ("\n  ".join(self.description.split("\n"))) + "\n>")
        return "\n".join(txt)


@dataclass
class TemplateParameters:
    parameters: dict[str, TemplateParameter] = field(default_factory=dict)

    @classmethod
    def from_data(cls, data: dict[str, _IDictTemplateParameter]) -> TemplateParameters:
        return cls({n: TemplateParameter.from_data(n, d) for n, d in data.items()})

    def dump_md(self) -> str:
        return "\n".join(p.dump_md() for p in self.parameters.values())

    def __len__(self) -> int:
        return len(self.parameters)


class _IDictPackageInfoData(TypedDict):
    generator: str
    version: str
    name: str
    templates: dict[str, _IDictTplInfoData | str]


@dataclass
class PackageInfo:
    path: str
    name: str
    version: Version
    generator: Specifier
    templates: dict[str, TemplateInfo] = field(default_factory=dict)

    @classmethod
    def from_data(cls, path: str, data: _IDictPackageInfoData) -> PackageInfo:
        pkg_name = data["name"]
        tpls = {}
        for n, tpl_data in data["templates"].items():
            if isinstance(tpl_data, str):
                tpls[n] = TemplateInfo.from_file(
                    os.path.join(path, tpl_data), pkg_name, n
                )
            else:
                tpls[n] = TemplateInfo.from_data(path, pkg_name, n, tpl_data)
        return cls(
            path=path,
            name=pkg_name,
            version=parse_version(data["version"]),
            generator=Specifier(data["generator"]),
            templates=tpls,
        )

    def get_template(self, tplname: str) -> TemplateInfo:
        try:
            return self.templates[tplname]
        except KeyError:
            raise ValueError(f"Unknown template {tplname!r} in package {self.name!r}")


@dataclass
class InstalledPackages:
    _packages: dict[str, PackageInfo] = field(default_factory=dict)

    def add_package(self, path: str) -> None:
        with open(os.path.join(path, TPLS_FILE)) as f:
            raw = typing.cast(_IDictPackageInfoData, json.load(f))
        pkg_info = PackageInfo.from_data(path, raw)
        self._packages[pkg_info.name] = pkg_info

    def add_all_subdirectories(self, localdir: str) -> None:
        subdirs = [os.path.join(localdir, s) for s in os.listdir(localdir)]
        for subdir in subdirs:
            if os.path.exists(os.path.join(subdir, TPLS_FILE)):
                self.add_package(subdir)

    def has_package(self, name: str, version: Specifier | None = None) -> bool:
        if version is None:
            return name in self._packages
        if name in self._packages:
            return bool(version.contains(self._packages[name].version))
        return False

    def get_package(self, name: str) -> PackageInfo:
        return self._packages[name]

    def iter_packages(self) -> Iterable[tuple[str, PackageInfo]]:
        yield from self._packages.items()


@dataclass
class InstalledTemplates:
    """A collection of information on installed templates"""

    _templates: dict[str, TemplateInfo] = field(default_factory=dict)

    def add_from_package(self, pkg_info: PackageInfo) -> None:
        for name, tpl in pkg_info.templates.items():
            self._templates[name] = tpl

    def get_template(self, tplname: str) -> TemplateInfo:
        try:
            return self._templates[tplname]
        except KeyError:
            raise ValueError(
                f"Unknown template {tplname!r} \n"
                f"You can install package with `{PROG_NAME} install package NAME`"
            )

    def has_template(self, tplname: str) -> bool:
        return tplname in self._templates

    def iter_templates(self) -> Iterable[tuple[str, TemplateInfo]]:
        yield from self._templates.items()


@dataclass
class GeneratorInfo:
    """Generator parsed information"""

    local_dir: str
    version: Version
    platform: IPlatform

    @property
    def binary(self) -> str:
        return os.path.join(self.local_dir, TMC_BIN_NAME)

    @property
    def dll(self) -> str:
        return os.path.join(self.local_dir, TMC_BIN_NAME + ".dll")

    @classmethod
    def from_dir_name(cls, dirname: str) -> GeneratorInfo:
        """Read information from generator directory.

        Not ideal. TODO: Would be great to have these info in the zip file
        """
        _, version_str, platform_s, *_ = os.path.basename(dirname).split("-")

        if platform_s.startswith("osx"):
            platform: IPlatform = "osx"
        elif platform_s.startswith("linux"):
            platform = "linux"
        elif platform_s.startswith("win"):
            platform = "windows"
        else:
            raise ValueError(f"Cannot read platform from {dirname}")
        return cls(
            dirname,
            version=parse_version(version_str),
            platform=platform,
        )


@dataclass
class InstalledGenerators:
    """A collection of installed generators

    They are unique per couple of version and platform
    """

    generators: dict[tuple[Version, IPlatform], GeneratorInfo] = field(
        default_factory=dict
    )

    def add_directory(self, dirname: str) -> None:
        """Add a generator from its directory"""
        gen_info = GeneratorInfo.from_dir_name(dirname)
        self.generators[(gen_info.version, gen_info.platform)] = gen_info

    def add_all_subdirectories(self, localdir: str) -> None:
        """Add all generators located in a directory (non-recursive)"""
        subdirs = [os.path.join(localdir, s) for s in os.listdir(localdir)]
        for subdir in subdirs:
            # TODO: not idesl
            if os.path.basename(subdir).startswith("tmc2fcs_generator"):
                self.add_directory(subdir)

    def has_generator(self, version: Version | Specifier, platform: IPlatform) -> bool:
        """return true if the generator is installed"""
        if isinstance(version, Version):
            return (version, platform) in self.generators
        else:
            for v, p in self.generators:
                if version.contains(v):
                    return True
        return False

    def get_generator_info(
        self, version: Specifier, platform_s: IPlatform | None = None
    ) -> GeneratorInfo:
        """For a version and platform, return Generator information"""
        good_versions = set()
        if platform_s is None:
            platform_s = find_platform()
        for v, p in self.generators:
            if p == platform_s:
                if version.contains(v):
                    good_versions.add(v)
        if not good_versions:
            raise ValueError(
                f"Cannot find installed generator satifying {version} for {platform!r}"
            )
        most_recent = max(good_versions)
        return self.generators[(most_recent, platform_s)]

    def iter_generators(
        self,
    ) -> Iterable[tuple[tuple[Version, IPlatform], GeneratorInfo]]:
        yield from self.generators.items()


@dataclass
class ProgramResources:
    """Collection of all program resources

    Include templates, generators and the .Net binary
    """

    packages: InstalledPackages = field(default_factory=InstalledPackages)
    templates: InstalledTemplates = field(default_factory=InstalledTemplates)
    generators: InstalledGenerators = field(default_factory=InstalledGenerators)
    dotnet_binary: str | None = None
    root: str = CONFIG_DIR

    def update(self) -> None:
        """Update the resources by looking inside the root directory

        On Linux, this will also install .Netif necessary
        """

        self.packages.add_all_subdirectories(_make_tree(self.root, PKG_SUBDIRECTORY))
        for _, pkg in self.packages.iter_packages():
            self.templates.add_from_package(pkg)
        self.generators.add_all_subdirectories(
            _make_tree(self.root, GENERATOR_SUBDIRECTORY)
        )
        self.dotnet_binary = DotNetInstaller(self.root).get_dotnet_binary()

    def get_template_description(self, tplname: str, short: bool = False) -> str:
        tpl = self.templates.get_template(tplname)
        return tpl.get_description(self.packages, short)


########################################
# Package Data, as receive by the template/generator package manager


_IDictPlatformData = TypedDict(
    "_IDictPlatformData",
    {"osx": str, "linux": str, "windows": str, "osx-arm": str, "linux-arm": str},
)


@dataclass
class GeneratorData:
    """Parsed generator data"""

    osx: UrlZipData
    linux: UrlZipData
    windows: UrlZipData
    osx_arm: UrlZipData | None = None
    linux_arm: UrlZipData | None = None

    @classmethod
    def from_dict(cls, d: _IDictPlatformData) -> GeneratorData:
        if "osx-arm" in d:
            osx_arm = UrlZipData(d["osx-arm"])
        else:
            osx_arm = None

        if "linux-arm" in d:
            linux_arm = UrlZipData(d["linux-arm"])
        else:
            linux_arm = None

        return cls(
            osx=UrlZipData(d["osx"]),
            linux=UrlZipData(d["linux"]),
            windows=UrlZipData(d["windows"]),
            osx_arm=osx_arm,
            linux_arm=linux_arm,
        )

    def get_url_zip(self, platform: IPlatform, processor: IProcessor) -> IRepoZipData:
        match platform:
            case "osx":
                if processor == X64_PROC:
                    return self.osx
                else:
                    if self.osx_arm is None:
                        raise ValueError("No osx arm generator for this version")
                    return self.osx_arm
            case "linux":
                if processor == X64_PROC:
                    return self.linux
                else:
                    if self.linux_arm is None:
                        raise ValueError("No osx arm generator for this version")
                    return self.linux_arm

            case "windows":
                return self.windows
        raise ValueError(f"Unknown platform {platform!r}")


class _IDictTemplateSourceData(TypedDict):
    name: str
    url: str


@dataclass
class TemplateSourceData:
    name: str
    url: IRepoZipData

    @classmethod
    def from_dict(cls, data: _IDictTemplateSourceData) -> TemplateSourceData:
        return cls(
            name=data["name"],
            url=UrlZipData(data["url"]),
        )


class _IDictPkgData(TypedDict):
    """Schema of the Package json data file dictionary"""

    generator: dict[str, _IDictPlatformData]  # per version
    template_packages: dict[str, dict[str, str]]  # id / (version/url)


def download_pkg_data() -> _IDictPkgData:
    """Download data containing package urls per asset"""
    with urllib.request.urlopen(DATA_URL) as f:
        data = json.load(f)
    return typing.cast(_IDictPkgData, data)


def read_pkg_data() -> _IDictPkgData:
    file = os.path.join(CONFIG_DIR, "data", "tmc2fcs.json")

    if os.path.exists(file):
        with open(file) as f:
            return typing.cast(_IDictPkgData, json.load(f))
    raise ValueError(f"Offline work. No cached data {file}")


def template_packages_from_data(
    data: dict[str, dict[str, str]],
) -> dict[str, dict[Version, IRepoZipData]]:
    return {
        name: {parse_version(v): UrlZipData(u) for v, u in subdata.items()}
        for name, subdata in data.items()
    }


@dataclass
class PkgData:
    """Parsed Package Data"""

    template_packages: dict[str, dict[Version, IRepoZipData]]
    generators: dict[Version, GeneratorData]

    @classmethod
    def from_dict(cls, data: _IDictPkgData) -> PkgData:
        return cls(
            template_packages=template_packages_from_data(data["template_packages"]),
            generators={
                parse_version(v): GeneratorData.from_dict(d)
                for v, d in data["generator"].items()
            },
        )


class PkgManager:
    _data: PkgData | None = None

    def get_data(self) -> PkgData:
        """Provide the package data. Download it the first time"""
        if self._data is None:
            try:
                raw_data = download_pkg_data()
            except urllib.error.URLError:
                log.error("Connection failed to template package server failed")
                raise RuntimeError(
                    "Connection failed to template package server failed"
                )
            self._data = PkgData.from_dict(raw_data)
        return self._data

    def iter_generators(self) -> Iterable[tuple[Version, GeneratorData]]:
        yield from self.get_data().generators.items()

    def iter_packages(self) -> Iterable[tuple[str, dict[Version, IRepoZipData]]]:
        yield from self.get_data().template_packages.items()

    def get_generator_url_zip(
        self, version: Version, platform: IPlatform, processor: IProcessor
    ) -> IRepoZipData:
        try:
            return self.get_data().generators[version].get_url_zip(platform, processor)
        except (KeyError, ValueError):
            raise ValueError(
                f"Generator version {version} for {platform} {processor} is not available. "
                f"You can install a Generator with '{PROG_NAME} install generator'"
            )

    def get_package_versions(self, package: str) -> dict[Version, IRepoZipData]:
        try:
            return self.get_data().template_packages[package]
        except KeyError:
            raise ValueError(f"Unknown resource name  {package!r}")

    def get_package_data(
        self, package: str, version: Version | None = None
    ) -> IRepoZipData:
        package_versions = self.get_package_versions(package)
        if version is None:
            version = max(package_versions)
        return package_versions[version]

    def get_most_recent_package_version(self, package: str) -> Version:
        return max(self.get_package_versions(package))

    def resolve_package_version(
        self, package: str, version: Specifier, prereleases: bool | None = None
    ) -> Version:
        pckgs = {
            v: p
            for v, p in self.get_package_versions(package).items()
            if version.contains(v, prereleases)
        }
        if pckgs:
            most_recent = max(pckgs)
            return most_recent
        raise ValueError(f"Cannnot find package {package!r} that satisfy {version}")

    def resolve_generator_version(
        self, version: Specifier, prereleases: bool | None = None
    ) -> Version:
        good_versions = [
            v
            for v, g in self.get_data().generators.items()
            if version.contains(v, prereleases)
        ]
        if not good_versions:
            raise ValueError(f"Cannot found generator stisfying {version}")
        most_recent = max(good_versions)
        return most_recent

    def install_generator(
        self, root: str, version: Version, platform: IPlatform, processor: IProcessor
    ) -> None:
        url = self.get_generator_url_zip(version, platform, processor)
        GeneratorDownloader(
            repo=url,
            root=os.path.join(root, GENERATOR_SUBDIRECTORY),
            overrides=True,
        ).download()

    def install_package(self, root: str, pckgname: str, version: Version) -> None:
        url_zip = self.get_package_data(pckgname, version)
        with tempfile.TemporaryDirectory() as tmpdirname:
            TemplatePackageDownloader(
                repo=url_zip,
                root=tmpdirname,
                overrides=True,
            ).download()
            # Try to include all products if no error is raised we can
            # copy everything to the root/template directory
            tmp = InstalledPackages()
            tmp.add_all_subdirectories(tmpdirname)
            for name, pkg in tmp.iter_packages():

                installation_dir = os.path.join(root, PKG_SUBDIRECTORY, pkg.name)
                if os.path.exists(installation_dir):
                    shutil.rmtree(installation_dir)

                shutil.copytree(
                    pkg.path,
                    installation_dir,
                    dirs_exist_ok=True,
                )
                log.info(
                    f"Package {pckgname} installed to {os.path.join(root, PKG_SUBDIRECTORY, pkg.name)}"
                )

    def install_local_package(self, root: str, pkg_dir: str) -> None:
        tmp = InstalledPackages()
        tmp.add_package(pkg_dir)
        for name, pkg_info in tmp.iter_packages():
            log.info(f"package {name!r} {pkg_info.version} installed from {pkg_dir!r}")

            installation_dir = os.path.join(root, PKG_SUBDIRECTORY, name)
            if os.path.exists(installation_dir):
                shutil.rmtree(installation_dir)

            shutil.copytree(
                pkg_dir,
                installation_dir,
                dirs_exist_ok=True,
            )


@dataclass
class TemplatePackageInstaller:
    pkg_mgr: PkgManager = field(default_factory=PkgManager)
    resources: ProgramResources = field(default_factory=ProgramResources)

    def install(
        self,
        pkgname: str,
        version_spcifier: Specifier = Specifier(">0"),
        force: bool = False,
    ) -> None:
        if os.path.exists(pkgname) and os.path.isdir(pkgname):
            self.install_local(pkgname)
        else:
            self.install_remote(pkgname, version_spcifier, force=force)

    def install_remote(
        self,
        pkgname: str,
        version_spcifier: Specifier = Specifier(">0"),
        force: bool = False,
    ) -> None:

        if not force and self.resources.packages.has_package(pkgname):
            pkg_info = self.resources.packages.get_package(pkgname)
            if version_spcifier.contains(pkg_info.version):
                log.info(
                    f"Package {pkgname!r} already installed and satisfy {version_spcifier}"
                )
                return

        version = self.pkg_mgr.resolve_package_version(pkgname, version_spcifier)
        log.info(f"Installing package {pkgname!r} {version}")
        self.pkg_mgr.install_package(self.resources.root, pkgname, version)

        self.resources.update()
        self.check_generators()
        self.check_dependencies()

    def install_local(self, pkgdir: str) -> None:

        log.info(f"Installing local package from {pkgdir!r} ")
        self.pkg_mgr.install_local_package(self.resources.root, pkgdir)
        self.resources.update()
        self.check_generators()
        self.check_dependencies()

    def check_generators(self) -> None:
        """Check if all generators are installed for the installed packages"""
        platform = find_platform()
        processor = find_processor()
        installed = False
        for name, pkg in self.resources.packages.iter_packages():
            if not self.resources.generators.has_generator(pkg.generator, platform):
                version = self.pkg_mgr.resolve_generator_version(pkg.generator)
                log.info(
                    f"Installing generator {version} for {platform!r}. Needed by {name}"
                )
                self.pkg_mgr.install_generator(
                    self.resources.root, version, platform, processor
                )
                installed = True
        if installed:
            self.resources.update()

    def check_dependencies(self) -> None:
        for name, tpl in self.resources.templates.iter_templates():
            for dependency in tpl.dependencies:
                pkg = dependency.package
                if pkg == ".":
                    pkg = tpl.package
                if not self.resources.packages.has_package(pkg, dependency.version):
                    log.info(
                        f"Installing package {pkg!r} needed by template {name!r} in package {tpl.package!r}"
                    )
                    self.install(pkg, dependency.version)


########################################
@dataclass
class GeneratorDownloader:
    repo: IRepoZipData
    root: str = os.path.join(CONFIG_DIR, GENERATOR_SUBDIRECTORY)
    overrides: bool = False

    def download(self) -> str:

        log = logging.getLogger("tmc_export")
        log.info("Installing/Checking tmc2fcf Generator")
        generator_path = _make_tree(self.root)
        target_dir = os.path.join(generator_path, self.repo.get_target_dir_name())
        bin_path = os.path.join(target_dir, TMC_BIN_NAME)

        log.info(f"generator root path : {target_dir}")

        if os.path.exists(bin_path) and not self.overrides:
            log.info(f"{bin_path} Already exists, all good")
            return bin_path

        url = self.repo.get_url()
        log.info(f"Download generator at {url}")
        download_zip(url, target_dir)

        log.info(f"Set {bin_path!r} as executable")
        os.chmod(bin_path, 0o755)
        return bin_path


@dataclass
class TemplatePackageDownloader:
    """Helper to download a Template from its zip url"""

    repo: IRepoZipData
    root: str = os.path.join(CONFIG_DIR, PKG_SUBDIRECTORY)
    overrides: bool = False

    # def download_into(self, template_infos: TemplateInfoGroup) -> None:
    #     template_infos.update(self.download().get_templates())

    def download(self) -> str:
        log.info("Installation/Check of tmc2fcs Templates")
        template_path = _make_tree(self.root)
        target_dir = os.path.join(template_path, self.repo.get_target_dir_name())

        if os.path.exists(target_dir) and not self.overrides:
            log.info(f"Template package already exists at {target_dir}")
            return target_dir

        log.info(f"Downloading template package from {self.repo.get_url()} ...")

        url = self.repo.get_url()
        download_zip(url, template_path)
        log.debug(f"Template package installed in {target_dir!r}")
        return target_dir


def get_dotnet_version(dotnet_path: str) -> Version:
    proc = subprocess.run([dotnet_path, "--info"], stdout=subprocess.PIPE)
    info = proc.stdout.decode()

    if rematch := re.search(r"Version\s*[:]\s*([0-9.]*)", info):
        return parse_version(rematch.group(1))
    raise ValueError(f"Bug: Cannot read Dotnet version of {dotnet_path}")


@dataclass
class DotNetInstaller:
    root: str = CONFIG_DIR
    script_url: str = "https://dot.net/v1/dotnet-install.sh"
    force: bool = False
    explicit: bool = False  # True if we explicitly want to install .net
    version_spec: Specifier = Specifier(">=8.0.0")
    channel: str = "8.0"

    def get_dotnet_root(self) -> str:
        if (root := os.environ.get("DOTNET_ROOT", None)) is not None:
            return root
        local_dotnet = os.path.join(self.root, "dotnet")
        local_bin = os.path.join(local_dotnet, "dotnet")
        if os.path.exists(local_bin):
            if self.version_spec.contains(get_dotnet_version(local_bin)):
                return local_dotnet

        local_dotnet = os.path.join(os.environ.get("HOME", "__dummy__"), ".dotnet")
        local_bin = os.path.join(local_dotnet, "dotnet")
        if os.path.exists(local_bin):
            if self.version_spec.contains(get_dotnet_version(local_bin)):
                return local_dotnet

        platform = find_platform()

        match platform:
            case "osx":
                options = [
                    "/usr/local/share/dotnet/x64",
                    "/usr/local/share/dotnet",
                ]
            case "windows":
                options = [
                    r"C:\Program Files\dotnet\x64",
                    r"C:\Program Files\dotnet",
                ]
            case "linux":
                options = [
                    "/usr/share/dotnet",
                    "/usr/lib/dotnet",
                ]
            case _:
                options = []
        for option in options:
            binary = os.path.join(option, "dotnet")
            if os.path.exists(binary):
                log.debug(
                    f"found dotnet in {binary} verions {get_dotnet_version(binary)}"
                )
                if self.version_spec.contains(get_dotnet_version(binary)):
                    log.debug(f"version {self.version_spec} satisfied")
                    return option
        return ""

    def set_dotnet_root_environ(self) -> None:
        """Set the DOTNET_ROOT environment variable to a dotnet pkg found"""
        root = self.get_dotnet_root()
        if root:
            os.environ["DOTNET_ROOT"] = root

    def get_dotnet_binary(self) -> str | None:
        dotnet_root = self.get_dotnet_root()
        if dotnet_root:
            return os.path.join(dotnet_root, "dotnet")
        return None

    def install(self) -> str | None:
        if platform.system() not in ["Linux", "Darwin"]:
            if self.explicit:
                log.error(
                    "DotNet can only be installed dynamically on linux or osx platform. "
                    "Please install .net manually"
                )
            return None

        dotnet_binary = self.get_dotnet_binary()

        if dotnet_binary:
            if not self.force and get_dotnet_version(dotnet_binary) >= parse_version(
                "8.0.0"
            ):
                log.info(f"Dotnet binary already installed at {dotnet_binary}")
                return dotnet_binary

        dotnet_install_script = os.path.join(_make_tree(self.root), "dotnet-install.sh")

        req = get_request(self.script_url)
        with open(dotnet_install_script, "wb") as fd:
            for chunk in req.iter_content(chunk_size=128):
                fd.write(chunk)

        os.chmod(dotnet_install_script, 0o755)
        install_dir = _make_tree(self.root, "dotnet")

        os.system(
            f"{dotnet_install_script} --channel {self.channel}  --runtime dotnet --install-dir {install_dir}"
        )
        return self.get_dotnet_binary()


@dataclass
class TemplateConfig:
    name: str
    data: dict[str, Any] = field(default_factory=dict)
    scriban: str | None = None
    global_data: TemplateConfig | None = None

    def append_yaml(self, file: str | TextIO) -> None:
        if isinstance(file, str):
            file = open(file)
        data: dict[str, Any] | str = yaml.load(file, yaml.CLoader)
        if not isinstance(data, (dict, str)):
            raise ValueError(
                f"Receive a {type(data)} object expecting a dict or string"
            )
        self.append_data(data)

    def append_data(self, data: dict[str, Any] | str) -> None:
        if isinstance(data, str):
            self.scriban = data
        else:
            self.data.update(data)

    def export_to_scriban_list(self) -> list[str]:
        scribans = []
        if self.global_data is not None:
            scribans.extend(self.global_data.export_to_scriban_list())
        scribans.append(f"# ------ {self.name} Config ------")
        if self.scriban:
            scribans.append(self.scriban)
        scribans.extend(_parse_dictionary_content_to_scriban_list(self.data))
        return scribans

    def export_to_scriban(self) -> str:
        return "{{~\n" + ("\n".join(self.export_to_scriban_list())) + "\n~}}\n"


@dataclass
class ConfigsData:
    data: dict[str, TemplateConfig] = field(default_factory=dict)

    def append_yaml(self, file: str | TextIO | io.BytesIO) -> None:
        if isinstance(file, str):
            url = urlparse(file)
            if url.scheme:
                req = get_request(file)
                file = io.BytesIO(req.content)
            else:
                file = open(file)
        data: dict[str, Any] = yaml.load(file, yaml.CLoader)
        self.append_data(data)

    def append_data(self, data: dict[str, dict[str, Any]]) -> None:
        for key, subdata in data.items():
            self.append_template_data(key, subdata)

    def append_template_data(self, key: str, tdata: dict[str, Any] | str) -> None:
        if not isinstance(tdata, (dict, str)):
            raise ValueError(f"Invalid config data for key {key!r}")
        self.data.setdefault(key, TemplateConfig(key)).append_data(tdata)

    def export_to_scriban_list(self, key: str) -> list[str]:
        if key in self.data:
            return self.data[key].export_to_scriban_list()
        return []
        # return self.global_data.export_to_scriban_list()

    def export_to_scriban(self, key: str) -> str:
        if key in self.data:
            return self.data[key].export_to_scriban()
        return "{{~ #" + key + " ~}}\n"
        # return self.global_data.export_to_scriban()


class _IDictModelData(TypedDict):
    """ """

    name: str
    extraction_root: str
    tmc_file: str | None
    scxml_file: str | None
    templates: list[str]
    outputs: dict[str, str]
    configs: dict[str, dict[str, Any]]
    model: dict[str, Any] | None


@dataclass
class DeviceModelData:
    name: str
    extraction_root: str | None
    tmc_file: str | None = None
    scxml_file: str | None = None
    templates: list[str] = field(default_factory=list)
    outputs: dict[str, str] = field(default_factory=dict)
    configs: ConfigsData = field(default_factory=ConfigsData)
    model: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.tmc_file:
            if self.model is None:
                raise ValueError("Please provide a tmc_file or define a model")
        # elif self.model is not None:
        #     raise ValueError("tmc_file and model cannot be both set")

    @classmethod
    def from_yaml(cls, file: str | TextIO) -> DeviceModelData:
        if isinstance(file, str):
            url = urlparse(file)
            if url.scheme:
                req = get_request(file)
                stream: io.BytesIO | TextIO = io.BytesIO(req.content)
            else:
                stream = open(file)
        else:
            stream = file
        data: dict[str, Any] = yaml.load(stream, yaml.CLoader)
        return cls.from_data(data)

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> DeviceModelData:
        data = data.copy()

        configs = ConfigsData()

        if "config_includes" in data:
            for inc in data.pop("config_includes"):
                configs.append_yaml(inc)

        if "configs" in data:
            configs.append_data(data.pop("configs"))

        if "tmc_file" not in data:
            data["tmc_file"] = ""

        return cls(**data, configs=configs)

    def get_scriban_model(self) -> str:
        if self.model is not None:
            return Model.from_dict(self.model).export_to_scriban()
        else:
            return ""

    def get_scriban_config(self, template_name: str) -> str:
        return self.configs.export_to_scriban(template_name)


def _parse_scriban_or_dict_to_scriban(data: dict[str, Any] | str) -> str:
    if isinstance(data, dict):
        cfg = _parse_dictionary_content_to_scriban(data)
    else:
        cfg = _parse_scribane_to_scriban(data)
    return cfg


def _parse_scribane_to_scriban(scriban: str) -> str:
    return "{{~" + scriban.strip(" \n").removeprefix("{{~").removesuffix("~}}") + "~}}"


def _walk_inludes(
    resources: ProgramResources, tpl_info: TemplateInfo, included: set[str]
) -> None:
    for inc in tpl_info.include_dirs:
        # pckg = resources.packages.get_package(tpl_info.package)
        path = os.path.join(tpl_info.path, inc)
        included.add(path)
    for dependency in tpl_info.dependencies:

        if dependency.package == ".":
            pkg = resources.packages.get_package(tpl_info.package)
        else:
            pkg = resources.packages.get_package(dependency.package)

        for tpl in dependency.templates:
            _walk_inludes(resources, pkg.get_template(tpl), included)


class TmpDirectory:
    def __init__(self, directory: None | str = None):
        self.directory = directory
        self._context: tempfile.TemporaryDirectory[Any] | None = None

    def __enter__(self) -> str:
        if self.directory is None:
            self._context = tempfile.TemporaryDirectory()
            return self._context.__enter__()
        else:
            return _make_tree(self.directory)

    def __exit__(self, *exc: Any) -> Literal[False]:
        if self._context:
            self._context.__exit__(*exc)
        return False


def recursive_write_config(
    g: typing.TextIO, configs: ConfigsData, resources: ProgramResources, tplname: str
) -> None:
    tpl_info = resources.templates.get_template(tplname)
    for dep_info in tpl_info.dependencies:
        for dep_tpl in dep_info.templates:
            recursive_write_config(g, configs, resources, dep_tpl)
    if tplname in configs.data:
        g.write(configs.export_to_scriban(tplname))


@dataclass
class TemplateExecutor:
    tpl_info: TemplateInfo
    gen_info: GeneratorInfo
    model_data: DeviceModelData
    resources: ProgramResources
    output_dir: str = "."
    debug: bool = False
    dry: bool = False
    tmpdir: str | None = None
    garbage_files: tuple[str, ...] = ("GenerationTrace.txt", ".info.gen")

    def build_command(self, dirname: str) -> list[str]:

        if self.resources.dotnet_binary is None:
            opts = [self.gen_info.binary]
        else:
            opts = [self.resources.dotnet_binary, self.gen_info.dll]

        if not self.model_data.tmc_file:
            if self.gen_info.version < parse_version("0.8.0"):
                raise ValueError("No tmc file is only suported for generator v>8.0.0")
        else:
            opts.extend(
                [
                    "-t",
                    self.get_tmc_file(dirname),
                ]
            )

        opts.extend(
            [
                "-o",
                self.output_dir,
                "--tpl",
                os.path.join(self.tpl_info.path, self.tpl_info.template_dir),
            ]
        )

        included_dirs: set[str] = set()
        _walk_inludes(self.resources, self.tpl_info, included_dirs)
        for inc in included_dirs:
            opts.extend(("-I", inc))

        if self.gen_info.version < parse_version("0.8.0"):
            opts.extend(["-d", self.model_data.name, "-I", dirname])
        else:
            opts.extend(("-I", dirname))
            opts.extend(("-p", self.get_proc_file(dirname)))

        if self.model_data.extraction_root:
            opts.extend(("-e", self.model_data.extraction_root))

        if self.model_data.scxml_file:
            opts.extend(("-s", self.get_xml_file(dirname)))

        return opts

    def get_proc_file(self, dirname: str) -> str:
        if self.gen_info.version < parse_version("0.8.0"):
            return os.path.join(dirname, self.model_data.name.lower() + ".sbn")
        else:
            return os.path.join(dirname, self.model_data.name.lower() + "_process.sbn")

    def write_legacy_proc_file(self, dirname: str) -> None:
        with open(self.get_proc_file(dirname), "w") as g:
            # for include_file in self.model_data.includes:
            #     log.info(f"Including file content: {include_file}")
            #     g.write(read_scriban_compatible_file(include_file))
            #     g.write("\n")
            g.write("{{~ Name = '" + self.model_data.name + "' ~}}\n")
            g.write("{{~ TemplateName = '" + self.tpl_info.name + "' ~}}\n")
            if "global" in self.model_data.configs.data:
                g.write(self.model_data.configs.export_to_scriban("global"))
            recursive_write_config(
                g, self.model_data.configs, self.resources, self.tpl_info.name
            )

            if self.model_data.model:
                g.write(self.model_data.get_scriban_model())

    def write_proc_file(self, dirname: str) -> None:

        if self.gen_info.version < parse_version("0.8.0"):
            self.write_legacy_proc_file(dirname)
            return

        with open(self.get_proc_file(dirname), "w") as g:
            g.write("{{~ Name = '" + self.model_data.name + "' ~}}\n")
            g.write("{{~ TemplateName = '" + self.tpl_info.name + "' ~}}\n")
            if self.tpl_info.pre_init:
                g.write("{{~ include '" + self.tpl_info.pre_init + "'~}}")

            if "global" in self.model_data.configs.data:
                g.write(self.model_data.configs.export_to_scriban("global"))
            recursive_write_config(
                g, self.model_data.configs, self.resources, self.tpl_info.name
            )

            if self.model_data.model:
                g.write("{{~# ------------- Model -----------------~}}\n")
                g.write(self.model_data.get_scriban_model())
            if self.tpl_info.post_init:
                g.write("\n{{~ include '" + self.tpl_info.post_init + "'~}}")

    def get_xml_file(self, dirname: str) -> str:
        """If url the scxml is writen in target (tmp) directory
        Otherwise return the path
        """
        return os.path.join(dirname, self.model_data.name.lower() + ".scxml.xml")
        # if self.model_data.scxml_file is None:
        #     raise ValueError("Bug No scxml file")
        # url = urlparse(self.model_data.scxml_file)
        # if url.scheme:
        #     return os.path.join(dirname, self.model_data.name.lower() + ".scxml.xml")
        # else:
        #     return os.path.abspath(self.model_data.scxml_file)

    def write_xml_file(self, dirname: str) -> None:
        # Copy scxml file in include (then copied by the template)
        if self.model_data.scxml_file is None:
            return None
        url = urlparse(self.model_data.scxml_file)
        if not url.scheme:  # this is a local file just copy it
            with open(self.model_data.scxml_file, "r") as f:
                with open(
                    self.get_xml_file(dirname),
                    "w",
                ) as g:
                    g.write(f.read())
            return None

        req = get_request(self.model_data.scxml_file)
        with open(
            self.get_xml_file(dirname),
            "wb",
        ) as g:
            for chunk in req.iter_content(chunk_size=128):
                g.write(chunk)

    def get_tmc_file(self, dirname: str) -> str:
        """If url the tmc is writen in target (tmp) directory
        Otherwise return the absolute path
        """
        if self.model_data.tmc_file is None:
            raise ValueError("Bug: No tmc file")
        url = urlparse(self.model_data.tmc_file)
        if url.scheme:
            return os.path.join(dirname, self.model_data.name.lower() + ".tmc")
        else:
            return os.path.abspath(self.model_data.tmc_file)

    def write_tmc_file(self, dirname: str) -> None:
        # Copy scxml file in include (then copied by the template)
        if self.model_data.tmc_file is None:
            return None

        url = urlparse(self.model_data.tmc_file)
        if not url.scheme:  # this is a local file leave it there
            return None
        req = get_request(self.model_data.tmc_file)
        with open(
            self.get_tmc_file(dirname),
            "wb",
        ) as g:
            for chunk in req.iter_content(chunk_size=128):
                g.write(chunk)

    def clean_side_products(self) -> None:
        files = [os.path.join(self.output_dir, f) for f in self.garbage_files]
        for file in files:
            if os.path.exists(file):
                os.unlink(file)

    def write_command(self, dirname: str, cmd: list[str]) -> None:
        with open(
            os.path.join(dirname, self.model_data.name.lower() + "_command"), "w"
        ) as g:
            g.write(" ".join(cmd))

    def execute_template(self) -> None:
        if not self.tpl_info.template_dir:
            raise ValueError(
                f"Template {self.tpl_info.name!r} in package {self.tpl_info.package!r} does not have templates. Probably just scriban functions"
            )

        # with tempfile.TemporaryDirectory() as tmpdirname:
        if self.tmpdir is None:
            tmpdir = None
        else:
            tmpdir = _make_tree(self.tmpdir, self.tpl_info.name)

        with TmpDirectory(tmpdir) as tmpdirname:

            # copy includes in tempdirectory
            self.write_proc_file(tmpdirname)
            self.write_xml_file(tmpdirname)
            self.write_tmc_file(tmpdirname)

            cmd = self.build_command(tmpdirname)
            log.info(f"Using .Net @ {self.resources.dotnet_binary}")
            self.write_command(tmpdirname, cmd)
            log.debug("Command executed: " + " ".join(cmd))
            if not self.dry:
                log.info(
                    f"{self.model_data.name} Running template {self.tpl_info.name} ..."
                )
                r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if r.returncode:
                    log.error(r.stdout.decode())
                    log.error(r.stderr.decode())
                    if ".NET location: Not found" in r.stderr.decode():
                        raise RuntimeError(
                            ".NET location: Not found. Please Install .Net.\n "
                            f"You can install with `{PROG_NAME} install dotnet` (linux only)"
                        )
                    raise RuntimeError(
                        f"Template {self.tpl_info.name} failed. See generator output above\n"
                    )
                else:
                    for line in r.stdout.split(b"\n"):
                        log.debug(line.decode())
                    log.info(
                        f"{self.model_data.name}. Template {self.tpl_info.name} finished (set debug to see generator log)"
                    )
                self.execute_post_process(tmpdirname)

        if not self.dry:
            self.clean_side_products()

    def execute_post_process(self, tmpdir: str) -> None:
        if self.tpl_info.post_process is None:
            return
        post_process_file = os.path.join(self.output_dir, self.tpl_info.post_process)
        if not os.path.exists(post_process_file):
            log.error(
                f"Cannot find post process python file {post_process_file!r}. It should be created by the template"
            )

        # mod = importlib.import_module(post_process_file)
        module_name = self.model_data.name.lower() + "_pos_process"
        spec = importlib.util.spec_from_file_location(module_name, post_process_file)
        if spec:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)  # type: ignore

            try:
                mod.main
            except AttributeError:
                log.error(
                    "Post process file must have a main(output_dir: str) function defined. Abording post process"
                )
                return
            log.info(f"{self.model_data.name}, Executing Post Process file")
            try:
                mod.main(tmpdir, self.output_dir)
            except Exception as er:
                raise RuntimeError("Post process failed") from er
            finally:
                base_dir, _ = os.path.split(post_process_file)
                pycache = os.path.join(base_dir, "__pycache__")
                if os.path.exists(pycache):
                    shutil.rmtree(pycache)
                if getattr(mod, "DELETE_ME", False):
                    log.info("Deleting Post Process file (DELETE_ME is True in file)")
                    os.remove(post_process_file)
        else:
            log.error("Problem when loading the module spec")


@dataclass
class Executor:
    model_data: DeviceModelData
    resources: ProgramResources
    output_dir: str = "."
    debug: bool = False
    dry: bool = False
    tmpdir: str | None = None

    def execute_template(self, template: str) -> None:
        tpl_info = self.resources.templates.get_template(template)
        pkg_info = self.resources.packages.get_package(tpl_info.package)
        gen_info = self.resources.generators.get_generator_info(pkg_info.generator)
        output_dir = os.path.join(
            self.output_dir, self.model_data.outputs.get(template, ".")
        )
        TemplateExecutor(
            tpl_info,
            gen_info,
            model_data=self.model_data,
            resources=self.resources,
            output_dir=output_dir,
            debug=self.debug,
            dry=self.dry,
            tmpdir=self.tmpdir,
        ).execute_template()

    def execute(self) -> None:
        for template in self.model_data.templates:
            self.execute_template(template)


def find_platform() -> IPlatform:
    """Return the binary from the current platform"""
    match ptf := platform.system():
        case "Linux":
            return "linux"
        case "Darwin":
            return "osx"
        case "Windows":
            return "windows"
        case _:
            raise ValueError(f"Cannot install tmc2fcf generator on {ptf}")


def find_processor() -> IProcessor:
    """Return 'x' (for x64) or 'arm'"""
    if "arm" in platform.processor():
        return "arm"
    return "x"


def read_scriban_compatible_file(file: str) -> str:
    _, ext = os.path.splitext(file)
    if ext in (".yaml", ".yml"):
        with open(file, "r") as f:
            return _parse_yaml_content_to_scriban(f.read())

    if ext == "json":
        with open(file, "r") as f:
            return _parse_json_content_to_scriban(f.read())

    with open(file, "r") as f:
        return _parse_scriban_content(f.read())


def _make_tree(*tree_path: str) -> str:
    """Return a directory path and make missing dirs"""
    path = ""
    for name in tree_path:
        path = os.path.join(path, name)
        if not os.path.exists(path):
            os.mkdir(path)
        elif os.path.isfile(path):
            raise ValueError(f"{path} is a file. Cannot create directory")

    return path


def _parse_dictionary_content_to_scriban(data: dict[str, Any]) -> str:
    scriban = _parse_dictionary_content_to_scriban_list(data)
    return "{{~\n" + ("\n".join(scriban)) + "\n~}}\n"


def _parse_dictionary_content_to_scriban_list(data: dict[str, Any]) -> list[str]:
    if not isinstance(data, dict):
        ValueError("Cannot parse content: this is not a json dictionary")
    scriban: list[str] = []
    for key, value in data.items():
        if isinstance(value, str):
            scriban.append("capture " + key + " -}}" + value + "{{-end")
        else:
            scriban.append(f"{key} = {json.dumps(value)}")
    return scriban


def _parse_json_content_to_scriban(content: str) -> str:
    data = json.loads(content)
    return _parse_dictionary_content_to_scriban(data)


def _parse_yaml_content_to_scriban(content: str) -> str:
    data = yaml.load(io.StringIO(content), yaml.CLoader)
    return _parse_dictionary_content_to_scriban(data)


def _parse_scriban_content(txt: str) -> str:
    txt = txt.strip(" \n\t")
    if not txt.startswith("{{") or not txt.endswith("}}"):
        raise ValueError(
            "Scriban include file should start with '{{' and end with '}}' "
        )
    return txt


# ######################################################################
# A tmc2fcfs Package loader based on token access
# this is currently not used
_platform_names = {
    BinaryType.OSX: "osx-x64",
    BinaryType.LINUX: "linux-x64",
    BinaryType.WINDOW: "win-x64",
}


@dataclass
class GeneratorRepositoryData:
    binary_type: BinaryType
    token_value: str = "glpat-7NBZcJbjjng5sqLcsWxs"
    token_name: str = "TMC2FCS_ASSET_DOWN"
    asset: str = "00.07.08"

    _url_format: str = (
        "https://{token_name}:{token_value}@gitlab.lam.fr/api/v4/projects/efisoft%2Ftmc2fcs_generator/packages/generic/my_package/{asset}/tmc2fcs_generator-{asset}-{platform_name}.zip"
    )

    def get_url(self) -> str:
        return self._url_format.format(
            token_value=self.token_value,
            token_name=self.token_name,
            asset=self.asset,
            platform_name=self.get_platform_name(),
        )

    def get_target_file_name(self) -> str:
        return f"tmc2fcs_generator-{self.asset}-{self.get_platform_name()}.zip"

    def get_target_dir_name(self) -> str:
        return f"tmc2fcs_generator-{self.asset}-{self.get_platform_name()}"

    def get_platform_name(self) -> str:
        return _platform_names[self.binary_type]


#####
# define some datclasses in order to parse a User Model
class ModelType(NamedTuple):
    opcua: str
    variant: int


UaTypeLoockup: dict[str, ModelType] = {
    "Boolean": ModelType("Boolean", 1),
    "SByte": ModelType("SByte", 2),
    "Byte": ModelType("Byte", 3),
    "Int16": ModelType("Int16", 4),
    "UInt16": ModelType("UInt16", 5),
    "Int32": ModelType("Int32", 6),
    "UInt32": ModelType("UInt32", 7),
    "Int64": ModelType("Int64", 8),
    "UInt64": ModelType("UInt64", 9),
    "Float": ModelType("Float", 10),
    "Double": ModelType("Double", 11),
    "String": ModelType("String", 12),
    "DateTime": ModelType("DateTime", 13),
    "ByteString": ModelType("ByteString", 15),
}


def parse_model_access(
    access: int | Literal["r", "w", "rw", "?", ""],
) -> int:
    if isinstance(access, int):
        if 0 <= access <= 3:
            return access
        else:
            raise ValueError(
                f"Invalid access {access!r}, expecting  '','r','w','rw' or integer between 0 and 3"
            )
    else:
        match access:
            case "r":
                return 1
            case "w":
                return 2
            case "rw":
                return 3
            case "?" | "":
                return 0
            case _:
                raise ValueError(
                    f"Invalid access {access!r}, expecting  '','r','w','rw' or integer between 0 and 3"
                )


@dataclass
class ExposedProperty:
    name: str
    type_: str
    default: str | None = None
    size: int | tuple[int, int] = 0
    comment: str = ""
    opcua_id: str | None = None
    access: int = 0
    kind: Literal["base", "enum", "extension"] | None = None

    def __post_init__(self) -> None:
        if self.kind == "base" and self.type_ not in UaTypeLoockup:
            raise ValueError(
                f"Invalid base type {self.type_!r} "
                f"expecting one of {tuple(UaTypeLoockup)}"
            )

    @property
    def opcua_type(self) -> str:
        match self.kind:
            case "base":
                return UaTypeLoockup[self.type_].opcua
            case "enum":
                return self.type_
            case "extension":
                return "ExtensionObject"
            case None:
                if self.type_ in UaTypeLoockup:
                    return UaTypeLoockup[self.type_].opcua
                return "ExtensionObject"

    @property
    def is_extension(self) -> bool:
        return self.type_ not in UaTypeLoockup

    @property
    def is_array(self) -> bool:
        return bool(self.size)

    @property
    def array_size(self) -> int:
        if isinstance(self.size, int):
            return self.size
        else:
            left, right = self.size
            return right - left + 1

    @property
    def array_left_bound(self) -> int:
        if isinstance(self.size, int):
            return 0
        else:
            left, _ = self.size
            return left

    @property
    def variant(self) -> int:
        try:
            return UaTypeLoockup[self.type_].variant
        except KeyError:
            return 0  # TODO Is it okay to return 0 ?

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExposedProperty:
        data = data.copy()
        # TODO: Data check
        try:
            data["type_"] = data.pop("type")
        except KeyError:
            raise ValueError(f"Missing Property type in {data}")

        if "access" in data:
            data["access"] = parse_model_access(data["access"])

        return ExposedProperty(**data)

    @classmethod
    def from_mixed(cls, name: str, data: dict[str, Any]) -> ExposedProperty:
        return cls.from_dict(dict(name=name, **data))

    def export(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "OpcUaType": self.opcua_type,
            "Type": self.type_,
            "Default": self.default,
            "IsArray": self.is_array,
            "ArraySize": self.array_size,
            "ArrayLeftBound": self.array_left_bound,
            "Comment": [self.comment],
            "OpcUaPrefix": "",  # Model export only root properties
            "OpcUaId": self.opcua_id,
            "OpcUaAccess": self.access,
        }

    def export_method_parameter(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "Comment": [self.comment],
            "Type": self.type_,
            "IsArray": self.is_array,
            "ArraySize": self.array_size,
            "ArrayLeftBound": self.array_left_bound,
            "OpcUaType": self.opcua_type,
            "OpcUaTypeId": self.variant,
            "OpcUaDeclaration": "",  # What is it ?
        }


@dataclass
class ExposedProperties:
    properties: list[ExposedProperty] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.properties)

    @classmethod
    def from_list(cls, data: list[dict[str, Any]]) -> ExposedProperties:
        return cls([ExposedProperty.from_dict(d) for d in data])

    @classmethod
    def from_dict(cls, data: dict[str, dict[str, Any]]) -> ExposedProperties:
        return cls([ExposedProperty.from_mixed(name, d) for name, d in data.items()])

    def export(self) -> list[dict[str, Any]]:
        return [p.export() for p in self.properties]

    def export_method_parameters(self, is_input: bool) -> dict[str, Any]:
        return {
            "OpcUaId": "",
            "IsIn": is_input,
            "Parameters": [p.export_method_parameter() for p in self.properties],
        }


@dataclass
class ExposedMethod:
    name: str
    inputs: ExposedProperties = field(default_factory=ExposedProperties)
    outputs: ExposedProperties = field(default_factory=ExposedProperties)
    comment: str = ""
    opcua_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExposedMethod:
        data = data.copy()
        if "name" not in data:
            raise ValueError("Missing Method name")

        data_inputs = data.pop("inputs", [])
        if isinstance(data_inputs, dict):
            inputs = ExposedProperties.from_dict(data_inputs)
        else:
            inputs = ExposedProperties.from_list(data_inputs)

        data_outputs = data.pop("outputs", [])
        if isinstance(data_outputs, dict):
            outputs = ExposedProperties.from_dict(data_outputs)
        else:
            outputs = ExposedProperties.from_list(data_outputs)

        return cls(**data, inputs=inputs, outputs=outputs)

    @classmethod
    def from_mixed(cls, name: str, data: dict[str, Any]) -> ExposedMethod:
        return cls.from_dict(dict(name=name, **data))

    def export(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "Comment": self.comment,
            "HasIn": bool(self.inputs),
            "HasOut": bool(self.outputs),
            "In": self.inputs.export_method_parameters(True),
            "Out": self.outputs.export_method_parameters(False),
            "OpcUaId": self.opcua_id,
        }


@dataclass
class ExposedMethods:
    methods: list[ExposedMethod] = field(default_factory=list)

    @classmethod
    def from_list(cls, data: list[dict[str, Any]]) -> ExposedMethods:
        return cls([ExposedMethod.from_dict(d) for d in data])

    @classmethod
    def from_dict(cls, data: dict[str, dict[str, Any]]) -> ExposedMethods:
        return cls([ExposedMethod.from_mixed(name, d) for name, d in data.items()])

    def export(self) -> list[dict[str, Any]]:
        return [m.export() for m in self.methods]

    @property
    def size(self) -> int:
        return len(self.methods)


@dataclass
class ExposedClass:
    name: str
    extends: bool = False
    extends_type: str = ""
    properties: ExposedProperties = field(default_factory=ExposedProperties)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExposedClass:
        data = data.copy()
        if "extends" in data and "extends_type" not in data:
            raise ValueError(
                "When parsing a Class, get extentds=True but no extends_type given"
            )
        data_properties = data.pop("properties", [])
        if isinstance(data_properties, dict):
            properties = ExposedProperties.from_dict(data_properties)
        else:
            properties = ExposedProperties.from_list(data_properties)
        return ExposedClass(**data, properties=properties)

    @classmethod
    def from_mixed(cls, name: str, data: dict[str, Any]) -> ExposedClass:
        return cls.from_dict(dict(name=name, **data))

    def export(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "Extends": self.extends,
            "ExtendsType": self.extends_type,
            "ExposedProperties": self.properties.export(),
        }


@dataclass
class ExposedEnumMember:
    label: str
    value: int
    comment: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExposedEnumMember:
        data = data.copy()
        try:
            label = data["label"]
            value = data["value"]
        except KeyError:
            raise ValueError("Enum member should have 'label' and 'value' keyword")

        if extras := (set(data) - {"label", "value", "comment"}):
            raise ValueError(f"Extra keyword in Enum member definition: {extras}")

        return cls(label=label, value=value, comment=data.get("comment", ""))

    @classmethod
    def from_mixed(cls, label: str, val: int | tuple[int, str]) -> ExposedEnumMember:
        if isinstance(val, int):
            return cls(label=label, value=val)
        else:
            value, comment = val
            return cls(label=label, value=value, comment=comment)

    def export(self) -> dict[str, Any]:
        return {
            "Label": self.label,
            "Value": self.value,
            "Comment": [self.comment] if self.comment else [],
        }


@dataclass
class ExposedEnum:
    name: str
    entries: list[ExposedEnumMember] = field(default_factory=list)
    comment: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExposedEnum:
        data = data.copy()
        try:
            name = data["name"]
        except KeyError:
            raise ValueError("Missing name keyword for enum declaration")
        if extras := (set(data) - {"name", "entries", "comment"}):
            raise ValueError(f"Extra keyword in Enum definition: {extras}")
        data_entries = data.get("entries", [])
        if isinstance(data_entries, dict):
            entries = [
                ExposedEnumMember.from_mixed(lb, v) for lb, v in data_entries.items()
            ]
        else:
            entries = [ExposedEnumMember.from_dict(d) for d in data_entries]
        return cls(name=name, entries=entries, comment=data.get("comment", ""))

    @classmethod
    def from_mixed(cls, name: str, data: dict[str, Any]) -> ExposedEnum:
        return cls.from_dict(dict(name=name, **data))

    def export(self) -> dict[str, Any]:
        return {
            "Name": self.name,
            "Entries": [e.export() for e in self.entries],
            "ForceUse": True,
            "Comment": [self.comment] if self.comment else [],
        }


@dataclass
class ExposedEnums:
    enums: list[ExposedEnum] = field(default_factory=list)

    @staticmethod
    def from_list(data: list[dict[str, Any]]) -> ExposedEnums:
        return ExposedEnums([ExposedEnum.from_dict(e) for e in data])

    @staticmethod
    def from_dict(data: dict[str, dict[str, Any]]) -> ExposedEnums:
        return ExposedEnums(
            [ExposedEnum.from_mixed(name, e) for name, e in data.items()]
        )

    def export(self) -> list[dict[str, Any]]:
        return [e.export() for e in self.enums]

    @property
    def size(self) -> int:
        return len(self.enums)


_model_merger = """
# We merge exported array to model, then model arrays replace the exported
func _has_model_enum(Name)
  for _mobj in M.Enums
     if _mobj.Name == Name 
        ret true
     end 
  end 
  ret false
end
for _obj in Enums 
   if !_has_model_enum(_obj.Name)
     M.Enums[M.Enums.size] = _obj
   end 
end
func _has_model_class(Name)
  if M.ExposedClasses[Name] 
    ret true 
  end 
  ret false
end

for _obj_key in (object.keys ExposedClasses) 
   if !_has_model_class(_obj_key)
     M.ExposedClasses[_obj_key] = ExposedClasses[_obj_key]
   end 
end

func _has_model_property(Name)
  for _mobj in M.ExposedProperties
     if _mobj.Name == Name 
        ret true
     end 
  end 
  ret false
end
for _obj in ExposedProperties 
   if !_has_model_property(_obj.Name)
     M.ExposedProperties[M.ExposedProperties.size] = _obj
   end 
end
func _has_model_object(Name)
  for _mobj in M.ExposedObjects
     if _mobj.Name == Name 
        ret true
     end 
  end 
  ret false
end
for _obj in ExposedObjects 
   if !_has_model_object(_obj.Name)
     M.ExposedObjects[M.ExposedObjects.size] = _obj
   end 
end

func _has_model_method(Name)
  for _mobj in M.ExposedMethods
     if _mobj.Name == Name 
        ret true
     end 
  end 
  ret false
end
for _obj in ExposedMethods 
   if !_has_model_method(_obj.Name)
     M.ExposedMethods[M.ExposedMethods.size] = _obj
   end 
end

ExposedClasses = M.ExposedClasses
ExposedProperties = M.ExposedProperties
ExposedObjects = M.ExposedObjects
ExposedMethods = M.ExposedMethods 
Enums = M.Enums

"""


@dataclass
class Model:
    classes: dict[str, ExposedClass] = field(default_factory=dict)
    properties: ExposedProperties = field(default_factory=ExposedProperties)
    methods: ExposedMethods = field(default_factory=ExposedMethods)
    enums: ExposedEnums = field(default_factory=ExposedEnums)
    extras: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.fix_enum_type()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Model:
        data = data.copy()

        data_classes = data.pop("classes", [])
        if isinstance(data_classes, dict):
            classes = [
                ExposedClass.from_mixed(name, d) for name, d in data_classes.items()
            ]
        else:
            classes = [ExposedClass.from_dict(d) for d in data_classes]

        data_properties = data.pop("properties", [])
        if isinstance(data_properties, dict):
            properties = ExposedProperties.from_dict(data_properties)
        else:
            properties = ExposedProperties.from_list(data_properties)

        data_methods = data.pop("methods", [])
        if isinstance(data_methods, dict):
            methods = ExposedMethods.from_dict(data_methods)
        else:
            methods = ExposedMethods.from_list(data_methods)

        data_enums = data.pop("enums", [])
        if isinstance(data_enums, dict):
            enums = ExposedEnums.from_dict(data_enums)
        else:
            enums = ExposedEnums.from_list(data_enums)

        return Model(
            properties=properties,
            methods=methods,
            classes={c.name: c for c in classes},
            enums=enums,
            extras=data,
        )

    def export(self) -> dict[str, Any]:
        return {
            "ExposedClasses": {name: cl.export() for name, cl in self.classes.items()},
            "ExposedProperties": self.properties.export(),
            "ExposedMethods": self.methods.export(),
            "Enums": self.enums.export(),
        }

    def export_to_scriban(self) -> str:
        scriban = ["M = {}"]

        json_classes = json.dumps(
            {name: cl.export() for name, cl in self.classes.items()}
        )
        scriban.append(f"M.ExposedClasses = {json_classes}")

        json_properties = json.dumps(self.properties.export())
        scriban.append(f"M.ExposedProperties = {json_properties}")
        scriban.append(f"M.ExposedObjects = {json_properties}")

        json_methods = json.dumps(self.methods.export())
        scriban.append(f"M.ExposedMethods = {json_methods}")

        json_enums = json.dumps(self.enums.export())
        scriban.append(f"M.Enums = {json_enums}")

        scriban.extend(_parse_dictionary_content_to_scriban_list(self.extras))

        scriban.extend(self.write_model_merging_scriban())

        return "{{~\n" + ("\n".join(scriban)) + "\n~}}\n"

    def write_model_merging_scriban(self) -> list[str]:
        return [_model_merger]

    def _export_to_scriban(self) -> str:
        scriban = []

        scriban.extend(
            [
                "ModelExposedClasses = {}",
                "for _k in (object.keys ExposedClasses); ModelExposedClasses[_k] = ExposedClasses[_k]; end",
                "ExposedClasses = ModelExposedClasses",
            ]
        )

        if self.classes:
            for name, cl in self.classes.items():
                json_class = json.dumps(cl.export())
                scriban.append(f"ExposedClasses['{name}'] = {json_class}")
        if self.properties:
            json_properties = json.dumps(self.properties.export())
            scriban.append(
                f"ExposedProperties = array.add_range ExposedProperties {json_properties}"
            )
        scriban.extend(_parse_dictionary_content_to_scriban_list(self.extras))

        return "{{~\n" + ("\n".join(scriban)) + "\n~}}\n"

    def fix_enum_type(self) -> None:
        enums = set(e.name for e in self.enums.enums)
        for prop in self.properties.properties:
            if prop.kind is None and prop.type_ in enums:
                prop.kind = "enum"

        for _, cl in self.classes.items():
            for prop in cl.properties.properties:
                if prop.kind is None and prop.type_ in enums:
                    prop.kind = "enum"


class ArgsProtocol(Protocol):
    """expected vars comming from devsim args parser"""

    model: list[str]
    output_dir: str
    debug: bool
    dry: bool
    tmpdir: str | None
    verbose: Literal["ERROR", "WARNING", "INFO", "DEBUG"]
    param: list[tuple[str, str]]
    template: None | str


def get_tmc_export_argument_parser(
    subcommand: str = "",
) -> argparse.ArgumentParser:

    arg_parser = argparse.ArgumentParser(
        prog=PROG_NAME + " " + subcommand,
        description="Export, Generate code from a model file",
    )

    arg_parser.add_argument(
        "model",
        nargs="+",
        default=[],
        help=("""model file(s) containing all export configuration"""),
    )

    arg_parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        default="",
        help=(
            "Output Directory. If not given output directory will be the directory"
            " where the input model file is located."
            " Warning, If several model files are given, they will be exported at"
            " the same output dir root"
        ),
    )

    arg_parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode will force verbose to DEBUG",
        default=False,
    )

    arg_parser.add_argument(
        "-v",
        "--verbose",
        choices=["ERROR", "WARNING", "INFO", "DEBUG"],
        help="verbose level. No effect if --debug",
        default="INFO",
    )

    arg_parser.add_argument(
        "--dry",
        action="store_true",
        help="Dry run. Template is not executed",
        default=False,
    )

    arg_parser.add_argument(
        "--tmpdir",
        dest="tmpdir",
        help="Specify a directory where generation temp products are writen. If not given these files are deleted after export",
        default=None,
    )

    arg_parser.add_argument(
        "-p",
        "--param",
        nargs=2,
        help=(
            "Force a template config parameters e.g. '-p SrcPath \"client\" -p Rename true'. "
            "This will erase what set in the model file and used on all templates"
        ),
        action="append",
        metavar=("name", "value"),
        default=[],
    )
    arg_parser.add_argument(
        "--template",
        help="Force the execution of this template only. The one defined in model file will be ignored.",
        default=None,
    )
    return arg_parser


# LOG_FORMAT = (
#     "%(asctime)s.%(msecs)03d:%(levelname)s"
#     + " %(funcName)s: %(message)s"
# )
LOG_FORMAT = "%(levelname)s" + " %(funcName)s: %(message)s"


def _init_logger(
    logger: logging.Logger,
    log_level: str | None = None,
    verbose: bool = True,
    force: bool = False,
) -> None:
    """Init the App logger

    Args:
        logs: log name(s) separated by " " or "," or a logger, or a list of logger
        log_level: valid log level name DEBUG, INFO, WARNING, ERROR
        verbose: if True (default) make the logger console verbose
    """
    if not force and getattr(logger, "_initialised", False):
        return
    if verbose:
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    if log_level is not None:
        try:
            log_level = typing.cast(str, getattr(logging, log_level))
        except AttributeError:
            raise ValueError(f"Unknown log level {log_level}")
        logger.setLevel(logging.getLevelName(log_level))
    setattr(logger, "_initialised", True)


def _join(*args: str) -> str:
    return " ".join(a for a in args if a)


def _parse_param_value(value: str) -> Any:
    if value.startswith("{{"):
        return value
    return yaml.load(value, yaml.CLoader)


@dataclass
class ExportCommand:
    context: str = ""

    def get_argument_parser(self, *sub_command: str) -> argparse.ArgumentParser:
        del sub_command  # does not take any subcommand
        return get_tmc_export_argument_parser(self.context)

    def parse(self, argv: list[str]) -> ArgsProtocol:
        return typing.cast(ArgsProtocol, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        global log
        arg_parser = self.get_argument_parser()
        args: ArgsProtocol = typing.cast(ArgsProtocol, arg_parser.parse_args(argv))
        _init_logger(log, "DEBUG" if args.debug else args.verbose, True)

        program_resources = ProgramResources()
        program_resources.update()

        for model in args.model:
            model_url = urlparse(model)
            if model_url.scheme:
                working_dir = "."
                model_file = model
            else:
                working_dir, model_file = os.path.split(model)
                
            if args.output_dir:
                output_dir = os.path.abspath(args.output_dir)
            else:
                output_dir = os.path.abspath(working_dir)

            with contextlib.chdir(working_dir or "."):
                device = DeviceModelData.from_yaml(model_file)
                if args.template:
                    device.templates = [args.template]
                if len(args.param):
                    for template in device.templates:
                        device.configs.append_template_data(
                            template, {n: _parse_param_value(v) for n, v in args.param}
                        )

                executor = Executor(
                    device,
                    program_resources,
                    output_dir=output_dir,
                    debug=args.debug,
                    dry=args.dry,
                    tmpdir=args.tmpdir,
                )
                log.debug(os.getcwd())
                executor.execute()


class IRunProtocol(Protocol):
    """expected vars comming from devsim args parser"""

    name: str
    template: str
    extract: str
    tmc: str
    output_dir: str
    scxml: str
    dry: bool
    tmpdir: str | None
    verbose: Literal["ERROR", "WARNING", "INFO", "DEBUG"]
    param: list[tuple[str, str]]
    include: list[str]


@dataclass
class RunCommand:
    context: str = ""

    def get_argument_parser(self, *sub_command: str) -> argparse.ArgumentParser:
        del sub_command  # does not take any subcommand
        arg_parser = argparse.ArgumentParser(
            prog=PROG_NAME + " " + self.context,
            description="Run the generator, export code from command line",
        )

        arg_parser.add_argument("-n", "--name", help="Device name", required=True)
        arg_parser.add_argument(
            "-t", "--template", help="Template name (must be installed)", required=True
        )
        arg_parser.add_argument(
            "-e",
            "--extract",
            help="Extraction root. e.g. 'MAIN.Lamp001'",
            required=True,
        )
        arg_parser.add_argument(
            "--tmc", help="Path to the tmc file (can be an url)", required=True
        )
        arg_parser.add_argument(
            "-o",
            "--output_dir",
            dest="output_dir",
            default=".",
            help=(
                "Output Directory. If not given output directory will be the current directory"
            ),
        )

        arg_parser.add_argument(
            "-s", "--scxml", help="Path to the scxml file statechart (can be an url)"
        )
        arg_parser.add_argument(
            "-v",
            "--verbose",
            choices=["ERROR", "WARNING", "INFO", "DEBUG"],
            help="verbose level. No effect if --debug",
            default="INFO",
        )
        arg_parser.add_argument(
            "--dry",
            action="store_true",
            help="Dry run. Template is not executed",
            default=False,
        )
        arg_parser.add_argument(
            "--tmpdir",
            dest="tmpdir",
            help="Specify a directory where generation temp products are writen. If not given these files are deleted after export",
            default=None,
        )

        arg_parser.add_argument(
            "-i",
            "--include",
            help="template config yaml file to include (can be an url)",
            action="append",
            default=[],
        )

        arg_parser.add_argument(
            "-p",
            "--param",
            nargs=2,
            help="Set template config parameters e.g. '-p SrcPath \"client\" -p Rename true'",
            action="append",
            metavar=("name", "value"),
            default=[],
        )

        return arg_parser

    def parse(self, argv: list[str]) -> IRunProtocol:
        return typing.cast(IRunProtocol, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        global log
        args = self.parse(argv)
        _init_logger(log, args.verbose, True)

        program_resources = ProgramResources()
        program_resources.update()

        configs = ConfigsData()
        configs.append_template_data(
            args.template, {n: _parse_param_value(v) for n, v in args.param}
        )
        for inc in args.include:
            configs.append_yaml(inc)

        model = DeviceModelData(
            name=args.name,
            extraction_root=args.extract,
            tmc_file=args.tmc,
            scxml_file=args.scxml,
            templates=[args.template],
            configs=configs,
        )
        executor = Executor(
            model,
            program_resources,
            output_dir=args.output_dir,
            debug=args.verbose == "DEBUG",
            dry=args.dry,
            tmpdir=args.tmpdir,
        )
        log.debug(os.getcwd())
        executor.execute()


class IInstallPackageArgs(Protocol):
    package_name: str
    version: str
    force: bool
    local: bool
    remote: bool


@dataclass
class InstallPackageCommand:
    context: str = ""

    def get_argument_parser(self, *subcommand: str) -> argparse.ArgumentParser:
        del subcommand  # no further sub-command
        arg_parser = argparse.ArgumentParser(
            description=(
                "Install a template package. \n\n"
                "Several templates can be added from one package"
            ),
            prog=_join(PROG_NAME + " " + self.context),
        )
        arg_parser.add_argument("package_name")
        arg_parser.add_argument(
            "-v",
            "--version",
            help="Version specifier of the package use",
            default=None,
        )
        arg_parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Force the installation even if satified",
            default=False,
        )
        arg_parser.add_argument(
            "-l",
            "--local",
            action="store_true",
            help="Remove the embiguity between a package name or a local directory",
            default=None,
        )
        arg_parser.add_argument(
            "-r",
            "--remote",
            action="store_true",
            help="Remove embiguity between a package name or a local directory",
            default=None,
        )

        return arg_parser

    def parse(self, argv: list[str]) -> IInstallPackageArgs:
        return typing.cast(
            IInstallPackageArgs, self.get_argument_parser().parse_args(argv)
        )

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        _init_logger(log, "INFO", True)

        version = Specifier(">0.0") if args.version is None else Specifier(args.version)
        resources = ProgramResources()
        resources.update()
        installer = TemplatePackageInstaller(resources=resources)
        if args.local is not None and args.local:
            installer.install_local(args.package_name)
        elif args.remote is not None and args.remote:
            installer.install_remote(args.package_name, version, args.force)
        else:
            installer.install(args.package_name, version, args.force)


class IInstallDotnetArgs(Protocol):
    version: str
    force: bool


@dataclass
class InstallDotnetCommand:
    context: str = ""

    def get_argument_parser(self, *subcommand: str) -> argparse.ArgumentParser:
        del subcommand  # no further subcommand
        arg_parser = argparse.ArgumentParser(
            description="Install dotnet. Only work on Linux platform",
            prog=_join(PROG_NAME + " " + self.context),
        )
        arg_parser.add_argument(
            "-v",
            "--version",
            help="NOTE YET IMPLEMENTED Version of dotnet",
            default="",
        )
        arg_parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Force the download of dotnet",
            default=False,
        )

        return arg_parser

    def parse(self, argv: list[str]) -> IInstallDotnetArgs:
        return typing.cast(
            IInstallDotnetArgs, self.get_argument_parser().parse_args(argv)
        )

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        _init_logger(log, "INFO", True)
        DotNetInstaller(force=args.force, explicit=True).install()


class IInstallGeneratorArgs(Protocol):
    version: str
    force: bool


@dataclass
class InstallGeneratorCommand:
    context: str = ""

    def get_argument_parser(self, *subcommand: str) -> argparse.ArgumentParser:
        del subcommand  # no further subcommand
        arg_parser = argparse.ArgumentParser(
            description="Install A Generator with a given version",
            prog=_join(PROG_NAME + " " + self.context),
        )
        arg_parser.add_argument(
            "-v",
            "--version",
            help="version specifier (e.g. >=0.8.0 , ==0.8.1, etc)",
            default=None,
        )
        # arg_parser.add_argument(
        #     "-f",
        #     "--force",
        #     action="store_true",
        #     help="Force the download",
        #     default=False,
        # )

        return arg_parser

    def parse(self, argv: list[str]) -> IInstallGeneratorArgs:
        return typing.cast(
            IInstallGeneratorArgs, self.get_argument_parser().parse_args(argv)
        )

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        _init_logger(log, "INFO", True)
        pkg_mgr = PkgManager()
        platform = find_platform()
        processor = find_processor()
        version_spec = (
            Specifier(">0.0") if args.version is None else Specifier(args.version)
        )
        version = pkg_mgr.resolve_generator_version(version_spec)
        pkg_mgr.install_generator(CONFIG_DIR, version, platform, processor)


class IInstallAllArgs(Protocol):
    force: bool


@dataclass
class InstallAllCommand:
    context: str = ""

    def get_argument_parser(self, *subcommand: str) -> argparse.ArgumentParser:
        del subcommand  # no further subcommand
        arg_parser = argparse.ArgumentParser(
            description="Install dotnet, all nown package and generator",
            prog=_join(PROG_NAME + " " + self.context),
        )
        arg_parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Force the download",
            default=False,
        )

        return arg_parser

    def parse(self, argv: list[str]) -> IInstallAllArgs:
        return typing.cast(IInstallAllArgs, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        _init_logger(log, "INFO", True)
        pkg_mgr = PkgManager()
        platform = find_platform()
        DotNetInstaller(force=args.force, explicit=False).install()

        version = Specifier(">0.0")
        resources = ProgramResources()
        resources.update()
        installer = TemplatePackageInstaller(resources=resources)
        for pkgname, _ in pkg_mgr.iter_packages():
            installer.install(pkgname, version, args.force)


class IInstallArgs(Protocol):
    category: Literal["package", "dotnet", "generator", "all"]

    subargs: list[str]


@dataclass
class InstallCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:
        if subcommands:
            cmd, *others = subcommands
            match cmd:
                case "package":
                    return InstallPackageCommand(
                        _join(self.context, "package")
                    ).get_argument_parser(*others)
                case "dotnet":
                    return InstallDotnetCommand(
                        _join(self.context, "dotnet")
                    ).get_argument_parser(*others)
                case "generator":
                    return InstallGeneratorCommand(
                        _join(self.context, "generator")
                    ).get_argument_parser(*others)
                case "all":
                    return InstallAllCommand(
                        _join(self.context, "all")
                    ).get_argument_parser(*others)

                case _:
                    raise ValueError("Not a valid subcommand")

        arg_parser = argparse.ArgumentParser(
            description="Install template package, generator or .Net",
            prog=_join(PROG_NAME + " " + self.context),
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=dedent(
                f"""
              See the specific install categores for further options.
                e.g. {PROG_NAME} help install package
            """
            ),
        )
        arg_parser.add_argument(
            "category",
            help=dedent(
                "- package: install given package\n"
                "- dotnet: install .Net \n"
                "- generator: install a generator\n"
                "- all: install all know template packages and .Net (Linux)"
            ),
            choices=["package", "generator", "dotnet", "all"],
        )
        arg_parser.add_argument(
            "subargs", nargs=argparse.REMAINDER, help=argparse.SUPPRESS
        )
        return arg_parser

    def parse(self, argv: list[str]) -> IInstallArgs:
        return typing.cast(IInstallArgs, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        _init_logger(log, "INFO", True)
        match args.category:
            case "package":
                InstallPackageCommand(_join(self.context, "package")).execute(
                    args.subargs
                )
            case "dotnet":
                InstallDotnetCommand(_join(self.context, "dotnet")).execute(
                    args.subargs
                )
            case "generator":
                InstallGeneratorCommand(_join(self.context, "generator")).execute(
                    args.subargs
                )
            case "all":
                InstallAllCommand(_join(self.context, "all")).execute(args.subargs)


class IAvailPackageArgs(Protocol): ...


@dataclass
class AvailPackageCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:
        if subcommands:
            raise ValueError(f"Invalid subcommand {subcommands}")

        arg_parser = argparse.ArgumentParser(
            description=("List the installed packages. \n\n"),
            prog=_join(PROG_NAME + " " + self.context),
        )

        return arg_parser

    def parse(self, argv: list[str]) -> IAvailPackageArgs:
        return typing.cast(
            IAvailPackageArgs, self.get_argument_parser().parse_args(argv)
        )

    def execute(self, argv: list[str]) -> None:
        self.parse(argv)
        _init_logger(log, "WARNING", True)
        resources = ProgramResources()
        resources.update()
        for name, pkg in resources.packages.iter_packages():
            print(name, pkg.version)


class IAvailTemplatesArgs(Protocol): ...


@dataclass
class AvailTemplatesCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:

        if subcommands:
            raise ValueError(f"Invalid subcommand {subcommands}")

        arg_parser = argparse.ArgumentParser(
            description=("List the installed templates. \n\n"),
            prog=_join(PROG_NAME + " " + self.context),
        )

        return arg_parser

    def parse(self, argv: list[str]) -> IAvailTemplatesArgs:
        return typing.cast(
            IAvailTemplatesArgs, self.get_argument_parser().parse_args(argv)
        )

    def execute(self, argv: list[str]) -> None:
        self.parse(argv)
        _init_logger(log, "WARNING", True)
        resources = ProgramResources()
        resources.update()
        print("name           package         dependencies")
        for name, tpl in resources.templates.iter_templates():
            if not tpl.template_dir:
                name = "(" + name + ")"
            pkg = resources.packages.get_package(tpl.package)
            desc = tpl.get_description(resources.packages, short=True).strip("\n")
            dep = []
            for dependency in tpl.dependencies:
                if dependency.package == ".":
                    pkgs = pkg.name
                else:
                    pkgs = dependency.package
                for tpl_dep in dependency.templates:
                    dep.append(f"{pkgs}/{tpl_dep}")
            sdep = "->".join(dep)
            s = ""
            print(
                f"{name:10s} {tpl.package:>10s} {str(pkg.version):8s} {sdep}\n{s:31s}{desc}\n"
            )


class IAvailGeneratorsArgs(Protocol): ...


@dataclass
class AvailGeneratorsCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:
        if subcommands:
            raise ValueError(f"Invalid subcommand {subcommands}")

        arg_parser = argparse.ArgumentParser(
            description=("List the installed generators. \n\n"),
            prog=_join(PROG_NAME + " " + self.context),
        )

        return arg_parser

    def parse(self, argv: list[str]) -> IAvailGeneratorsArgs:
        return typing.cast(
            IAvailGeneratorsArgs, self.get_argument_parser().parse_args(argv)
        )

    def execute(self, argv: list[str]) -> None:
        self.parse(argv)
        _init_logger(log, "WARNING", True)
        resources = ProgramResources()
        resources.update()
        for (version, splatform), _ in resources.generators.iter_generators():
            print(f"{version} {splatform} ")


class IAvailArgs(Protocol):
    category: Literal["packages", "templates", "generators"]

    subargs: list[str]


@dataclass
class AvailCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:
        if subcommands:
            cmd, *others = subcommands
            match cmd:
                case "packages":
                    return AvailPackageCommand(
                        _join(self.context, "packages")
                    ).get_argument_parser(*others)
                case "templates":
                    return AvailTemplatesCommand(
                        _join(self.context, "templates")
                    ).get_argument_parser(*others)
                case "generators":
                    return AvailGeneratorsCommand(
                        _join(self.context, "generators")
                    ).get_argument_parser(*others)

        arg_parser = argparse.ArgumentParser(
            description=("List installed generator, package or templates. "),
            prog=_join(PROG_NAME + " " + self.context),
        )
        arg_parser.add_argument(
            "category", choices=["packages", "templates", "generators"]
        )
        arg_parser.add_argument(
            "subargs", nargs=argparse.REMAINDER, help=argparse.SUPPRESS
        )
        return arg_parser

    def parse(self, argv: list[str]) -> IAvailArgs:
        return typing.cast(IAvailArgs, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        _init_logger(log, "WARNING", True)
        match args.category:
            case "packages":
                AvailPackageCommand(_join(self.context, "packages")).execute(
                    args.subargs
                )
            case "templates":
                AvailTemplatesCommand(_join(self.context, "packages")).execute(
                    args.subargs
                )
            case "generators":
                AvailGeneratorsCommand(_join(self.context, "generators")).execute(
                    args.subargs
                )

            case _:
                raise ValueError(f"Invalid Category {args.category}")


class IListGeneratorsArgs(Protocol): ...


@dataclass
class ListGeneratorsCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:
        if subcommands:
            raise ValueError(f"Invalid subcommand {subcommands}")

        arg_parser = argparse.ArgumentParser(
            description=("List the available generators for download. "),
            prog=_join(PROG_NAME + " " + self.context),
        )

        return arg_parser

    def parse(self, argv: list[str]) -> IListGeneratorsArgs:
        return typing.cast(
            IListGeneratorsArgs, self.get_argument_parser().parse_args(argv)
        )

    def execute(self, argv: list[str]) -> None:
        self.parse(argv)
        _init_logger(log, "WARNING", True)
        pkg_mgr = PkgManager()
        for version, _ in pkg_mgr.iter_generators():
            print(version)


class IListPackagesArgs(Protocol): ...


@dataclass
class ListPackagesCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:
        if subcommands:
            raise ValueError(f"Invalid subcommand {subcommands}")

        arg_parser = argparse.ArgumentParser(
            description=("List the available packages for download. "),
            prog=_join(PROG_NAME + " " + self.context),
        )

        return arg_parser

    def parse(self, argv: list[str]) -> IListPackagesArgs:
        return typing.cast(
            IListPackagesArgs, self.get_argument_parser().parse_args(argv)
        )

    def execute(self, argv: list[str]) -> None:
        self.parse(argv)
        _init_logger(log, "WARNING", True)
        pkg_mgr = PkgManager()
        for name, versions in pkg_mgr.iter_packages():
            for version in versions.keys():
                print(name, version)


class IListArgs(Protocol):
    category: Literal["packages", "generators", "installed"]

    subargs: list[str]


@dataclass
class ListCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:
        if subcommands:
            cmd, *others = subcommands
            match cmd:
                case "packages":
                    return AvailPackageCommand(
                        _join(self.context, "packages")
                    ).get_argument_parser(*others)
                case "installed":
                    return AvailCommand(
                        _join(self.context, "installed")
                    ).get_argument_parser(*others)
                case "generators":
                    return AvailGeneratorsCommand(
                        _join(self.context, "generators")
                    ).get_argument_parser(*others)

        arg_parser = argparse.ArgumentParser(
            description=("List generator or package available for installation"),
            prog=_join(PROG_NAME + " " + self.context),
        )
        arg_parser.add_argument(
            "category", choices=["packages", "generators", "installed"]
        )
        arg_parser.add_argument(
            "subargs", nargs=argparse.REMAINDER, help=argparse.SUPPRESS
        )
        return arg_parser

    def parse(self, argv: list[str]) -> IListArgs:
        return typing.cast(IListArgs, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        _init_logger(log, "WARNING", True)
        match args.category:
            case "packages":
                ListPackagesCommand(_join(self.context, "packages")).execute(
                    args.subargs
                )
            case "installed":
                AvailCommand(_join(self.context, "installed")).execute(args.subargs)
            case "generators":
                ListGeneratorsCommand(_join(self.context, "generators")).execute(
                    args.subargs
                )

            case _:
                raise ValueError(f"Invalid Category {args.category}")


class IHelpArgs(Protocol):
    category: Literal["export", "run", "install" "avail" "list" "info"] | None
    subargs: list[str]


@dataclass
class HelpCommand:
    context: str = ""

    def get_argument_parser(self) -> argparse.ArgumentParser:
        arg_parser = argparse.ArgumentParser(
            description="Print command help",
            prog=_join(PROG_NAME, self.context),
        )
        arg_parser.add_argument(
            "category",
            nargs="?",
            default=None,
            choices=["export", "run", "install", "avail", "list", "info"],
        )
        arg_parser.add_argument(
            "subargs", nargs=argparse.REMAINDER, help=argparse.SUPPRESS
        )
        return arg_parser

    def parse(self, argv: list[str]) -> IHelpArgs:
        return typing.cast(IHelpArgs, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        match args.category:
            case "export":
                cmd_arg_parser = ExportCommand("export").get_argument_parser(
                    *args.subargs
                )
            case "run":
                cmd_arg_parser = RunCommand("run").get_argument_parser(*args.subargs)
            case "install":
                cmd_arg_parser = InstallCommand("install").get_argument_parser(
                    *args.subargs
                )
            case "avail":
                cmd_arg_parser = AvailCommand("avail").get_argument_parser(
                    *args.subargs
                )
            case "list":
                cmd_arg_parser = ListCommand("list").get_argument_parser(*args.subargs)
            case "info":
                cmd_arg_parser = InfoCommand("info").get_argument_parser(*args.subargs)

            case None:
                cmd_arg_parser = MainCommand("").get_argument_parser()
            case _:
                raise ValueError(f"Invalid Category {args.category}")
        cmd_arg_parser.print_help()


def show_info(text: str, raw: bool = False, style: str = DEFAULT_MD_STYLE) -> None:
    if raw:
        print(text)
    try:
        import rich.console
        import rich.markdown
    except ImportError:
        print(text)
    else:
        # to get a list of theme from pygments.styles import get_all_styles
        # list(get_all_styles())
        console = rich.console.Console(
            width=min(100, shutil.get_terminal_size().columns)
        )
        console.print(rich.markdown.Markdown(text, code_theme=style))


class IInfoTemplateArgs(Protocol):
    template_name: str
    raw: bool
    style: str


def add_info_argument(arg_parser: argparse.ArgumentParser) -> None:
    try:
        from pygments.styles import get_all_styles
    except ImportError:
        choices = None
    else:
        choices = list(get_all_styles())

    arg_parser.add_argument(
        "-r",
        "--raw",
        action="store_true",
        help="Return the raw description text. By default Markdown is rendered for console",
        default=False,
    )
    arg_parser.add_argument(
        "--style",
        help=("Style name for the console output "),
        default=DEFAULT_MD_STYLE,
        choices=choices,
    )


@dataclass
class InfoTemplateCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:

        if subcommands:
            raise ValueError(f"Invalid subcommand {subcommands}")

        arg_parser = argparse.ArgumentParser(
            description=("Show Information about a specific template"),
            prog=_join(PROG_NAME + " " + self.context),
        )
        arg_parser.add_argument("template_name")
        add_info_argument(arg_parser)
        return arg_parser

    def parse(self, argv: list[str]) -> IInfoTemplateArgs:
        return typing.cast(
            IInfoTemplateArgs, self.get_argument_parser().parse_args(argv)
        )

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        _init_logger(log, "WARNING", True)
        resources = ProgramResources()
        resources.update()
        desc = resources.get_template_description(args.template_name)
        show_info(desc, args.raw, args.style)


class IInfoOtherArgs(Protocol):
    raw: bool
    style: str


@dataclass
class InfoOtherCommand:
    topic: None | Literal["model", "config", "custom_model"]
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:

        if subcommands:
            raise ValueError(f"Invalid subcommand {subcommands}")

        arg_parser = argparse.ArgumentParser(
            description=("Show Information about a specific topic"),
            prog=_join(PROG_NAME + " " + self.context),
        )

        add_info_argument(arg_parser)
        return arg_parser

    def parse(self, argv: list[str]) -> IInfoOtherArgs:
        return typing.cast(IInfoOtherArgs, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        _init_logger(log, "WARNING", True)
        match self.topic:
            case None:
                desc = general_info
            case "model":
                desc = model_info
            case "config":
                desc = config_info
            case "custom_model":
                desc = custom_model_info
            case _:
                raise ValueError(f"Invalid info topic {self.topic}")
        show_info(desc, args.raw, args.style)


class IInfoArgs(Protocol):
    category: Literal["template", "model", "config", "custom_model"]
    subargs: list[str]


@dataclass
class InfoCommand:
    context: str = ""

    def get_argument_parser(self, *subcommands: str) -> argparse.ArgumentParser:

        if subcommands:
            cmd, *others = subcommands
            match cmd:
                case "template":
                    return InfoTemplateCommand(
                        _join(self.context, "template")
                    ).get_argument_parser(*others)
                case "model":
                    return InfoOtherCommand(
                        "model", _join(self.context, "model")
                    ).get_argument_parser(*others)
                case "config":
                    return InfoOtherCommand(
                        "config", _join(self.context, "config")
                    ).get_argument_parser(*others)
                case "custom_model":
                    return InfoOtherCommand(
                        "custom_model", _join(self.context, "custom_model")
                    ).get_argument_parser(*others)

        arg_parser = argparse.ArgumentParser(
            description="Print some information",
            prog=_join(PROG_NAME, self.context),
        )
        arg_parser.add_argument(
            "category",
            choices=["template", "model", "config", "custom_model"],
            nargs="?",
        )
        arg_parser.add_argument(
            "subargs", nargs=argparse.REMAINDER, help=argparse.SUPPRESS
        )
        return arg_parser

    def parse(self, argv: list[str]) -> IInfoArgs:
        return typing.cast(IInfoArgs, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        match args.category:
            case "template":
                return InfoTemplateCommand(_join(self.context, "template")).execute(
                    args.subargs
                )
            case None | "model" | "config" | "custom_model":
                return InfoOtherCommand(
                    args.category, _join(self.context, args.category or "")
                ).execute(args.subargs)
            case _:
                raise ValueError(f"Invalid Category {args.category}")


class IMainArgs(Protocol):
    subcommand: Literal["export" "run", "install", "help", "avail", "list", "info"]
    subargs: list[str]


@dataclass
class MainCommand:
    context: str = ""

    def get_argument_parser(self) -> argparse.ArgumentParser:
        arg_parser = argparse.ArgumentParser(
            description=dedent(
                """
           Toolbox to export code from tmc file. 
           It also serves as template package manager, .Net installer (Linux only) 
           and generator engine installer. 

           Available commands:
               export:  export code using a model.yaml file as input
               run:     run generator with command lien argument only
               install: install a specific template package, generator or .Net
               list:    List available or installed packages, templates or generators  
               info:    Display detailed information about something (e.g. info template) 
               help:    print help for specific commands
            """
            ),
            prog=_join(PROG_NAME, self.context),
            formatter_class=argparse.RawTextHelpFormatter,
            epilog="""Other options depend on the used command. See specific `help <command>`""",
        )
        arg_parser.add_argument(
            "subcommand",
            choices=["export", "run", "install", "avail", "list", "info", "help"],
        )
        arg_parser.add_argument(
            "subargs", nargs=argparse.REMAINDER, help=argparse.SUPPRESS
        )
        return arg_parser

    def parse(self, argv: list[str]) -> IMainArgs:
        return typing.cast(IMainArgs, self.get_argument_parser().parse_args(argv))

    def execute(self, argv: list[str]) -> None:
        args = self.parse(argv)
        match args.subcommand:
            case "export":
                ExportCommand(_join(self.context, "export")).execute(args.subargs)
            case "run":
                RunCommand(_join(self.context, "run")).execute(args.subargs)
            case "install":
                InstallCommand(_join(self.context, "install")).execute(args.subargs)
            case "help":
                HelpCommand(_join(self.context, "help")).execute(args.subargs)
            case "avail":
                AvailCommand(_join(self.context, "avail")).execute(args.subargs)
            case "list":
                ListCommand(_join(self.context, "list")).execute(args.subargs)
            case "info":
                InfoCommand(_join(self.context, "info")).execute(args.subargs)

            case _:
                self.get_argument_parser().print_usage()


general_info = f"""
# Info command 

Info command allows to print in-terminal documentation. Like this one. 
Available topics are: 

- `template <name>` where `name` is the template name 
- `model` doc about the model.yaml file 
- `config` doc about the template configuration in model.yaml file
- `custom_model` doc on how to build a device model without tmc file

## Example 

```shell
> {PROG_NAME} info template simulator 
> {PROG_NAME} info model 
```


"""

model_info = """

# Model 

The model is defined as a yaml file containing all necessary information to 
run the code generation.  

Example:
    
```yaml
name: Lamp
extraction_root: MAIN.Lamp001
tmc_file: "./model_data/Lamp.tmc"
scxml_file: "./model_data/lamp.scxml.xml"
templates: ["simulator", "client"]
config_includes: ["../model_config.yaml", "./model_data/lamp_error.yaml"]
configs:
    base:
       Rename: True 
    client:
       PkgPath: '{{Name|lower}}/client'
    simulator:
       PkgPath: '{{Name|lower}}/sim'
```

## Parameters 

- `name` (str, mendatory)  
  This is the Name of the exported device.The name is used to build code 
  file names and to build classes. 
  The case of the first letter change function to context 
  (file name, class name, ...). It is recommanded to use a capital letter for 
  better clarity. 
>
- `templates` (list[str])  
  A list of template names to be executed. The templates shall be installed
  before, they are grouped into "packages". To install a package:  

  ```shell
  > tmcExport install package <Package Name>  
  # To know the list of known packages:  
  > tmcExport list packages  
  # And installed templates:  
  > tmcExport list installed templates
  ```
>
- `configs`   
  This is a dictionary of per templates configuration. 
  For more info:  
    
    ```shell
    > tmcExport info config  
    ```
>
- `config_includes` (list[str])
  A list of yaml file containing valid content of configs. The file contents 
  must be a dictionary of template name / template config dictionary.
  The file path is relative to where the model is defined or absolute. This can
  also be an url.
>
- `scxml_file` (str)
  An optional scxml file containing the device State Machine.
  The path is relative to model location or absolute, or an url.

### Using TMC file 

The TMC file is generated by TwinCat3. It contains all information about the 
local control TC3 code (classes, enums, properties, ...). It is used to by the 
the generator to extract all informations for templating 

- `tmc_file` (str)
  tmc location (relative, absolute or url)
>
- `extraction_root` (str)
  The extraction starts from a given point inside the PLC Project. This is usually 
  a device instance, e.g. :

    ```yaml
    extraction_root: MAIN.Shutter001     
    ```

### Using a custom Model 

If no TMC file is available, one can still use tmc export by defining the model
classes, enums and properties. It shall be defined inside the `model` dictionary

- `model` dict 
  custom model content, for more info: 

      > tmcExport info custom_model





"""

config_info = """

# Template Configs 

The configs is a dictionary of per template configuration. For each templates
a scriban variable / scirban value can be given. Scriban is the templating 
langage used by the generator (https://github.com/scriban/scriban).

The configuration can be done per-template but also into template dependencies 
this allows to set the configuration for several templates without having 
to duplicate content.

for instance: 

```yaml
name: Shutter 
extraction_root: MAIN.Shutter001
tmc_file: "./model/Shutter.tmc"
scxml_file: "./model/shutter.scxml.xml"
templates: ["simulator", "client"]
config_includes: ["../model_config.yaml", "model/shutter_errors.yaml"]

configs:
  python:
    RenamedProperties['sRPCErrorText']: 'rpc_error_text'
    SrcPath: 'ifw/fcfsim/devices/{{Name|lower}}'
  path:
    ConfigPath: 'config/ifw/fcfsim/devices/{{Name|lower}}'
    SchemaPath: 'schema/ifw/fcfsim/devices/{{Name|lower}}'
    ExamplePath: 'config/ifw/fcfsim/example'
    PkgPath: ''
  client:
    PkgPath: 'cli'
  cimulator: 
    PkgPath: 'simu'
```

The above configuration will work on "simulator" and "client" templates because
they both depend on the "python" template and the "path" template.

However, in the above example the `PkgPath` (part of path properties) is 
overwriten and specified to "client" and "simulator" template. 

To list the template parameters, e.g.:  

    > tmcExport info template simulator

## Notes 

- String value in config can be a valid Scriban template as illustrated in the 
  example above. However, initialy, the scriban variables are limited to what 
  the generator is exporting plus the `Name` and `TemplateName` string variable.
  Other vairables might be availble if they have been declared before in the 
  template config or in the dependency tree.

- In yaml the key can be a Scriban complete path to a scriban variable: 

    ```yaml
    configs:
       base:
          EnumTexts['E_MOTOR_ERROR']['LOCAL']: 'Control not allowed. Motor in Local mode'
    ```

"""

custom_model_info = """
Custom Model can be defined inside the model file to replace a TMC file.

One can define classes, properties, enums and methods

The example bellow is self-explainatory 

```yaml
model:
  classes:
      - name: SwitchStat 
        properties:
          - name: "bOpened"
            type: "Boolean"
          - name: "nState"
            type: "int"
            default: 0
            
      - name: SwitchCfg
        properties:
          - name: nOpeningTimeout
            type: int
            comment: "Time for Opening"
          - name: lrAnalogFeedback
            type: Double
            comment: "Analog Feedback relative scale"
          - name: arSomeArray
            type: Double
            size: 4

  properties:
    - name: stat 
      type: "SwitchStat"
      access: 'r' # OPC-UA access
    - name: cfg
      type: SwitchCfg
      access: 'r'
  
  methods:
    - name: turn_on
      inputs:
        - name: lrDelay 
          type: Double 
          comment: "Turn On after a delay in second"
      outputs:
        - name: ReturnValue
          type: Int16 
    - name: turn_off
      outputs:
        - name: ReturnValue
          type: Int16 


  enums:
    - name: E_SWITCH_STATE
      entries:
        - label: 'OK'
          value: 0

```

## Notes 

- Names of properties, classes, enums, etc ... can be conform to TC3 naming. 
  However they migh be converted by the template in the specific language naming
  convention (see `Rename` base template config parameter).
>
- Methods can only be defined at root level (generator limitation)
>
- Like on TwinCat the `access`` (OPC-UA access) is hierachical it can be a 
  integer 0 or string:

    | access     |  decription | 
    |------------|-------------|
    | 0, "?", "" | Unknown (take the parent access) |
    | 1, "r"     | Read Only   |
    | 2, "w"     | Write Only  |
    | 3, "rw"    | Read Write  | 


- Avilable `type` for properties or method arguments: 

    | type       | Ua  Variant  |
    |------------|--------------|
    |Boolean     |     1   |
    |SByte       |     2   |
    |Byte        |     3   |
    |Int16       |     4   |
    |UInt16      |     5   |
    |Int32       |     6   |
    |UInt32      |     7   |
    |Int64       |     8   |
    |UInt64      |     9   |
    |Float       |     10  |
    |Double      |     11  |
    |String      |     12  |
    |DateTime    |     13  |
    |ByteString  |     15  |


  Other types shall point to a custom Class name
>
- `size` is an integer to define an array size. It can also be a tuple of
  two integers to defining the left and right bound:  
  `size: [1,4]` represent an array of 4 elements , with a left bound at 1  
  `size: 4` is equivalent to `size: [0,3]`
    
"""


def main(argv: list[str]) -> int:
    MainCommand().execute(argv)
    return 0


######################################################################


if __name__ == "__main__":
    main(sys.argv[1:])
