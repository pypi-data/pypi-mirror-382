from setuptools import setup, find_packages

setup(
    name="seanox-ai-nlp",
    version="1.3.0.1",
    packages=find_packages(),
    author="Seanox Software Solutions",
    description=(
        "Lightweight NLP components for semantic processing of domain-specific content."
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seanox/seanox-ai-nlp",
    license="Apache-2.0",
    python_requires=">=3.10",
    install_requires=[
        "pyyaml>=6.0",
        "jsonschema>=4.17",
        "jinja2>=3.0.0"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent"
    ],
    keywords=[
        # NLP pipeline
        "NLP", "fine-tuning", "information retrieval", "preprocessing",
        "semantic retrieval", "retrieval optimization",
        # Package focus
        "domain-specific", "structured data",
        "semantic processing", "text processing",
        "information extraction", "entity extraction",
        # units
        "measurement units", "measurement extraction",
        # synthetics
        "synthetic data", "data generation", "synthetic text", "template engine", "sentence generator",
        "data annotation", "semantic labeling", "pretraining data",
        "training data augmentation"
    ]
)
