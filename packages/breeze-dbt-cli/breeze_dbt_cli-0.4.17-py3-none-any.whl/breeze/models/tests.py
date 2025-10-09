import os
import yaml
from jinja2 import Template
from breeze.utils.template_utils import get_template_content
from breeze.utils.dbt_utils import load_dbt_project
import typer


def create_test_file(test_name: str, force: bool = False) -> bool:
    """
    Create a test SQL file in the test-paths specified in dbt_project.yml.

    Args:
    - test_name: The name of the test to create.
    - force: Whether to overwrite the file if it already exists.

    Returns:
    - bool: True if the file was created, False if skipped.
    """
    dbt_project = load_dbt_project()
    generic_path = "generic"
    test_paths = dbt_project.get("test-paths", [])

    if not test_paths:
        raise Exception("❌ No test-paths found in dbt_project.yml.")

    # Use the first test path for file creation
    test_path = os.path.join(test_paths[0], generic_path, f"{test_name}.sql")
    os.makedirs(os.path.dirname(test_path), exist_ok=True)

    # Check if the file exists
    if os.path.exists(test_path) and not force:
        typer.echo(f"⏭️  Test '{test_name}.sql' already exists at '{test_path}'. Skipping creation.")
        return False

    # Get the template content
    try:
        template_content = get_template_content("default_test_template.sql")
    except FileNotFoundError:
        raise Exception("❌ Default test template not found in the templates directory.")

    # Replace placeholders in the template
    test_content = template_content.replace("test_name", test_name)

    # Write the test file
    with open(test_path, "w") as test_file:
        test_file.write(test_content)

    if force:
        typer.echo(f"♻️  Test '{test_name}.sql' has been created / overwritten at '{test_path}'.")
    else:
        typer.echo(f"✅  Test '{test_name}.sql' has been created at '{test_path}'.")

    return True