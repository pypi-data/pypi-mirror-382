from setuptools import setup, find_packages

__VERSION__ = "1.0b1"
__NAME__ = "udma"

with open("README.md", encoding="utf-8") as readme_file:
    README = readme_file.read()

setup(
    name=__NAME__,
    version=__VERSION__,
    author="MLAB-ICTP Team",
    author_email="wflorian@ictp.it",
    description=(
        "Automatic and platform-independent CLI communication system via Ethernet "
        "with ComBlock support."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/ictp-mlab/udma",
    license="GPLv3", 
    python_requires=">=3.6",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "cmd2>=2.4.3",
        "appdirs>=1.4.4",
        "tqdm>=4.58.0",
    ],
    entry_points={
        "console_scripts": [
            "udma_cli=cli.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
)
