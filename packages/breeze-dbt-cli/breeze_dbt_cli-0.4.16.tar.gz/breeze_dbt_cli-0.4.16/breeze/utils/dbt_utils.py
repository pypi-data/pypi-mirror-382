# breeze/utils/dbt_utils.py

import os
import json
import yaml
import re
from typing import Optional

def load_manifest() -> dict:
    """
    Load the `manifest.json` file from the dbt `target` directory and return its contents as a dictionary.

    Returns:
        dict: The parsed contents of the `manifest.json` file.

    Raises:
        Exception: If the `manifest.json` file is not found.
    """
    manifest_path = os.path.join("target", "manifest.json")

    if not os.path.exists(manifest_path):
        raise Exception(
            "manifest.json not found. Please run 'dbt compile' or 'dbt build' first."
        )

    # Load the manifest file
    with open(manifest_path, "r") as manifest_file:
        manifest = json.load(manifest_file)
    
    return manifest

def find_entity_in_manifest(manifest: dict, entity_name: str, resource_type: Optional[str] = None) -> dict:
    """
    Find a model, seed, or snapshot in the `manifest.json` file by its name.

    Args:
        manifest (dict): The parsed contents of the `manifest.json` file.
        model_name (str): The name of the model, seed, or snapshot to locate.

    Returns:
        dict: Metadata for the specified model, seed, or snapshot.

    Raises:
        Exception: If the `manifest` is invalid or the specified model is not found.

    """
    if not manifest:
        raise Exception("Manifest is empty or not loaded.")

    # Check nodes for models, seeds, and snapshots
    if "nodes" in manifest:
        for node_id, node in manifest["nodes"].items():
            if node["name"] == entity_name and (resource_type is None or node["resource_type"] == resource_type):
                return node

    # Check sources for source tables
    if "sources" in manifest:
        for source_id, source in manifest["sources"].items():
            if source["name"] == entity_name and (resource_type is None or resource_type == "source"):
                return source

    raise Exception(f"Entity '{entity_name}' not found in manifest.")

def resolve_env_vars(obj):
    """
    Recursively resolve dbt-style env_var references in a dict/list structure.
    Replaces strings like "{{ env_var('DBT_USER') }}" with the value of os.environ['DBT_USER'].
    """
    env_var_pattern = re.compile(r"\{\{\s*env_var\(['\"](\w+)['\"]\)\s*\}\}")

    if isinstance(obj, dict):
        return {k: resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        def replacer(match):
            var_name = match.group(1)
            return os.environ.get(var_name, "")
        return env_var_pattern.sub(replacer, obj)
    else:
        return obj

def get_profile() -> dict:
    """
    Load the `profiles.yml` configuration file for dbt and return its contents.

    Returns:
        dict: The parsed contents of the `profiles.yml` file.

    Raises:
        Exception: If the `profiles.yml` file is not found in the current directory 
                   or the default `~/.dbt/` directory.    
    """

    profiles_path = "profiles.yml"

     # If not found, fall back to ~/.dbt/profiles.yml
    if not os.path.exists(profiles_path):
        home_dir = os.path.expanduser("~")
        profiles_path = os.path.join(home_dir, ".dbt", "profiles.yml")   

    if not os.path.exists(profiles_path):
        raise Exception(
            "\u274c profiles.yml not found. Please place the profiles.yml file in ~/.dbt/. or in your dbt project directory"
        )

    with open(profiles_path, "r") as profiles_file:
        profiles = yaml.safe_load(profiles_file) or {}

    profiles = resolve_env_vars(profiles)

    return profiles

def load_dbt_project() -> dict:
    """
    Load the `dbt_project.yml` file from the current directory and return its contents.

    Returns:
        dict: The parsed contents of the `dbt_project.yml` file.

    Raises:
        Exception: If the `dbt_project.yml` file is not found.
    """
    dbt_project_path = os.path.join(os.getcwd(), "dbt_project.yml")
    if not os.path.exists(dbt_project_path):
        raise Exception(
            "\u274c dbt_project.yml not found. Please ensure you're in a dbt project directory."
        )
    with open(dbt_project_path, "r") as dbt_project_file:
        dbt_project = yaml.safe_load(dbt_project_file) or {}
    return dbt_project

def get_entity_paths_from_dbt_project(entity) -> list:
    """
    Extract the paths for a given entity (e.g., models, seeds, snapshots) from the `dbt_project.yml` file.

    Args:
        entity (str): The entity type (e.g., "model", "seed", "snapshot").

    Returns:
        list: A list of paths defined for the specified entity in `dbt_project.yml`.

    Raises:
        Exception: If the entity paths are not defined or invalid in `dbt_project.yml`.

    """
    dbt_project = load_dbt_project()
    if entity == "source":
        entity_paths = ["models"]
    else:
        entity_paths = dbt_project.get(entity + "-paths")
    
    if not entity_paths or not isinstance(entity_paths, list):
        raise Exception(f"\u274c No valid path for '{entity}' defined in dbt_project.yml.")
    
    return entity_paths

def get_profile_name_from_dbt_project() -> str:
    """
    Retrieve the active profile name from the `dbt_project.yml` file.

    Returns:
        str: The name of the active profile.

    Raises:
        Exception: If the `dbt_project.yml` file is not found or the profile name is missing.

    """
    dbt_project_path = os.path.join(os.getcwd(), "dbt_project.yml")

    if not os.path.exists(dbt_project_path):
        raise Exception(
            "\u274c dbt_project.yml not found. Please ensure you're in a dbt project directory."
        )
    with open(dbt_project_path, "r") as dbt_project_file:
        dbt_project = yaml.safe_load(dbt_project_file)

    profile_name = dbt_project.get("profile") if dbt_project else None

    if not profile_name:
        raise Exception("\u274c Profile name not found in dbt_project.yml.")
    return profile_name

def get_target_from_profile(profile: dict, profile_name: str) -> dict:
    """
    Retrieve the active target configuration for a given profile from the `profiles.yml` file.

    Args:
        profile (dict): The parsed contents of the `profiles.yml` file.
        profile_name (str): The name of the active profile.

    Returns:
        dict: The configuration details for the active target.

    Raises:
        Exception: If the profile or target configuration is missing or invalid.
    """
    profile_data = profile.get(profile_name)
    if not profile_data:
        raise Exception(f"\u274c Profile '{profile_name}' not found in profiles.yml.")

    # Ensure that a target is defined in the profile
    target_name = profile_data.get("target")
    if not target_name or target_name is None:
        raise Exception(f"\u274c No target defined in profile '{profile_name}'.")

    if target_name not in profile_data["outputs"]:
        raise Exception(
            f"\u274c Target '{target_name}' not found in profile '{profile_name}'."
        )

    target = profile_data["outputs"][target_name]
    return target
