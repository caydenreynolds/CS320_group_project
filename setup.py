from setuptools import find_packages, setup

INSTALL_REQUIRES = [
    'sqlalchemy',
    'flask',
    'requests'
]

DEV_REQUIRES = [
    'rope',
    'pytest',
    'autopep8',
    'pylint'
]

ENTRY_POINTS = {
    'console_scripts': [
        'prototype_server=ypd.scripts.prototype_server:main',
    ]
}

setup(
    name="ycp_project_database",
    version="0.0.1",
    packages=find_packages("src"),
    author='abaldwin3, creynolds1, gholley, llewis9',
    description = "Python Server for project_proposer",
    install_requires = INSTALL_REQUIRES,
    extra_require = {
        "dev": DEV_REQUIRES
    },
    package_dir={'': 'src'},
    entry_points=ENTRY_POINTS
)