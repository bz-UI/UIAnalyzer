from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, "r", encoding="utf-8") as fh:
        return fh.read().splitlines()


setup(
    name="UIAnalyzer",
    version="0.2.0",
    author="TSKGHS17",
    author_email="23210240317@m.fudan.edu.cn",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TSKGHS17/UIAnalyzer",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['Assets/*.ttf'],
    },
    license="GPL-3.0-or-later",
    license_files=('LICENSE',),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=parse_requirements("requirements.txt"),
)
