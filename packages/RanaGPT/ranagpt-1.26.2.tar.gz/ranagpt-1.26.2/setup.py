import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RanaGPT",
    version="1.26.2",
    author="Tofey",
    description="Library for interacting with multiple AI APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=["RanaGPT"],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "user_agent",
        "beautifulsoup4",
        "pycountry",
        "mnemonic"
    ],
)