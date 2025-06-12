from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

install_requires = ["wagtail>=2"]

tests_requires = [
    "black",
    "coverage",
    "flake8",
    "isort",
    "pytest",
    "pytest-cov",
    "pytest-django",
]

setup(
    name="wagtail-model-forms",
    version="0.8.7",
    description="The Wagtail Form Builder functionalities available for your models/snippets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="R. Moorman <rob@vicktor.nl>",
    install_requires=install_requires,
    tests_requires=tests_requires,
    extras_require={"test": tests_requires},
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Operating System :: Unix",
        "Framework :: Wagtail :: 5",
        "Framework :: Wagtail :: 6",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
