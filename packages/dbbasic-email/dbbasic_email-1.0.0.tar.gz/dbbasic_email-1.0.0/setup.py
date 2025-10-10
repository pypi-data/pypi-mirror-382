from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dbbasic-email",
    version="1.0.0",
    author="DBBasic Project",
    author_email="dan@quellhorst.com",
    description="Simple email queue with Unix mail support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/askrobots/dbbasic-email",
    project_urls={
        "Bug Tracker": "https://github.com/askrobots/dbbasic-email/issues",
        "Documentation": "https://github.com/askrobots/dbbasic-email#readme",
        "Source Code": "https://github.com/askrobots/dbbasic-email",
        "Specification": "http://dbbasic.com/email-spec",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Email",
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
    keywords="email, smtp, mail, queue, unix mail, mbox",
    python_requires=">=3.6",
    install_requires=[
        # No required dependencies for local mail
        # dbbasic-queue is optional (only needed for send_email)
    ],
    extras_require={
        "queue": [
            "dbbasic-queue>=1.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
