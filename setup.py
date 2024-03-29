from setuptools import setup, find_packages  # NOQA

with open("README.md", "r") as fh:
    long_description = fh.read()

def read(filename):
    return [
        req.strip() for req in open(filename).readlines()
    ]

setup(
    name="covid-seird",
    version="0.0.7",
    author="Paulo Branco",
    author_email="paulorobertobranco@gmail.com",
    description="""A small package that implements the SEIRD Epidemiological
                   Model on COVID-19 data.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paulorobertobranco/covid_seird",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=read('requirements.txt'),
    python_requires=">=3.6",
)
