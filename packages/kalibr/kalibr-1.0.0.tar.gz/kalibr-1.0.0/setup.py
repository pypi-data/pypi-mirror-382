from setuptools import setup, find_packages

setup(
    name="kalibr",
    version="1.0.0",
    author="Devon",
    author_email="hello@kalibr.systems",
    description="Kalibr Connect: one SDK to integrate your app with every major AI model.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/devon/kalibr-sdk",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "typer",
        "pydantic>=2.0",
    ],
    entry_points={
        "console_scripts": [
            "kalibr-connect=kalibr.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
