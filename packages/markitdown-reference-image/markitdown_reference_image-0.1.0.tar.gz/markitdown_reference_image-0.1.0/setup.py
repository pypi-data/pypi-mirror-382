from setuptools import setup, find_packages

setup(
    name="markitdown-reference-image",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "Pillow>=8.0.0",
        "markdown>=3.0.0",
        "beautifulsoup4>=4.9.0",
        "selenium>=4.0.0",
        "webdriver-manager>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "markitdown-extract=markitdown_reference_image.__main__:main",
        ],
    },
    author="Naveen Kumar Rajarajan",
    author_email="smazeeapps@gmail.com",
    description="Extract images from markdown files and highlight text chunks with bounding boxes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/markitdown-reference-image",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
