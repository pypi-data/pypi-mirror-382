from setuptools import setup, find_packages

setup(
    name="currency_converter_and_calculator",  # Replace with your package name (use hyphens)
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "FreeSimpleGUI>=0.6.0",  # Or "PySimpleGUI" if using standard version
        # Add other dependencies here
    ],
    entry_points={
        "console_scripts": [
            "calc=currency_converter_and_calculator.main:main",
        ],
    },
    author="Carlisle",
    description="A currency converter and calculator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bunnybunnybun/Coin-Calculator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    package_data={
        "currency_converter_and_calculator": ["assets/*.png"],  # Include image assets if needed
    },
)

