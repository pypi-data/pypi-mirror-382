from pathlib import Path

from setuptools import find_packages, setup

CURRENT_DIR = Path(__file__).parent


def get_long_description() -> str:
    return (CURRENT_DIR / "README.md").read_text(encoding="utf8")


setup(
    name="dockertown",
    version="0.2.8",
    description="A decent Python wrapper for Docker CLI",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    install_requires=(CURRENT_DIR / "requirements.txt").read_text().splitlines(),
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,  # will read the MANIFEST.in
    license="MIT",
    python_requires=">=3.7, <4",
    entry_points={
        "console_scripts": ["dockertown=dockertown.command_line_entrypoint:main"],
    },
    project_urls={
        "Documentation": "https://duckietown.github.io/dockertown/",
        "Source Code": "https://github.com/duckietown/dockertown",
        "Bug Tracker": "https://github.com/duckietown/dockertown/issues",
    },
)
