from setuptools import setup, find_packages

setup(
    name="aacc",
    version="2.0.1",
    packages=find_packages(),
    description="Use 'aacc()' instead of 'print()' in Python",
    long_description=open("README.md", encoding="utf-8").read(),  
    long_description_content_type="text/markdown",
    author="Programmer Seo Hook : @LAEGER_MO ",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.0",
)
