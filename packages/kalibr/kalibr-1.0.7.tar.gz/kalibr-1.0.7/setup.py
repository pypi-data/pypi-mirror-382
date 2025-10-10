from setuptools import setup, find_packages

setup(
    name="kalibr",
    version="1.0.7",  # BUMPED VERSION
    author="Devon",
    author_email="hello@kalibr.systems",
    description="Kalibr Connect: integrate your app with every major AI model",
    long_description="Kalibr Connect lets developers integrate once and connect to all major AI models — GPT, Claude, Gemini, Copilot, and more.",
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
            "kalibr-connect = kalibr.__main__:main",
        ],
    },
    python_requires=">=3.9",
    license="MIT",
)
