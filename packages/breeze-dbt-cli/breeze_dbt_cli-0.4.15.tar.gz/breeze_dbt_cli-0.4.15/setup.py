# setup.py

from setuptools import setup, find_packages

setup(
    name="breeze-dbt-cli",  # The name of your package
    version="0.4.15",  # Version of your package
    author="Alejandro Cabrera",  # Your name or your team's name
    author_email="alecab1994@gmail.com",  # Your email
    description="A CLI tool to streamline dbt project development.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alecab94/breeze-dbt-cli",  # URL to your project's repository
    packages=find_packages(),
    install_requires=[
        "typer[all]",
        "pyyaml",
        "Jinja2",
        "ruamel.yaml",
        "pyodbc",
        "openai",
        "pydantic",
        "alive_progress"
    ],
    include_package_data=True,  # This ensures non-code files are included
    package_data={
        'breeze': ['templates/*.sql', 'templates/*.yml']
    },
    entry_points={
        "console_scripts": [
            "breeze=breeze.cli:app",  # Make the `breeze` command available globally
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version requirement
)
