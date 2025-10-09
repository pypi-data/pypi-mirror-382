# breeze/models/model.py

import os
from breeze.utils.db_utils import get_columns_from_database
from breeze.utils.yaml_utils import load_yaml_file, write_yaml_file, find_yaml_path, add_tests_to_yaml
from breeze.utils.utils import format_description
from breeze.utils.template_utils import get_template_content
from breeze.utils.dbt_utils import load_manifest, find_entity_in_manifest, get_entity_paths_from_dbt_project
from breeze.utils.ai_utils import generate_descriptions_for_entity
from typing import Optional, List
from jinja2 import Template
import typer
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq
import json

def create_empty_sql_file(
    model_name: str,
    path: str,
    force: bool = False,
    template_path: Optional[str] = None,
    no_subfolder: bool = False
) -> bool:
    """
    Creates an SQL file for a specified model in the appropriate directory, 
    using either a default template or a custom template. The function 
    handles directory creation and optionally overwrites existing files.

    Args:
        - model_name (str): The name of the model for which the SQL file is being created.
        - path (str): The directory path where the model SQL file will be created.
        - force (bool, optional): If True, overwrites the file if it already exists. Defaults to False.
        - template_path (Optional[str], optional): Path to a custom SQL template file. If not provided, 
            a default template is used. Defaults to None.
        - no_subfolder (bool, optional): If True, places the SQL file directly in the provided path 
            instead of a subdirectory named after the model. Defaults to False.

    Returns:
        - bool: 
            - True if the SQL file was successfully created or overwritten.
            - False if the file already exists and `force` is False, or if an error occurred.

    Raises:
        - Exception: If no model paths are defined in the `dbt_project.yml` configuration file.
        - FileNotFoundError: If the specified template file does not exist.

    """
    # Get model paths from dbt_project.yml
    model_paths = get_entity_paths_from_dbt_project("model")
    # Until I implement multi model path capabilities, lets just get the first element
    model_paths = model_paths[0]
    if not model_paths:
        raise Exception("No model paths defined in dbt_project.yml.")
    
    # Define the directory and SQL file path
    if no_subfolder:
        model_dir = os.path.join(model_paths, path)
    else:
        model_dir = os.path.join(model_paths, path, model_name)
        os.makedirs(model_dir, exist_ok=True)
    
    sql_path = os.path.join(model_dir, f"{model_name}.sql")

    # Get the template content using the new utility function
    try:
        template_content = get_template_content("default_model_template.sql", custom_template_path=template_path)
    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        return False

    # Check if the SQL file already exists
    if os.path.exists(sql_path) and not force:
        typer.echo(f"SQL file for '{model_name}' model already exists at '{sql_path}'. Skipping creation.")
        return False

    # Create or overwrite the SQL file with the template
    with open(sql_path, "w") as sql_file:
        sql_file.write(template_content)

    if force and os.path.exists(sql_path):
        typer.echo(f"♻️  SQL file for '{model_name}' model at '{sql_path}' has been created / overwritten.")
    else:
        typer.echo(f"✅  SQL file for '{model_name}' model created at '{sql_path}'")

    return True


def create_model_yml(
    model_name: str, 
    force: bool = False, 
    template_path: Optional[str] = None,
    describe: bool = False
) -> bool:
    """
    Generates or updates a model YAML file for the specified model, including column metadata such as
    names, data types, and optional AI-generated descriptions. Uses a template to format the YAML file 
    and fetches model metadata from the dbt manifest and database.

    Args:
        - model_name (str): The name of the model for which the YAML file is being generated or updated.
        - force (bool, optional): If True, overwrites the YAML file if it already exists. Defaults to False.
        - template_path (Optional[str], optional): Path to a custom YAML template file. If not provided, 
            a default template is used. Defaults to None.
        - describe (bool, optional): If True, uses AI to generate descriptions for the model and its columns. 
            Defaults to False.

    Returns:
        bool: 
            - True if the YAML file was successfully created or overwritten.
            - False if the YAML file already exists and `force` is False.

    Raises:
        Exception: 
            - If the table for the model is not found in the database.
            - If the custom template file is not found.

    """
    # Load the manifest file using the utility function
    manifest = load_manifest()

    # Find the model in the manifest using the utility function
    model = find_entity_in_manifest(manifest, model_name)

    # Extract folder_name from the model's original file path
    original_file_path = model["original_file_path"]
    resource_type = model["resource_type"]
    database = model["database"]
    schema = model["schema"]
    alias = model.get("alias") or model["name"]

    model_dir = os.path.dirname(original_file_path)

    yml_path = os.path.join(model_dir, f"{model_name}.yml")

    # Check if the YML file already exists
    if os.path.exists(yml_path) and not force:
        typer.echo(f"⏭️  Properties YML file for {resource_type} '{schema}.{alias}' already exists at '{yml_path}'. Skipping creation.")
        return False

    # Prepare columns data
    columns = get_columns_from_database(
        database, schema, alias
    )
    if not columns:
        raise Exception(
            f"Error: Table '{model_name}' was not found in schema '{schema}' of database '{database}'."
        )
    columns_data = [
        {"name": col_name, "data_type": data_type, "description": ""} for col_name, data_type in columns
    ]

    model_description = ""
    # Optionally use AI to generate descriptions
    if describe:
        model_description, columns_data = generate_descriptions_for_entity(model_name, resource_type, schema, columns_data)

    # Format descriptions for columns
    for column in columns_data:
        column["description"] = format_description(column["description"],  "build", resource_type + "_column")

    # Get the template content from template_utils
    try:
        template_content = get_template_content("default_model_template.yml", custom_template_path=template_path)
    except FileNotFoundError as e:
        raise Exception(f"❌ {e}")

    # Create a Jinja2 template with whitespace control
    jinja_template = Template(
        template_content, trim_blocks=True, lstrip_blocks=True
    )
    # Render the template with context variables
    content = jinja_template.render(
        resource_type=resource_type + "s",
        model_name=model_name, 
        schema_name=schema, 
        columns=columns_data, 
        model_description=format_description(model_description, "build", resource_type + "_table")
    )

    # Write content to the YML file
    with open(yml_path, "w") as yml_file:
        yml_file.write(content)

    if force and os.path.exists(yml_path):
        typer.echo(f"♻️  YML file for {resource_type} '{schema}.{model_name}' at '{yml_path}' created / has been overwritten.")
    else:
        typer.echo(f"✅  YML file for {resource_type} '{schema}.{model_name}' created at '{yml_path}'")
    return True


