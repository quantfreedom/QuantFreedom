from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
    long_description = fh.read()

version = {}
with open("quantfreedom/_version.py", encoding="utf-8") as fp:
    exec(fp.read(), version)

setup(
    name="quantfreedom",
    version=version["__version__"],
    description="Python library for backtesting and analyzing trading strategies at scale",
    author="Quant Freedom",
    author_email="QuantFreedom1022@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QuantFreedom1022/quantfreedom",
    packages=find_packages(),
    install_requires=[],
    extras_require={},
    python_requires=">=3.6, <3.11",
    license="Apache 2.0 with Commons Clause",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: Free for non-commercial use",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
)
