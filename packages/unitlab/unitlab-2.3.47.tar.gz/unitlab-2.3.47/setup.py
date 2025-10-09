from setuptools import find_packages, setup

setup(
    name="unitlab",
    version="2.3.47",
    license="MIT",
    author="Unitlab Inc.",
    author_email="team@unitlab.ai",
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={"static": ["*"], "Potato": ["*.so"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    package_dir={"": "src"},
    url="https://github.com/teamunitlab/unitlab-sdk",
    keywords="unitlab-sdk",
    install_requires=[
        "aiohttp",
        "aiofiles",
        "requests",
        "tqdm",
        "typer",
        "validators",
    ],
    entry_points={
        "console_scripts": ["unitlab=unitlab.main:app"],
    },
)
