# coding: utf-8
"""Модуль для работы с зависимостями приложения."""
from functools import wraps
from os.path import normcase
from os.path import realpath
from pathlib import Path
import subprocess
import sys

from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution
from pkg_resources import working_set


def is_package_installed(name):
    """Возвращает True, если пакет с указанным именем установлен.

    :param str name: имя пакета.

    :rtype: bool
    """
    try:
        get_distribution(name)
    except DistributionNotFound:
        return False
    else:
        return True


def install_packages(*names):
    """Устанавливает пакеты с указанными именами.

    .. code-block: python

       install_packages('fabric3>=1', 'pip>9', 'django>=1.11,<2')
    """
    if names:
        params = [
            Path(sys.executable).parent.joinpath('pip').as_posix(),
            'install',
            '--quiet',
        ]
        params.extend(names)

        cmd = subprocess.Popen(params)
        if cmd.wait() != 0:
            raise RuntimeError('Package install failed: ' + ', '.join(names))


def require(*packages):
    """Декоратор, устанавливающий указанные пакеты, перед запуском функции."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            non_installed_packages = [
                package
                for package in packages
                if not is_package_installed(package)
            ]
            if non_installed_packages:
                install_packages(*non_installed_packages)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_dependent_packages(package_name):
    """Возвращает пакеты, от которых зависит указанный пакет.

    :param str package_name: имя проверяемого пакета.
    :return генератор по названиям пакетов, от которых зависит текущий.
    :rtype: generator
    """
    distribution = get_distribution(package_name)

    for requirement in distribution.requires():
        yield get_distribution(requirement.name).project_name
        for name in get_dependent_packages(requirement.name):
            yield name


def get_installed_distributions():
    """Возвращает информацию об установленных в окружении пакетах.

    :rtype: list of :class:`~pkg_resources.Distribution`.
    """
    stdlib_pkgs = ('python', 'wsgiref')
    if sys.version_info >= (2, 7):
        stdlib_pkgs += ('argparse',)

    # pylint: disable=not-an-iterable
    for dist in working_set:
        if (
            dist.key not in stdlib_pkgs and
            normcase(realpath(dist.location)).startswith(sys.prefix)
        ):
            yield dist
