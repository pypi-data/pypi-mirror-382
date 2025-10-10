from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dbbasic-queue",
    version="1.0.0",
    author="DBBasic Project",
    author_email="dan@quellhorst.com",
    description="TSV-based job queue for async tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/askrobots/dbbasic-queue",
    project_urls={
        "Bug Tracker": "https://github.com/askrobots/dbbasic-queue/issues",
        "Documentation": "https://github.com/askrobots/dbbasic-queue#readme",
        "Source Code": "https://github.com/askrobots/dbbasic-queue",
        "Specification": "http://dbbasic.com/queue-spec",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*", "workers", "workers.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="queue, job queue, background jobs, async, tsv, cron, worker",
    python_requires=">=3.6",
    install_requires=[
        # Note: dbbasic-tsv is stubbed in the implementation
        # Remove this dependency once dbbasic-tsv is published
        # "dbbasic-tsv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
