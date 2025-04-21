from setuptools import setup, find_packages

setup(
    name="sudoninja",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],  # Add dependencies if you ever use numpy, etc.
    author="Vinicius Barros Canonico",
    author_email="viniciusbcanonico@gmail.com",
    description="A simple Sudoku generator and grid builder library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Vinicius-b-Canonico/sudoninja",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
