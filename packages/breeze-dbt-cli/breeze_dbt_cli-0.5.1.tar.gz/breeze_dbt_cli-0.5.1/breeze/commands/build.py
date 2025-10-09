# breeze/commands/build.py

import typer
from typing import List, Optional, Tuple
from pathlib import Path
from breeze.models.model import create_empty_sql_file, create_model_yml, create_semantic_model_yml
from breeze.models.source import generate_source_yml
from breeze.utils.db_utils import get_all_sources_from_schema
from breeze.models.tests import create_test_file
from breeze.utils.config_utils import config_manager
from breeze.utils.manifest_utils import (
    fetch_manifest_from_branch,
    show_manifest_info,
    validate_manifest_file,
    get_current_branch
)

build_app = typer.Typer(
    help="""
Build commands to generate models, YAML files, and sources.

Use these commands to create .sql and YAML files for dbt 
models and sources. You can use custom templates or force 
updates to existing files.

Options:
  --help  Show this message and exit.

Commands:
  model    Generate .sql files for dbt models.
  yml      Generate YAML files for one or more dbt models.
  source   Generate YAML files for one or more sources in a schema.
  semantic Generate semantic model YAML files.
  test     Generate custom test SQL files.
  manifest Fetch manifest files from different branches for deferred runs.
"""
)

def process_items_for_generation(
    item_names: List[str],
    generate_function,
    generate_context:str,
    **kwargs,
) -> Tuple[List[str], List[str], List[str]]:
    """
    Generic handler to process a list of items, generating corresponding files.
    
    Args:
    - item_names: List of item names to process (e.g., model names or source names).
    - generate_function: The function used to generate files for each item.
    - generate_context: Type of file being generated.
    - generate_args: Dictionary containing arguments to pass to the generation function.

    Returns:
    - Tuple of three lists: (success, skipped, failed).
    """
    success_items = []
    skipped_items = []
    failed_items = []

    for item_name in item_names:
        try:
            file_created = generate_function(item_name, **kwargs)
            if file_created:
                success_items.append(item_name)
            else:
                skipped_items.append(item_name)
        except Exception as e:
            typer.echo(f"❌ Failed to generate {generate_context} for '{item_name}': {e}")
            failed_items.append(item_name)

    return success_items, skipped_items, failed_items

def provide_summary_feedback(success: List[str], skipped: List[str], failed: List[str], entity_type: str):
    """
    Provide summary feedback for the results of file generation.
    
    Args:
    - success: List of items successfully processed.
    - skipped: List of items that were skipped.
    - failed: List of items that failed.
    - entity_type: The type of entity being processed (e.g., "SQL files", "YAML files").
    """
    if success:
        typer.echo(f"\n✅ Successfully created {entity_type} for: {', '.join(success)}")
    if skipped:
        typer.echo(f"\n{entity_type.capitalize()} skipped for: {', '.join(skipped)}. Use --force to overwrite.")
    if failed:
        typer.echo(f"\n❌ Failed to create {entity_type} for: {', '.join(failed)}")

@build_app.command()
def model(
    path: str = typer.Argument(..., help="The path where the model is created / located."),
    model_names: List[str] = typer.Argument(..., help="One or more model names to generate .sql files for."),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite existing files."),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Path to a custom SQL template."),
    no_subfolder: bool = typer.Option(False, "--no-subfolder", "-n", help="Store the .sql file directly in the specified path without a subfolder for each model."),

):
    """
    Generate SQL files for dbt models in the specified schema.

    This command will create a .sql file for each specified model. By default, files will get created in `models/path/model_name/model_name.sql.
    You can suppress the subfolder named after the model by using the flag `--no-subfolder` or `-n`.
    The SQL file will contain a default template with `ref()` and `source()` CTEs for referencing other models.

    If a file already exists, it will not be overwritten unless the `--force` option is used.

    You can use a custom template for the SQL file created by including the `--template` flag and passing the path of your template.

    Options:
      - `path`: Name of the folder where the models will be created.
      - `model_names`: One or more model names for which to generate .sql files.
      - `--force`, `-f`: Overwrite existing files.
      - `--template`, `-t`: Use a custom SQL template file.
      - `--no_subfolder`, `-n`: Store .sql file in models/folder_name.

    Examples:
      - Generate .sql files for `model1` and `model2` in `my_folder`:

        \b
        breeze build model my_folder model1 model2

      - Force overwrite existing .sql file for `model1`:

        \b
        breeze build model my_schema model1 --force

      - Use a custom SQL template for `model1`:

        \b
        breeze build model my_schema model1 --template path/to/custom_template.sql
    """

    success_models, skipped_models, failed_models = process_items_for_generation(
        model_names, 
        create_empty_sql_file, 
        "SQL", 
        path=path, 
        force=force, 
        template_path=template, 
        no_subfolder=no_subfolder
    )

    provide_summary_feedback(success_models, 
                             skipped_models, 
                             failed_models, 
                             "SQL files")


