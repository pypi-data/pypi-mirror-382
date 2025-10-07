from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="word-frequency-analyzer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple Python package to analyze word frequency in text - محلل تكرار الكلمات",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/word-frequency-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Natural Language :: Arabic",
        "Natural Language :: English",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "word-frequency=word_frequency_analyzer.analyzer:main",
        ],
    },
    keywords="word frequency analysis text processing nlp arabic",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/word-frequency-analyzer/issues",
        "Source": "https://github.com/yourusername/word-frequency-analyzer",
    },
)
