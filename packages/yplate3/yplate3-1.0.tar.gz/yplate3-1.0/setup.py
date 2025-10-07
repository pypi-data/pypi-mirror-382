from setuptools import setup, find_packages

setup(
    name="yplate3",
    version="1.0",
    author="Itry",
    author_email="support@itrypro.ru",
    description="Минималистичный Python web-фреймворк в стиле Django, но проще",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/IGBerko/yplate",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Environment :: Web Environment",
    ],
    entry_points={
        "console_scripts": [
            "yplate = yplate.cli:main"
        ],
    },
)
