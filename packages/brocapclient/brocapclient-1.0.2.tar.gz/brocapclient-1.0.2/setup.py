from __future__ import print_function
import sys
if sys.version_info < (3,):
    print("Python 2 not supported by BroCapGpt.")
    sys.exit(-1)

from pathlib import Path
from pkg_resources import parse_requirements
from setuptools import setup


NAME = 'brocapclient'
EMAIL = 'dev@brocapgpt.com'
AUTHOR = 'Nikita Markov'
with open('libpy_client/version.txt', 'r') as f:
    VERSION = f.read()
with open("requirements.txt", "rt") as requirements_txt:
    REQUIRED = [str(requirement) for requirement in parse_requirements(requirements_txt)]

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name=NAME,
    version=VERSION,
    author_email=EMAIL,
    author=AUTHOR,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['brocapclient', 'brocapclient.requests'],
    package_dir={"brocapclient": 'libpy_client'},
    package_data={'': ['version.txt']},
    include_package_data=True,
    py_modules=["brocapclient"],
    python_requires='>=3.8',
    install_requires=REQUIRED,
    keywords="""
                captcha 
				hcaptcha
				funcaptcha
                foxcaptcha
				python3
				python-library
				brocapgpt
               """,
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Development Status :: 5 - Production/Stable",
        "Framework :: AsyncIO",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ]
)