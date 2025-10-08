from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
readme_file = this_dir / "README.md"

setup(
    name="taxman-common",
    version="0.1.0",
    description="Common utilities for taxzman",
    long_description=readme_file.read_text(encoding="utf-8") if readme_file.exists() else "",
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/yourname/common",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
)
