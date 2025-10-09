# coding: utf-8
from __future__ import absolute_import

from os.path import abspath
from os.path import dirname
from os.path import join
import re

from pkg_resources import Requirement
from setuptools import find_packages
from setuptools import setup


_COMMENT_RE = re.compile(r'(^|\s)+#.*$')


def _get_requirements(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            line = _COMMENT_RE.sub('', line)
            line = line.strip()
            if line.startswith('-r '):
                for req in _get_requirements(
                    join(dirname(abspath(file_path)), line[3:])
                ):
                    yield req
            elif line:
                req = Requirement(line)
                req_str = req.name + str(req.specifier)
                if req.marker:
                    req_str += '; ' + str(req.marker)
                yield req_str


def main():
    setup(
        name='m3-dev-utils',
        author='Andrey Chagochkin',
        author_email='andrey.chagochkin@bars-open.ru',
        description=(
            u'Инструментарий разработчика веб-приложений на платформе M3.'
        ),
        url='https://stash.bars-open.ru/projects/M3/repos/m3-dev-utils',
        package_dir={'': 'src'},
        packages=find_packages('src'),
        include_package_data=True,
        classifiers=[
            'Intended Audience :: Developers',
            'Environment :: Web Environment',
            'Natural Language :: Russian',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.6',
            'Development Status :: 5 - Production/Stable',
            'Framework :: Django :: 1.9',
            'Framework :: Django :: 1.10',
            'Framework :: Django :: 1.11',
        ],
        dependency_links=(
            'https://pypi.bars-open.ru/simple/m3-builder',
        ),
        setup_requires=(
            'm3-builder>=1.2,<2',
        ),
        install_requires=tuple(_get_requirements('requirements/prod.txt')),
        set_build_info=dirname(__file__),
    )


if __name__ == '__main__':
    main()
