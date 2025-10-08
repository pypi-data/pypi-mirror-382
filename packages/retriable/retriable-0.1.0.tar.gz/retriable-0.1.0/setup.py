from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="retriable",
    version="0.1.0",
    description="A Python library for editing images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kkristof200/kretriable",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="retriable",
    project_urls={
        "Homepage": "https://github.com/kkristof200/kretriable",
        "Repository": "https://github.com/kkristof200/kretriable",
        "Issues": "https://github.com/kkristof200/kretriable/issues",
    },
)