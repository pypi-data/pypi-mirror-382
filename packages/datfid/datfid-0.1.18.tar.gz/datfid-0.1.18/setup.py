from setuptools import setup, find_packages

# to build:
# 1) open this file at level of datfid-sdk folder
# 2) change version in this file and save it
# 3) delete folder datfid.egg-info
# 4) delete older files from dist folder
# 5) in terminal: python setup.py sdist bdist_wheel
# 6) in terminal: twine upload --repository pypi dist/*
# 7) in hugging face delete older files from dist folder
# 8) in hugging face upload updated files
# 9) in terminal uninstall older version of datfid: pip uninstall datfid
# 10) in terminal install new version of datfid: pip install --index-url https://test.pypi.org/simple/ datfid

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="datfid",
    version="0.1.18",
    description="SDK to access the DATFID API hosted on Hugging Face Spaces",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Important!
    author="DATFID",
    author_email="igor.schapiro@datfid.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pandas>=1.0.1",
        "numpy>=1.22, <2.1"
    ],
    python_requires=">=3.7",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
