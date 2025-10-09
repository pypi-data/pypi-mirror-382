from setuptools import setup, find_packages

setup(
    name="card_gen",
    version="0.1.0",
    author="Tapas Pradhan",
    author_email="tapas.pradhan1801@gmail.com",
    description="A simple package to generate annotated images with text and logo.",
    packages=find_packages(),
    install_requires=[
        "Pillow>=10.0.0",
    ],
    python_requires=">=3.8",
)
