# breeze/utils/yaml_utils.py

from typing import List, Optional, Dict
import typer
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.scalarstring import FoldedScalarString
from breeze.utils.dbt_utils import get_entity_paths_from_dbt_project
from breeze.utils.ai_utils import generate_descriptions_for_entity
from breeze.utils.dbt_utils import load_manifest, find_entity_in_manifest
from breeze.utils.utils import format_description
from jinja2 import Template
import os

def load_yaml_file(file_path: str) -> dict:
    """
    Load the YAML file and return its content as a dictionary.
    
    Args:
    - file_path: The path of the YAML file to load.

    Returns:
    - A dictionary containing the contents of the YAML file.
    """
    yaml = YAML()
    try:
        with open(file_path, "r") as yml_file:
            return yaml.load(yml_file) or {}
    except FileNotFoundError as e:
        raise FileNotFoundError(f"No such file or directory: '{file_path}'") from e


def write_yaml_file(file_path: str, data: dict) -> None:
    """
    Write the given data to a YAML file.
    
    Args:
    - file_path: The path of the YAML file to write to.
    - data: A dictionary containing the contents to write to the YAML file.
    """
    yaml = YAML()
    yaml.preserve_quotes = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    with open(file_path, "w") as yml_file:
        yaml.dump(data, yml_file)

def find_yaml_path(entity_name: str, resource_type: str) -> Optional[str]:
    """
    Find the path to the YAML file for the given entity (model or source).
    
    Args:
    - entity_name: The name of the model or source to find.
    - resource_tyoe: The type of entity to find ("model", "seed", "snapshot", or "source").
    
    Returns:
    - The path to the YAML file containing the entity, if found; otherwise, None.
    """

    if resource_type == "source":
        resource_paths = "models"
    else:
        resource_paths = get_entity_paths_from_dbt_project(resource_type)
        resource_paths = resource_paths[0]

    if not resource_paths:
        raise Exception(f"No {resource_type} paths defined in dbt_project.yml.")    

    for root, dirs, files in os.walk(resource_paths):
        for file in files:
            if file.endswith(".yml") or file.endswith(".yaml"):
                yml_path = os.path.join(root, file)
                with open(yml_path, "r") as yml_file:
                    yaml = YAML()
                    yml_data = yaml.load(yml_file)
                
                # Check for models or sources in the YAML data
                if resource_type != "source" and yml_data and resource_type + "s" in yml_data:
                    for model in yml_data[resource_type + "s"]:
                        if model.get("name") == entity_name:
                            return yml_path
                elif resource_type == "source" and yml_data and resource_type + "s" in yml_data:
                    for source in yml_data[resource_type + "s"]:
                        for table in source.get("tables", []):
                            if table.get("name") == entity_name:
                                return yml_path
    return None

def add_tests_to_yaml(
    yaml_entity: dict, 
    test_names: List[str], 
    columns: Optional[List[str]] = None,
    test_params: Optional[dict] = None
) -> bool:
    """
    Add one or more tests to a YAML entity (e.g., model or source).
    If columns are specified, the tests are added to those columns.
    If no columns are specified, the tests are added at the entity level.
    Returns True if changes were made, False otherwise.

    Args:
    - yaml_entity: The YAML entity to which tests will be added (e.g., model or source table).
    - test_names: A list of test names to add.
    - columns: An optional list of column names to add the tests to.
    - test_params: Optional dictionary with parameters for specific tests.

    Returns:
    - bool: True if changes were made, False otherwise.
    """
    changes_made = False
    test_params = test_params or {}

    if columns:
        # Ensure 'columns' key exists
        if "columns" not in yaml_entity or not yaml_entity["columns"]:
            yaml_entity["columns"] = []
        # Get existing columns
        existing_columns = {col["name"]: col for col in yaml_entity["columns"]}
        for col_name in columns:
            if col_name not in existing_columns:
                raise Exception(
                    f"Column '{col_name}' not found in entity '{yaml_entity.get('name', 'unknown')}'."
                )
            column = existing_columns[col_name]
            tests = column.get("tests")
            if tests is None:
                column["tests"] = CommentedSeq()
                tests = column["tests"]
            for test_name in test_names:
                test_entry = create_test_entry(test_name)
                if test_name not in tests:
                    tests.append(test_entry)
                    changes_made = True
    else:
        # Add tests at the entity level
        tests = yaml_entity.get("tests")
        if tests is None:
            yaml_entity["tests"] = CommentedSeq()
            tests = yaml_entity["tests"]
        for test_name in test_names:
            test_entry = create_test_entry(test_name)
            if test_name not in tests:
                tests.append(test_entry)
                changes_made = True

    return changes_made


