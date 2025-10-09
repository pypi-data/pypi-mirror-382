# Copyright (C) 2024 Red Hat, Inc.
# SPDX-License-Identifier: MIT

import os
import re
import shutil
import subprocess
import tempfile
from enum import IntEnum, StrEnum, auto
from pathlib import Path
from typing import Iterator
import yaml


class FqException(Exception):
    DEFAULT_MESSAGE: str = ""

    def __init__(self, *args, msg=None, **kwargs):
        if not msg:
            msg = self.DEFAULT_MESSAGE

        super().__init__(msg.format(args), *args, **kwargs)


class NotSupported(FqException):
    DEFAULT_MESSAGE: str = "no supported package manager available"


class PackageNotFound(FqException):
    DEFAULT_MESSAGE: str = "package not found."


class NoPackageManager(FqException):
    DEFAULT_MESSAGE: str = "no package manager is installed"


class NoPackageRepo(FqException):
    DEFAULT_MESSAGE: str = "no such package repositories"


class NoBranchInPackageRepo(FqException):
    DEFAULT_MESSAGE: str = "no such branches available in package repository"


class InvalidFormat(FqException):
    DEFAULT_MESSAGE: str = "Invalid fmf format"


class Font2Package:

    @classmethod
    def get_source_package_name(cls, pkg) -> Iterator[str]:
        if not isinstance(pkg, list):
            pkg = [pkg]
        for p in pkg:
            cmdline = ['rpm', '-q', '--qf', '%{version}-%{release}', p]
            retver = subprocess.run(cmdline, capture_output=True,
                                    check=False)
            if retver.returncode != 0:
                raise PackageNotFound(p)
            cmdline = ['rpm', '-q', '--qf', '%{sourcerpm}', p]
            retsrpm = subprocess.run(cmdline, capture_output=True,
                                     check=False)
            if retsrpm.returncode != 0:
                raise PackageNotFound(p)
            yield re.sub(fr'-{retver.stdout.decode("utf-8")}.*', '',
                         retsrpm.stdout.decode('utf-8'))

    @classmethod
    def get_package_name_from_file(cls, fontfile) -> Iterator[str]:
        if shutil.which('rpm'):
            cmdline = ['rpm', '-qf', '--qf', '%{name}', fontfile]
            retval = subprocess.run(cmdline, capture_output=True,
                                    check=False)
            if retval.returncode != 0:
                raise PackageNotFound(fontfile)
            yield retval.stdout.decode('utf-8')
        else:
            raise NotSupported()


class VarList(IntEnum):
    PACKAGE = 0
    FONT_ALIAS = 1
    FONT_LANG = 2
    FONT_WIDTH = 3
    FONT_FAMILY = 4
    DEFAULT_SANS = 5
    DEFAULT_SERIF = 6
    DEFAULT_MONO = 7
    DEFAULT_EMOJI = 8
    DEFAULT_MATH = 9
    FONT_LANG_EXCLUDE_FILES = 10
    FONT_VALIDATE_EXCLUDE_FILES = 11


class UpperStrEnum(StrEnum):

    @staticmethod
    def _generate_next_value_(name, *args):
        return name.upper()


class ParamList(UpperStrEnum):
    PACKAGE = auto()
    FONT_ALIAS = auto()
    FONT_LANG = auto()
    FONT_WIDTH = auto()
    FONT_FAMILY = auto()
    DEFAULT_SANS = auto()
    DEFAULT_SERIF = auto()
    DEFAULT_MONO = auto()
    DEFAULT_EMOJI = auto()
    DEFAULT_MATH = auto()
    FONT_LANG_EXCLUDE_FILES = auto()
    FONT_VALIDATE_EXCLUDE_FILES = auto()


class PackageRepoCache:

    def __init__(self, product: str = 'fedora'):
        self._cache = {}
        if product == 'fedora':
            self._url = 'https://src.fedoraproject.org/rpms/'
            self._branch = 'f{}'
        elif product == 'centos':
            self._url = 'https://gitlab.com/redhat/centos-stream/rpms/'
            self._branch = 'c{}s'
        else:
            raise RuntimeError(f'unknown product: {product}')

    def add(self, pkg: str, repodir: tempfile.TemporaryDirectory):
        if pkg in self._cache:
            self._cache[pkg].cleanup()
        self._cache[pkg] = repodir

    def get(self, pkg: str, branch: str = 'rawhide') -> tempfile.TemporaryDirectory:
        if pkg not in self._cache:
            tmpdir = tempfile.TemporaryDirectory()
            cmdline = ['git', 'clone', self._url + f'{pkg}.git', tmpdir.name]
            retval = subprocess.run(cmdline, capture_output=True,
                                    check=False)
            if retval.returncode != 0:
                tmpdir.cleanup()
                raise NoPackageRepo(pkg)
            self.add(pkg, tmpdir)
        else:
            tmpdir = self._cache[pkg]
        cwd = Path.cwd()
        try:
            os.chdir(tmpdir.name)
            cmdline = ['git', 'switch', branch if branch == 'rawhide' else self._branch.format(branch)]
            retval = subprocess.run(cmdline,
                                    capture_output=True,
                                    check=False)
        finally:
            os.chdir(cwd)
        if retval.returncode != 0:
            tmpdir.cleanup()
            raise NoBranchInPackageRepo(branch)

        return tmpdir


