import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="me_toolbox",
    version="0.0.2",
    author="Omri Stein",
    author_email="omri.stein@gmail.com",
    description="Mechanical engineering design tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OmriStein/MEtoolbox",
    project_urls={
        "Bug Tracker": "https://github.com/OmriStein/MEtoolbox/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "me_toolbox"},
    packages=setuptools.find_packages(where="me_toolbox"),
    python_requires=">=3.6",
)
