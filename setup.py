from setuptools import find_packages, setup

setup(
    name="bss-plot",  # Updated package name for PyPI/pip
    packages=find_packages(
        include=["bss_plot", "bss_plot.*"]  # Use underscores internally
    ),
    version="0.1",
    include_package_data=True,
    install_requires=[
        "matplotlib",  # Ensure matplotlib is installed
    ],
    package_data={
        "bss_plot": ["styles/*.mplstyle"],  # Adjusted to the new package name
    },
    entry_points={
        "matplotlib.style.core": [
            "use = bss_plot.styles",
        ]
    },
)
