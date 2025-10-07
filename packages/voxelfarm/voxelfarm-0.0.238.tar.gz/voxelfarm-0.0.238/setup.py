# python setup.py sdist

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="voxelfarm",
    version="0.0.238",
    author="Voxel Farm",
    author_email="webmaster@voxelfarm.com",
    description="Voxel Farm Python Lambdas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.voxelfarm.com/help/PythonCookbook.html",
    project_urls={
        "Bug Tracker": "https://github.com/voxelfarm/voxelfarmclient/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    install_requires = [ 
        "pandas",
        "requests",
        "pybase64",
        "msal",
    ],
    extras_require = {
        "dev": [
            "pytest>=3.7",
        ],
    }
)