@build_app.command()
def yml(
    model_names: List[str] = typer.Argument(..., help="One or more model names to generate YAML files for."),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite existing files."),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Path to a custom YAML template."),
    describe: bool = typer.Option(False, "--describe", "-d", help="Use AI assistant to generate descriptions."),

):
    """
    Generate YAML files for one or more models.

    This command creates a YAML file for each specified model, containing metadata about the model and its columns.
    The generated YAML file will include column names, data types, and placeholders for adding tests.

    If the YAML file already exists, it will not be overwritten unless the `--force` option is used.

    You can use a custom template for the YAML file created by including the `--template` flag and passing the path of your template.

    Options:
      - `model_names`: One or more model names for which to generate YAML files.
      - `--force`, `-f`: Overwrite existing YAML files.
      - `--template`, `-t`: Use a custom YAML template file.
      - `--describe`, `-d`: Use AI assistant to generate descriptions for the model and its columns.


    Examples:
      - Generate YAML files for `model1` and `model2`:

        \b
        breeze build yml model1 model2

      - Force overwrite an existing YAML file for `model1`:

        \b
        breeze build yml model1 --force

      - Use a custom YAML template for `model1`:

        \b
        breeze build yml model1 --template path/to/custom_template.yml
    """

    success_models, skipped_models, failed_models = process_items_for_generation(
        model_names,
        create_model_yml,
        "YAML",
        force=force,
        template_path=template,
        describe=describe,
    )

    provide_summary_feedback(success_models, skipped_models, failed_models, "YAML files")


@build_app.command()
def source(
    schema_name: str = typer.Argument(..., help="The schema of the source, and by default, the folder where source .yml will be created."),
    source_names: Optional[List[str]] = typer.Argument(None, help="One or more source names to generate YAML files for."),
    all_sources: bool = typer.Option(False, "--all", "-a", help="Build YAML files for all sources in the schema."),    
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite existing files."),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Path to a custom YAML template."),
    describe: bool = typer.Option(False, "--describe", "-d", help="Generate descriptions using AI."),
    catalog: Optional[str] = typer.Option (None, "--catalog", "-c", help="Specify a different Catalog."),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Custom path to store the source YAML files.")
):
    """
    Generate YAML files for one or more sources.

    This command creates a YAML file for each specified source, containing metadata about the source and its columns.
    The generated YAML file will include column names, data types, and placeholders for adding tests.

    If the YAML file already exists, it will not be overwritten unless the `--force` option is used.

    You can use a custom template for the YAML file created by including the `--template` flag and passing the path of your template.

    Options:
      - `schema_name`: The schema of the source, and by default, the folder where source .yml will be created..
      - `source_names`: One or more source names for which to generate YAML files.
      - `--all`, `-a`: Build YAML files for all sources in the schema.
      - `--force`, `-f`: Overwrite existing YAML files.
      - `--template`, `-t`: Use a custom YAML template file.
      - `--describe`, `-d`: Use AI to generate descriptions.
      - `--catalog`, `-c`: Specify a different catalog.
      - `--path`, `-p`: Create the source YAML file in the custom-path.

    Examples:
      - Generate YAML files for `source1` and `source2` with schema `my_schema`:

        \b
        breeze build source my_schema source1 source2

      - Force overwrite an existing YAML file for `source1`:

        \b
        breeze build source my_schema source1 -f

      - Use a custom YAML template for `source1`:

        \b
        breeze build source my_schema source1 --template path/to/source_template.yml
    """
    # Validate input: Either source_names or --all must be provided
    if not source_names and not all_sources:
        typer.echo("❌ Please provide source names or use the --all flag to build YAMLs for all sources.")
        raise typer.Exit(code=1)

    # If --all flag is set, fetch all sources from the schema
    if all_sources:
        try:
            source_names = get_all_sources_from_schema(schema_name, catalog if catalog else None)
        except Exception as e:
            typer.echo(f"❌ Failed to retrieve sources from schema '{schema_name}': {e}")
            raise typer.Exit(code=1)

    success_sources, skipped_sources, failed_sources = process_items_for_generation(
        source_names, 
        generate_source_yml, 
        "YML", 
        schema_name=schema_name, 
        force=force, 
        template_path=template, 
        path=path, 
        describe=describe,
        catalog=catalog
    )

    provide_summary_feedback(success_sources, 
                             skipped_sources, 
                             failed_sources, 
                             "source YAML files")


