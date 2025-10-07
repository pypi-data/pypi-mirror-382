from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Image-Processing-Peralta",
    version="0.0.1",
    author="João Filipe Peralta",
    author_email="joaofilipeperalta@gmail.com",
    description="A project that will too a images matchmaking and also show their diferences.",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joaofilipe014/image-processing-package.git",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
)
