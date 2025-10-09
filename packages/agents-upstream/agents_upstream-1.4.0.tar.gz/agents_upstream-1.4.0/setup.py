"""
Setup script for agents-upstream package.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Ler README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="agents-upstream",
    version="1.4.0",
    description="AI-powered research analysis system for product discovery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Agents Upstream Contributors",
    license="MIT",
    url="https://github.com/marcelusfernandes/agents-upstream",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "agents-upstream=agents_upstream.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=["ai", "agents", "product-discovery", "research-analysis", "workflow", "cursor-ai"],
    project_urls={
        "Homepage": "https://github.com/marcelusfernandes/agents-upstream",
        "Repository": "https://github.com/marcelusfernandes/agents-upstream",
        "Issues": "https://github.com/marcelusfernandes/agents-upstream/issues",
    },
)

