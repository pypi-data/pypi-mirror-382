from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="logforge-django",
    version="0.1.1",
    author="LogForge Team",
    author_email="team@logforge.dev",
    description="Django audit logging package for LogForge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/logforge/logforge-django",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2,<6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-django>=4.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
        ],
        "celery": [
            "celery>=5",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
