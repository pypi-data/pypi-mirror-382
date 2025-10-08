import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="iDEA-inversion",
    version="1.1.7",
    author="Jack Wetherell original code, Anthony R. Osborne new inversion code",
    author_email="anthony.r.osborne019@pm.me",
    description="interacting Dynamic Electrons Approach (iDEA) with an additional inversion method packaged only for testing purposes not for distribution",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.8",
    install_requires=[
        'numpy>=1.22.3',
        'scipy>=1.8.0',
        'matplotlib>=3.5.1',
        'jupyterlab>=3.3.2',
        'tqdm>=4.64.0',
        'black>=22.3.0',
        'autoflake>=1.4.0',
        'build>=0.7.0',
        'twine>=4.0.0',
    ],
)