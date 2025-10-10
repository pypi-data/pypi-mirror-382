import os
from setuptools import setup, find_packages

# Read the contents of README.md for the long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="enkryptai-sdk",  # This is the name of your package on PyPI
    # NOTE: Also change this in .github/workflows/test.yaml
    version="1.0.25", # Update this for new versions
    description="A Python SDK with guardrails and red teaming functionality for API interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Enkrypt AI Team",
    author_email="software@enkryptai.com",
    url="https://github.com/enkryptai/enkryptai-sdk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Update this if you choose a different license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        # List runtime dependencies here, e.g., "requests>=2.25.1",
    ],
)
