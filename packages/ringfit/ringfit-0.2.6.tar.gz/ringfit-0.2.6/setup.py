from setuptools import setup, find_packages

setup(
    name="ringfit",
    version="0.2.6",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "Pillow",
        "ehtim"
    ],
)
