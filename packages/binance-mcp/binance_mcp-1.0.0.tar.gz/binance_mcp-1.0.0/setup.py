from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="binance-mcp",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="MCP server for crypto trading via Binance.US",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/binance-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "python-binance>=1.0.19",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "websockets>=12.0",
        "aiohttp>=3.9.1",
        "sqlalchemy>=2.0.25",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
        ],
    },
    entry_points={
        "console_scripts": [
            "binance-mcp=crypto_mcp_server.server:main",
        ],
    },
)
