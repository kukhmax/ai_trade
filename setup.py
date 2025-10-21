from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="crypto-ai-agent",
    version="1.0.0",
    author="Crypto AI Agent Team",
    author_email="support@crypto-ai-agent.com",
    description="AI-powered cryptocurrency market analysis agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/crypto-ai-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "crypto-ai=cli:main",
        ],
    },
    include_package_data=True,
)