class PackageRepo:

    def __init__(self, cache, pkg, family: str = None, branch: str = 'rawhide'):
        self._is_default = {}
        self._lang_coverage = []
        if not shutil.which('git'):
            raise RuntimeError('No git installed')
        srpm = list(Font2Package.get_source_package_name(pkg))[0]
        tmpdir = cache.get(srpm, branch)
        self._parse_plan(tmpdir.name, pkg, family)

    def is_default_sans(self, family, lang):
        return family in self._is_default and self._is_default[family]['sans'].get(lang, 0)

    def is_default_serif(self, family, lang):
        return family in self._is_default and self._is_default[family]['serif'].get(lang, 0)

    def is_default_mono(self, family, lang):
        return family in self._is_default and self._is_default[family]['mono'].get(lang, 0)

    @property
    def languages(self):
        return self._lang_coverage

    def _parse_plan(self, repo: str, pkg: str, family: str):
        p = Path(repo) / 'plans'
        if p.exists() and p.is_dir():
            for fn in p.glob('**/*.fmf'):
                with open(fn, encoding='utf-8') as f:
                    fmf = yaml.safe_load(f)
                    if 'environment' not in fmf:
                        raise InvalidFormat('environment')
                    env = fmf['environment']
                    if 'VARLIST' in env:
                        with open(p / env['VARLIST'], encoding='utf-8') as v:
                            for row in v.readlines():
                                if re.match('#', row):
                                    continue
                                data = row.strip().split(';')
                                self._parse_params(data, VarList, pkg, family)
                    else:
                        self._parse_params(env, ParamList, pkg, family)

    def _parse_params(self, data: list, enum, pkg: str, family: str) -> bool:
        if data[enum.PACKAGE] != pkg:
            return False
        if family is not None and data[enum.FONT_FAMILY] != family:
            return False

        def set_default(v, idx, default):
            try:
                return v[idx]
            except (IndexError, KeyError):
                return default

        ls = [ls.replace('-', '_') for ls in set_default(data,
                                                         enum.FONT_LANG,
                                                         'en').split(',')]
        set1 = set(self._lang_coverage)
        set2 = set(ls)
        newls = sorted(list(set2 - set1))
        self._lang_coverage += newls

        for l in ls:
            if data[enum.FONT_FAMILY] not in self._is_default:
                self._is_default[data[enum.FONT_FAMILY]] = {
                    'sans': {}, 'serif': {}, 'mono': {}, 'emoji': {}, 'math': {}
                }
            is_default = self._is_default[data[enum.FONT_FAMILY]]
            if enum == VarList or enum.DEFAULT_SANS in data:
                is_default['sans'][l] = int(set_default(data,
                                                        enum.DEFAULT_SANS,
                                                        0))
            if enum == VarList or enum.DEFAULT_SERIF in data:
                is_default['serif'][l] = int(set_default(data,
                                                         enum.DEFAULT_SERIF,
                                                         0))
            if enum == VarList or enum.DEFAULT_MONO in data:
                is_default['mono'][l] = int(set_default(data,
                                                        enum.DEFAULT_MONO,
                                                        0))
        return True


if __name__ == '__main__':
    _pkg = list(Font2Package.get_package_name_from_file('/usr/share/fonts/google-noto-vf/'
                                                        'NotoSans[wght].ttf'))
    print(_pkg)
    print(_pkg[0])
    _srpm = list(Font2Package.get_source_package_name(_pkg))
    print(_srpm)
    _cache = PackageRepoCache()
    for _p in _pkg:
        _repo = PackageRepo(_cache, _p)
        print(_repo)
        print(_repo.languages)
        print(_repo._is_default)
    _repo = PackageRepo(_cache, 'google-noto-sans-fonts')
    print(_repo)
    print(_repo._is_default)
    _repo = PackageRepo(_cache, 'abattis-cantarell-vf-fonts')
    print(_repo)
    print(_repo._is_default)
    _repo = PackageRepo(_cache, 'google-noto-sans-cjk-vf-fonts')
    print(_repo._is_default)
    _repo = PackageRepo(_cache, 'google-noto-sans-cjk-vf-fonts', 40)
    print(_repo._is_default)
    _pkg = list(Font2Package.get_package_name_from_file('/usr/share/fonts/vazirmatn-vf-fonts/'
                                                        'Vazirmatn[wght].ttf'))
    print(_pkg)
    print(_pkg[0])
    for _p in _pkg:
        _repo = PackageRepo(_cache, _p)
        print(_repo)
        print(_repo._is_default)
