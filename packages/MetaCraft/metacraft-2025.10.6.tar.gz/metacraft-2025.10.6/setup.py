from setuptools import setup, find_packages

setup(
    name="MetaCraft",
    version="2025.10.6",
    description="Toolkit to enrich, validate and explore YAML metadata from a pandas DataFrame.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Jose Carlos Del Valle",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.23",
        "pandas>=2.1",
        "PyYAML>=6.0",
        "openai>=1.14",
        "tdigest==0.5.2.2",
        "datasketch>=1.5",
    ],
    project_urls={
        "Homepage": "https://example.com/MetaCraft",
    },
)
