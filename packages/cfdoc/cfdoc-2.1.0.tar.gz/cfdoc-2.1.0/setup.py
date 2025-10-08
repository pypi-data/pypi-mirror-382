"""setup.py for cfdoc."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from setuptools import find_packages, setup

__version__ = (resources.files('cfdoc') / 'VERSION').read_text().strip()

REPO_URL = 'https://bitbucket.org/murrayandrews/cfdoc/src/master/'
REQUIRES_PYTHON = '>=3.9.0'


# ------------------------------------------------------------------------------
def find_cli_entry_points(*cli_pkg: str, entry_point: str = 'main') -> list[str]:
    """Find CLI entry point scripts in the specified CLI packages."""

    entry_points = []
    for pkg in cli_pkg:
        pkg_path = Path(pkg.replace('.', '/'))
        if not pkg_path.is_dir():
            continue
        entry_points.extend(
            [
                f'{f.stem.replace("_", "-")}={pkg}.{f.stem}:{entry_point}'
                for f in pkg_path.glob('*.py')
                if not f.name.startswith('_')
            ]
        )
    return entry_points


# ------------------------------------------------------------------------------
# Import README.md and use it as the long-description. Must be in MANIFEST.in
with open('PYPI.md') as fp:
    long_description = '\n' + fp.read()

# ------------------------------------------------------------------------------
# Get pre-requisites from requirements.txt. Must be in MANIFEST.in
with open('requirements.txt') as fp:
    required = [s.strip() for s in fp.readlines()]

# ------------------------------------------------------------------------------
packages = find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*'])
setup(
    name='cfdoc',
    version=__version__,
    packages=packages,
    entry_points={
        'console_scripts': find_cli_entry_points(*(p for p in packages if p.endswith('.cli')))
    },
    url=REPO_URL,
    license='3-Clause BSD License',
    author='Murray Andrews',
    description='Extract documentation from an AWS CloudFormation Template',
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms=['macOS', 'Linux'],
    python_requires=REQUIRES_PYTHON,
    install_requires=required,
    package_data={
        'cfdoc': ['man/*'],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
)
