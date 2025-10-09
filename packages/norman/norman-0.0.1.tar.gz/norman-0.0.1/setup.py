from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="norman",
    version="0.0.1",
    author="Norman AI",
    author_email="contact@norman.ai",
    description="Placeholder package for Norman AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/norman-ml",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
    license="Apache 2.0",
)
