"""Setup script for PDF Text Organizer."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pdf-text-organizer",
    version="1.0.0",
    description="PDF text extraction and spatial grouping tool - Vultus Serpentis demo application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vultus Serpentis Team",
    url="https://github.com/yourusername/pdf-text-organizer",
    project_urls={
        "Documentation": "https://github.com/yourusername/pdf-text-organizer/blob/main/README.md",
        "Source": "https://github.com/yourusername/pdf-text-organizer",
        "Bug Tracker": "https://github.com/yourusername/pdf-text-organizer/issues",
    },
    packages=find_packages(exclude=["tests", "tests.*", "Build", "Build.*"]),
    install_requires=[
        "vultus-serpentis>=1.0.0",
        "pdfplumber>=0.10.0",
        "ttkbootstrap>=1.10.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "pdf-organizer=pdf_text_organizer.app:main",
        ],
        "gui_scripts": [
            "pdf-organizer-gui=pdf_text_organizer.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    keywords="pdf text extraction grouping spatial-analysis gui tkinter",
)
