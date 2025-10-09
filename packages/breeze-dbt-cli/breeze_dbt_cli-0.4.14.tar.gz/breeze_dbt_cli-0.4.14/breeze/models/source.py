# breeze/models/source.py

import os
from breeze.utils.db_utils import get_columns_from_database
from breeze.utils.dbt_utils import (
    get_profile,
    get_profile_name_from_dbt_project,
    get_target_from_profile,
    get_entity_paths_from_dbt_project
)
from breeze.utils.yaml_utils import load_yaml_file, write_yaml_file, find_yaml_path, add_tests_to_yaml
from breeze.utils.utils import format_description
from breeze.utils.template_utils import get_template_content
from breeze.utils.ai_utils import generate_descriptions_for_entity
from typing import Optional, List
from jinja2 import Template
import typer
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq


def generate_source_yml(
    source_name: str,
    schema_name: str,
    force: bool = False,
    template_path: Optional[str] = None,
    path: Optional[str] = None,
    describe: bool = False,
    catalog: Optional[str] = None,
) -> bool:
    """
    Generates or updates a YAML file for a source, including column metadata. 
    The YAML file can be customized with a template and optional AI-generated descriptions.

    Args:
        - source_name (str): The name of the source table.
        - schema_name (str): The schema where the source table resides.
        - force (bool, optional): If True, overwrites the YAML file if it already exists. Defaults to False.
        - template_path (Optional[str], optional): Path to a custom YAML template file. If None, a default 
            template is used. Defaults to None.
        - path (Optional[str], optional): Custom directory path to store the YAML file. If None, defaults 
            to `models/schema_name`. Defaults to None.
        - describe (bool, optional): If True, uses AI to generate descriptions for the source and its columns. 
            Defaults to False.

    Returns:
        bool: 
            - True if the YAML file was created or overwritten.
            - False if the file already exists and `force` is False.

    Raises:
        Exception:
            - If the source table cannot be found in the database.
            - If the custom template file is not found.
    """
    # Get model paths from dbt_project.yml
    model_paths = get_entity_paths_from_dbt_project("source")

    # Until I implement multi model path capabilities, lets just get the first element
    model_paths = model_paths[0]
    if not model_paths:
        raise Exception("No model paths defined in dbt_project.yml.")
    
    # Define the directory and YAML file path
    if path:
        # If custom path is provided, use it
        os.makedirs(path, exist_ok=True)
        yml_path = os.path.join(path, f"{source_name}.yml")
    else:
        # Default behavior: Create the YAML file in 'models/schema_name/source_name.yml'
        source_dir = os.path.join(model_paths, schema_name)
        os.makedirs(source_dir, exist_ok=True)
        yml_path = os.path.join(source_dir, f"{source_name}.yml")

    # Check if the YML file already exists
    if os.path.exists(yml_path) and not force:
        typer.echo(f"⏭️  YML file already exists at '{yml_path}'. Skipping creation.")
        return False

    # Attempt to get columns by querying the database
    profile = get_profile()
    profile_name = get_profile_name_from_dbt_project()
    target = get_target_from_profile(profile, profile_name)
    database = target.get("dbname") or target.get("database") or target.get("catalog") or target.get("project")
    if catalog:
        database = catalog
        
    columns = get_columns_from_database(database, schema_name, source_name)
    if not columns:
        raise Exception(
            f"Error: Table '{source_name}' was not found in schema '{schema_name}' of database '{database}'."
        )
    columns_data = [
        {"name": col_name, "data_type": data_type, "description": ""} for col_name, data_type in columns
    ]

    # Optionally use AI to generate descriptions

    source_description = ""
    if describe:
        source_description, columns_data = generate_descriptions_for_entity(
            entity_name=source_name,
            resource_type="source",
            schema=schema_name,
            columns_data=columns_data
        )

    # Format descriptions for columns
    for column in columns_data:
        column["description"] = format_description(column["description"], "build", "source_column")

    # Get the template content from template_utils
    try:
        template_content = get_template_content("default_source_template.yml", custom_template_path=template_path)
    except FileNotFoundError as e:
        raise Exception(f"❌ {e}")

    # Create a Jinja2 template with whitespace control
    jinja_template = Template(
        template_content, trim_blocks=True, lstrip_blocks=True
    )

    # Render the template with context variables
    content = jinja_template.render(
        source_name=source_name,
        schema_name=schema_name,
        database=database,
        columns=columns_data,
        source_description=format_description(source_description, "build", "source_table")
    )

    # Write the content to the YML file
    with open(yml_path, "w") as yml_file:
        yml_file.write(content)

    if force and os.path.exists(yml_path):
        typer.echo(f"♻️  Source YML file for source {source_name} at {yml_path} has been created / overwritten.")
    else:
        typer.echo(f"✅  Source YML file for source {source_name} was created at {yml_path}")
    return True


def add_test_to_source(
    test_names: List[str], 
    source_name: str, 
    columns: Optional[List[str]] = None
) -> bool:
    """
    Adds one or more tests to a source YAML file. Tests can be applied at the table level 
    or to specific columns.

    Args:
        - test_names (List[str]): A list of test names to be added (e.g., ["not_null", "unique"]).
        - source_name (str): The name of the source table to which the tests will be added.
        - columns (Optional[List[str]], optional): A list of column names to add the tests to. 
            If None, the tests are added at the table level. Defaults to None.

    Returns:
        bool: 
            - True if the YAML file was modified with new tests.
            - False if no changes were made (e.g., tests were already present).

    Raises:
        Exception:
            - If the YAML file for the source cannot be located.
            - If the source table does not exist in the YAML file.
    """
    # Locate the YAML file for the source
    yml_path = find_yaml_path(source_name, "source")
    if not yml_path:
        raise Exception(f"YAML file for source '{source_name}' not found.")

    # Load the YAML file using the utility function
    yml_data = load_yaml_file(yml_path)

    sources = yml_data.get("sources", [])
    if not sources:
        raise Exception(f"No sources found in YAML file '{yml_path}'.")

    # Find the table (source) in the YAML
    table = None
    for source in sources:
        for tbl in source.get("tables", []):
            if tbl.get("name") == source_name:
                table = tbl
                break
        if table:
            break

    if table is None:
        raise Exception(f"Source '{source_name}' not found in YAML file '{yml_path}'.")

    # Use the utility function to add tests
    changes_made = add_tests_to_yaml(table, test_names, columns)

    if changes_made:
        # Write back the YAML file using the utility function
        write_yaml_file(yml_path, yml_data)
        return True
    else:
        return False