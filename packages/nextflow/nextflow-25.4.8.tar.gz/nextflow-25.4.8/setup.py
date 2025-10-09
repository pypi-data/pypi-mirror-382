from setuptools import setup

__version__ = '25.04.8'


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='nextflow',
    version=__version__,
    author='Jordi Deu-Pons',
    description='A Python wrapper that installs the Nextflow launcher',
    scripts=['launcher/nextflow'],
    long_description=readme(),
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    keywords=["pipeline", "workflow", "nextflow"],
    install_requires=[],
    py_modules=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering"
    ]
)
