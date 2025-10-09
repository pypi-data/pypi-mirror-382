from pathlib import Path
from setuptools import setup, find_packages

# Read long description from README.md
this_dir = Path(__file__).parent
readme = (this_dir / "README.md").read_text(encoding="utf-8") if (this_dir / "README.md").exists() else "YOLO annotation helper."

setup(
    name="annobel",
    version="0.0.1",
    description="Automatic + manual YOLO bounding box annotation tool (GUI + console)",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Sayali Dongre",
    author_email="sayali.dongre25@gmail.com",
    url="https://github.com/SayaliDongre/annobel",
    license="AGPL-3.0-or-later",
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["annobel", "annobel.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "ultralytics>=8.0.0",
        "pillow>=9.0.0",
    ],
    extras_require={
        "dev": ["black", "flake8", "mypy", "pytest"],
    },
    entry_points={
        "console_scripts": [
            "annobel=annobel.main:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Environment :: X11 Applications :: GTK",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Source": "https://github.com/SayaliDongre/annobel",
        "Issues": "https://github.com/SayaliDongre/annobel/issues",
        "Ultralytics": "https://github.com/ultralytics/ultralytics",
    },
)
