####################################################
# setup.py for the 'cmpparis' library
# Created by: Sofiane Charrad
####################################################

import setuptools

with open("README_PYPI.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("CHANGELOG.md", "r", encoding="utf-8") as fh:
    changelog = fh.read()

setuptools.setup(
    name="cmpparis",
    version="1.13.0",
    author="Sofiane Charrad | Hakim Lahiani",
    author_email="s.charrad@cmp-paris.com | h.lahiani@cmp-paris.com",
    description="Une bibliothèque pour CMP",
    long_description=long_description + "\n\n" + changelog,
    long_description_content_type="text/markdown",
    url="https://codecatalyst.aws/spaces/CMP/projects/Coding-Tools/source-repositories/python-cmpparis-lib/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  # Changé de 3.6 à 3.7 pour dataclasses
    install_requires=[
        "requests",
        "moto",
        "paramiko",
        "pyodbc",
        "pymssql==2.3.4",
        "Office365-REST-Python-Client",
        "pymongo",
        "pandas",
        "lxml",
        "pyyaml",
    ],
    extras_require={
        'dev': [
            'mkdocs>=1.5.0',
            'mkdocs-material>=9.0.0',
            'mkdocstrings[python]>=0.24.0',
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ]
    }
)