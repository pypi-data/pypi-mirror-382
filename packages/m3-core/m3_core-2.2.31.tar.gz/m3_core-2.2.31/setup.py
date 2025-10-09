# coding: utf-8
from os.path import (
    dirname,
    join,
)

from setuptools import (
    find_packages,
    setup,
)


def _read(file_name):
    with open(join(dirname(__file__), file_name)) as f:
        return f.read()


setup(
    name='m3-core',
    url='https://bitbucket.org/barsgroup/m3-core',
    license='MIT',
    author='BARS Group',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description=_read('DESCRIPTION.md'),
    long_description=_read('README.md'),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.2',
    ],
    dependency_links=('http://pypi.bars-open.ru/simple/m3-builder',),
    setup_requires=('m3-builder>=1.2.0,<2',),
    install_requires=(
        'six>=1.11,<2',
        'm3-builder>=1.2.0,<2',
        'm3_django_compatibility>=1.12.0,<2',
        'django>=1.4,<5.0',
    ),
    set_build_info=dirname(__file__),
)
