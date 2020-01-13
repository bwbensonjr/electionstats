import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
    "pandas",
    "requests",
    ]
    
setuptools.setup(
    name="electionstats",
    version="0.0.2",
    author="Brent Benson",
    author_email="bwbensonjr@gmail.com",
    description="Download Massachusetts election results from electionstats.state.ma.us",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bwbensonjr/electionstats",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3.5',
)
