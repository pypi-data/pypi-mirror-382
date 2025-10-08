from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements file
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh.readlines() if line.strip() and not line.startswith("#")]

setup(
    name="meter-lib",
    version="0.0.4",
    author="Sruthi R",
    author_email="sruthi@litewave.ai",
    description="A litewave library to collect the customer credit usage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aiorch/meter-lib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="customer credit usage ",
    project_urls={
        "Bug Reports": "https://github.com/aiorch/meter-lib/issues",
        "Source": "https://github.com/aiorch/meter-lib",
        "Documentation": "https://github.com/aiorch/meter-lib#readme",
    },
    include_package_data=True,
    zip_safe=False,
) 