def add_test_to_model(
    test_names: List[str], 
    model_name: str, 
    resource_type: str,
    columns: Optional[List[str]] = None
) -> bool:
    """
    Adds one or more tests to a model YAML file. Tests can be applied at the 
    model level or to specific columns.

    Args:
        - test_names (List[str]): A list of test names to be added (e.g., ["not_null", "unique"]).
        - model_name (str): The name of the model to which the tests will be added.
        - resource_type (str): The type of resource (e.g., "model", "seed", "snapshot").
        - columns (Optional[List[str]], optional): A list of column names to add the tests to. 
            If None, the tests are added at the model level. Defaults to None.

    Returns:
        bool: 
            - True if the YAML file was modified with new tests.
            - False if no changes were made (e.g., tests were already present).

    Raises:
        Exception: 
            - If the YAML file for the model cannot be located.
            - If the resource type does not exist in the YAML file.
            - If the specified model is not found in the YAML file.
    """
    # Locate the YAML file for the model
    yml_path = find_yaml_path(model_name, resource_type)
    if not yml_path:
        raise Exception(f"YAML file for {resource_type} '{model_name}' not found.")

    # Load the YAML file using the utility function
    yml_data = load_yaml_file(yml_path)

    models = yml_data.get(resource_type + "s", [])
    if not models:
        raise Exception(f"No {resource_type}s found in YAML file '{yml_path}'.")

    # Find the model in the YAML
    model = next((m for m in models if m.get("name") == model_name), None)
    if model is None:
        raise Exception(f"{resource_type.capitalize()} '{model_name}' not found in YAML file '{yml_path}'.")

    # Use the utility function to add tests
    changes_made = add_tests_to_yaml(model, test_names, columns)

    if changes_made:
        # Write back the YAML file using the utility function
        write_yaml_file(yml_path, yml_data)
        return True
    else:
        return False
    

def create_semantic_model_yml(
    model_name: str,
    force: bool = False,
    template_path: Optional[str] = None,
    path: Optional[str] = None,
) -> bool:
    """
    Create a boilerplate .yml file for a semantic model corresponding to a dbt model.

    Args:
        - model_name (str): The name of the dbt model for which the semantic model YAML file is created.
        - force (bool, optional): If True, overwrites the YAML file if it already exists. Defaults to False.
        - template_path (Optional[str], optional): Path to a custom template file for the semantic model. 
            If None, a default template is used. Defaults to None.
        - path (Optional[str], optional): A custom directory path to store the YAML file. If None, 
            the directory is inferred from the dbt manifest. Defaults to None.

    Returns:
        bool: 
            - True if the YAML file was successfully created or overwritten.
            - False if the file already exists and `force` is False.

    Raises:
        Exception: 
            - If the custom template file is not found.
            - If the model cannot be located in the dbt manifest.
    """
    # Load the manifest to locate the model
    manifest = load_manifest()

    # Find the model in the manifest using the utility function
    model = find_entity_in_manifest(manifest, model_name)

    # Extract folder_name from the model's original file path
    original_file_path = model["original_file_path"]
    model_dir = path or os.path.dirname(original_file_path)

    semantic_model_yml_path = os.path.join(model_dir, f"{model_name}_semantic.yml")

    # Check if the .yml file already exists
    if os.path.exists(semantic_model_yml_path) and not force:
        typer.echo(f"⏭️  Semantic model YML file for model '{model_name}' already exists at '{semantic_model_yml_path}'. Skipping creation.")
        return False

    # Get the template content from template_utils
    try:
        template_content = get_template_content("default_semantic_model_template.yml", custom_template_path=template_path)
    except FileNotFoundError as e:
        raise Exception(f"❌ {e}")
    
   # Create a Jinja2 template with whitespace control
    jinja_template = Template(
        template_content, trim_blocks=True, lstrip_blocks=True
    )

    # Render the template with context variables
    content = jinja_template.render(
        model_name=model_name
    )

    # Write the semantic model template to the .yml file
    with open(semantic_model_yml_path, "w") as yml_file:
        yml_file.write(content)

    if force:
        typer.echo(f"♻️  Semantic model .yml file for '{model_name}' has been created / overwritten at '{semantic_model_yml_path}'.")
    else:
        typer.echo(f"✅  Semantic model .yml file for '{model_name}' created at '{semantic_model_yml_path}'.")
    return True
