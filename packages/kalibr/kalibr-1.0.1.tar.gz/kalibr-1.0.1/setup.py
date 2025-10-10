from setuptools import setup, find_packages

setup(
    name="kalibr",
    version="1.0.1",
    author="Devon",
    description="Kalibr SDK — Integrate your SaaS with every major AI model using a single SDK.",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "typer>=0.9.0",
        "pydantic>=2.0",
    ],
    entry_points={
        "console_scripts": [
            "kalibr-connect=kalibr.__main__:main",
        ],
    },
    python_requires=">=3.9",
)
