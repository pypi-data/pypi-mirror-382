from setuptools import setup, find_packages
from pathlib import Path

PACKAGE_NAME = "flax-weightwatcher"
HERE = Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8") if (HERE / "README.md").exists() else ""

setup(
    name=PACKAGE_NAME,
    version="0.1.1",
    description="A Flax/JAX port of HTSR analysis tools",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Jaisidh Singh",
    author_email="jaisidh.singh@student.uni-tuebingen.com",
    url="https://github.com/jaisidhsingh/flax-weightwatcher",
    license="MIT",
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    install_requires=[
        "numpy>=1.23",
        "pandas>=1.4",
        "flax>=0.6.0",
        "jax>=0.3.0",
        "powerlaw>=1.4.6",
        "jaxtyping>=0.2.0"
    ],
    python_requires=">=3.12",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="flax jax weightwatcher weight-analysis HTSR ES powerlaw",
)
