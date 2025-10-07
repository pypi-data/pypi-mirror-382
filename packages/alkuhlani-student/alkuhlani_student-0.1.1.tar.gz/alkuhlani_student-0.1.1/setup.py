from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="alkuhlani-student",
    version="0.1.1",
    author="Alkuhlani Student (CYS 2)",
    author_email="alkuhlani@example.com",
    description="A simple Python package to analyze word frequency in text - محلل تكرار الكلمات",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alkuhlani/alkuhlani-student",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
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
            "alkuhlani-student=alkuhlani_student.analyzer:main",
        ],
    },
    keywords="word frequency analysis text processing nlp arabic alkuhlani student",
    project_urls={
        "Bug Reports": "https://github.com/alkuhlani/alkuhlani-student/issues",
        "Source": "https://github.com/alkuhlani/alkuhlani-student",
    },
)
