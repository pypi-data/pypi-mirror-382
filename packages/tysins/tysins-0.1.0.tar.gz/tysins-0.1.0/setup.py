from setuptools import setup, find_packages

setup(
    name="tysins",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # add dependencies here, e.g. "adbutils", "colorama", etc.
    ],
    entry_points={
        "console_scripts": [
            "tysins=tysins.main:main",  # This is the magic line
        ],
    },
    author="Ervuln",
    description="Android transfer CLI tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
