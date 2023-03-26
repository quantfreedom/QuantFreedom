from setuptools import setup, find_packages

with open('README.md', 'r', encoding="utf-8", errors='ignore') as fh:
    long_description = fh.read()

version = {}
with open("quantfreedom/_version.py", encoding="utf-8") as fp:
    exec(fp.read(), version)

setup(
    name='quantfreedom',
    version=version['__version__'],
    description='Python library for backtesting and analyzing trading strategies at scale',
    author='Quant Freedom',
    author_email='QuantFreedom1022@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/QuantFreedom1022/quantfreedom',
    packages=find_packages(),
    install_requires=[
        'autopep8',
        'ccxt',
        'dash',
        'dash-bootstrap-templates',
        'ipywidgets==7.7.2',
        'jupyter-dash',
        'jupyterlab-widgets==1.1.1',
        'kaleido==0.1.0post1',
        'mypy_extensions',
        'notebook',
        'numba>=0.53.1; python_version < "3.10"',
        'numba>=0.56.0; python_version >= "3.10"',
        'numpy>=1.16.5',
        'pandas',
        'polars',
        'pyarrow',
        'pybit',
        'typing_extensions; python_version < "3.8"',
    ],
    extras_require={
        'web': [
            'Markdown',
            'PyYAML',
            'black',
            'mkdocs',
            'mkdocs-autorefs',
            'mkdocs-gen-files',
            'mkdocs-literate-nav',
            'mkdocs-material',
            'mkdocs-material-extensions',
            'mkdocs-minify-plugin',
            'mkdocs-section-index',
            'mkdocs-video',
            'mkdocstrings',
            'mkdocstrings-python',
            'pymdown-extensions',
            'tabulate',
        ]
    },
    python_requires='>=3.6, <3.11',
    license='Ask me now!',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: Must ask to use',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development',
        'Topic :: Office/Business :: Financial',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ],
)
