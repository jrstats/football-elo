from setuptools import setup, find_packages

setup(
    name="football-elo",
    version="1!0+dev",
    author_email="jrstats@outlook.com",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "requests",
        "selenium",
        "webdriver-manager",
        "lxml",
        "html5lib",
        "beautifulsoup4",
        "glom",
    ],
    author="James Robinson",
    license="Apache-2.0",
    description="Python smart mirror",
)