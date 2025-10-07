from setuptools import setup, find_packages

setup(
    name="ringfit",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "Pillow",
        "ehtim"
    ],
)