@build_app.command()
def semantic(
    model_names: List[str] = typer.Argument(..., help="One or more model names for which to generate semantic YAML files."),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite existing files."),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Path to a custom semantic model template."),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Custom directory path for the .yml files."),
):
    """
    Create boilerplate .yml files for semantic models corresponding to dbt models.

    This command creates a semantic model YAML file for each specified dbt model.

    Options:
      - `model_names`: One or more dbt model names for which to generate semantic YAML files.
      - `--force`, `-f`: Overwrite existing YAML files.
      - `--template`, `-t`: Use a custom YAML template file.
      - `--path`, `-p`: Specify a custom output path for the semantic YAML files.

    Examples:
      - Generate semantic model YAMLs for `model1` and `model2`:

        \b
        breeze build semantic model1 model2

      - Force overwrite an existing semantic model YAML for `model1`:

        \b
        breeze build semantic model1 --force

      - Use a custom YAML template for `model1`:

        \b
        breeze build semantic model1 --template path/to/custom_template.yml
    """
    success_models, skipped_models, failed_models = process_items_for_generation(
        model_names,
        create_semantic_model_yml,
        "YML",
        force=force,
        template_path=template,
        path=path,
    )

    provide_summary_feedback(success_models, skipped_models, failed_models, "semantic model YAML files")


@build_app.command()
def test(
    test_names: List[str] = typer.Argument(..., help="One or more test names to create."),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite if test files already exist."),
):
    """
    Create custom test SQL files in the test-paths specified in dbt_project.yml.

    Options:
      - `test_names`: One or more custom test names to create.
      - `--force`, `-f`: Overwrite test files if they already exist.

    Examples:
      - Create tests `unique_values` and `accepted_values`:

        \b
        breeze build test unique_values accepted_values

      - Force overwrite existing tests:

        \b
        breeze build test unique_values --force
    """
    success_tests, skipped_tests, failed_tests = process_items_for_generation(
        test_names, 
        create_test_file, 
        "SQL",
        force=force
    )

    provide_summary_feedback(success_tests, skipped_tests, failed_tests, "test files")


@build_app.command()
def manifest(
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Branch to fetch manifest from (default: main)."),
    fetch_path: Optional[str] = typer.Option(None, "--fetch-path", "-f", help="Path to manifest file in the target branch (default: target/manifest.json)."),
    store_path: Optional[str] = typer.Option(None, "--store-path", "-s", help="Path to store the manifest file (default: breeze/<branch>/manifest.json)."),
    target: Optional[str] = typer.Option(None, "--target", help="dbt target to use for compilation (default: prod)."),
    info: bool = typer.Option(False, "--info", "-i", help="Show manifest information after fetching.")
):
    """
    Fetch manifest.json from a specified branch for deferred runs.
    
    This command fetches the manifest.json file from a specified branch
    and copies it to your current branch, enabling deferred runs in dbt.
    This is useful when you want to run dbt with references to models
    from production or main branch without having to build them locally.
    
    Options:
      - `--branch`, `-b`: Branch to fetch manifest from (default: main).
      - `--fetch-path`, `-f`: Path to manifest file in target branch (default: target/manifest.json).
      - `--store-path`, `-s`: Path to store the manifest file (default: breeze/<branch>/manifest.json).
      - `--target`: dbt target to use for compilation (default: prod).
      - `--info`, `-i`: Show manifest information after fetching.
    
    Examples:
      - Fetch manifest from main branch (uses defaults):
        
        \b
        breeze build manifest
        
      - Fetch manifest from main branch with custom fetch path:

        \b
        breeze build manifest --branch main --fetch-path custom/manifest.json

      - Fetch manifest and show info:

        \b
        breeze build manifest --branch main --info
    """
    # Use defaults from config if not provided
    if branch is None:
        branch = config_manager.get_manifest_default_branch()
    
    if fetch_path is None:
        fetch_path = config_manager.get_manifest_default_fetch_path() or "target/manifest.json"
    
    if target is None:
        target = config_manager.get_manifest_default_target()
    
    if store_path is None:
        # Use default store path template and replace {branch} placeholder
        default_store_template = config_manager.get_manifest_default_store_path()
        store_path = default_store_template.replace("{branch}", branch)
        
    # Fetch the manifest
    typer.echo(f"🔄 Generating manifest from branch '{branch}' using target '{target}'...")
    success = fetch_manifest_from_branch(branch, fetch_path, store_path, target)
    
    if success:
        typer.echo(f"✅ Manifest successfully generated from branch '{branch}'")
        
        if info:
            typer.echo("\n📊 Manifest Information:")
            show_manifest_info(store_path)
        
        typer.echo(f"\n💡 You can now run dbt with deferred references:")
        # Extract directory from store path for --state flag
        store_dir = str(Path(store_path).parent)
        typer.echo(f"   dbt run --defer --state {store_dir}/")
    else:
        typer.echo("❌ Failed to generate manifest")
        raise typer.Exit(1)