def create_test_entry(test_name: str) -> dict:
    """
    Create a test entry with parameters for predefined tests.
    
    Args:
    - test_name: The name of the test.

    Returns:
    - A dictionary or string representing the test entry.
    """
    if test_name == "accepted_values":
        return {test_name: {"values": ["add_values_here"]}}
    elif test_name == "relationships":
        return {test_name: {"to": "ref('model_name')", "field": "column_name"}}
    else:
        return test_name  # Regular test name without parameters

def add_ai_descriptions_to_yaml(
    resource_type: str, entity_name: str, columns: Optional[List[str]], all: bool
) -> bool:
    """
    Add AI-generated descriptions to a YAML file.

    Args:
    - resource_type: The type of resource (model, seed, source, snapshot).
    - entity_name: The name of the entity.
    - columns: List of column names to add descriptions to (optional).
    - all: If True, update all descriptions for the entity.

    Returns:
    - bool: True if changes were made, False otherwise.
    """
    # Load the manifest file using the utility function
    manifest = load_manifest()

    # Locate the entity in the manifest
    entity = find_entity_in_manifest(manifest, entity_name, resource_type)

    # Load the YAML file
    yml_path = find_yaml_path(entity_name, resource_type)
    if not yml_path:
        raise Exception(f"YAML file for {resource_type} '{entity_name}' not found.")

    yml_data = load_yaml_file(yml_path)

    # Extract schema and existing columns
    schema = entity.get("schema", "")
    columns_data = []
    if resource_type == "source":
        sources = yml_data.get("sources", [])
        for source in sources:
                for table in source.get("tables", []):
                    if table["name"] == entity_name:
                        for column in table.get("columns", []):
                            columns_data.append({
                                "name": column["name"],
                                "data_type": column.get("data_type", ""),
                                "description": column.get("description", "")
                            })
    else:
        models = yml_data.get(resource_type + "s", [])
        for model in models:
            if model["name"] == entity_name:
                for column in model.get("columns", []):
                    columns_data.append({
                        "name": column["name"],
                        "data_type": column.get("data_type", ""),
                        "description": column.get("description", "")
                    })

    # Pass all columns if `all` flag is set, otherwise filter by specified columns
    included_columns = [col["name"] for col in columns_data] if all else columns or []
    # Generate descriptions using AI
    entity_description, updated_columns = generate_descriptions_for_entity(entity_name, resource_type, schema, columns_data)
    # Update the YAML file
    changes_made = update_yaml_with_descriptions(yml_path, resource_type, entity_name, entity_description, updated_columns, included_columns, all)

    return changes_made
    

def update_yaml_with_descriptions(
    yml_path: str,
    resource_type: str,
    entity_name: str,
    entity_description: str,
    updated_columns: List[Dict[str, str]],
    included_columns: List[str],
    all: bool
) -> bool:
    """
    Update the YAML file with AI-generated descriptions.

    Args:
    - yml_path (str): Path to the YAML file.
    - resource_type (str): The type of entity ('model', 'source', etc.).
    - entity_name (str): Name of the entity being updated (model or source table).
    - entity_description (str): AI-generated description for the entity.
    - updated_columns (list): List of updated column dictionaries.

    Returns:
    - bool: True if changes were made, False otherwise.
    """
    changes_made = False

    yml_data = load_yaml_file(yml_path)
    
    if resource_type == "source":
        sources = yml_data.get("sources", [])
        for source in sources:
            for table in source.get("tables", []):
                if table["name"] == entity_name:
                    # Update entity description
                    if table.get("description") != entity_description and (all or not included_columns):
                        table["description"] = format_description(entity_description, "add")
                        changes_made = True

                    # Update column descriptions
                    for column in table.get("columns", []):
                        if column["name"] in included_columns:
                            for updated_col in updated_columns:
                                if column["name"] == updated_col["name"]:
                                    if column.get("description") != updated_col["description"]:
                                        column["description"] = format_description(updated_col["description"], "add")
                                        changes_made = True
    else:
        models = yml_data.get(resource_type + "s", [])
        for model in models:
            if model["name"] == entity_name:
                # Update entity description
                if model.get("description") != entity_description and (all or not included_columns):
                    model["description"] = format_description(entity_description, "add")
                    changes_made = True

                # Update column descriptions
                for column in model.get("columns", []):
                    if column["name"] in included_columns:
                        for updated_col in updated_columns:
                            if column["name"] == updated_col["name"]:
                                if column.get("description") != updated_col["description"]:
                                    column["description"] = format_description(updated_col["description"], "add")
                                    changes_made = True

    if changes_made:
        write_yaml_file(yml_path, yml_data)

    return changes_made