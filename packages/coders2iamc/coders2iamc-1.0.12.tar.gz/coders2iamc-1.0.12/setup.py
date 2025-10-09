# coders-to-iamc/setup.py

from os.path import abspath, dirname, join

from setuptools import find_packages, setup

# Define the directory containing this file
this_dir = abspath(dirname(__file__))

# Read the long description from README.md
with open(join(this_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read the global requirements.txt
with open(join(this_dir, "requirements.txt"), encoding="utf-8") as f:
    requirements = f.read().splitlines()


setup(
    name="coders2iamc",
    version="1.0.12",
    description="Scripts that pull data from the CODERS database and format it for use in the IAMC format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/sesit/coders-to-iamc",
    install_requires=requirements,
    packages=find_packages(include=["coders_to_iamc"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",  # Specify the Python versions you support
    package_data={"": ["*.yaml"]},
)
