# breeze/commands/add.py

import typer
from typing import List, Optional
from breeze.models.model import add_test_to_model
from breeze.models.source import add_test_to_source
from breeze.utils.yaml_utils import add_ai_descriptions_to_yaml

add_app = typer.Typer(
    help="""
Usage: breeze add [OPTIONS] COMMAND [ARGS]...

  Add commands to apply tests to models or sources.

  Use these commands to add dbt tests to models or sources, either at the
  model level or to specific columns.

Options:
  --help  Show this message and exit.

Commands:
  test  Add one or more tests to a model or source.
"""
)


@add_app.command()
def test(
    test_names: List[str] = typer.Argument(
        ..., help="The name(s) of the test(s) to add."
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model name to add the test(s) to."
    ),
    seed: Optional[str] = typer.Option(
        None, "--seed", "-e", help="Seed name to add the test(s) to."
    ),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", "-n", help="Snapshot name to add the test(s) to."
    ),
    source: Optional[str] = typer.Option(
        None, "--source", "-s", help="Source name to add the test(s) to."
    ),
    columns: Optional[str] = typer.Option(
        None,
        "--columns",
        "-c",
        help="Comma-separated column names to add the test(s) to.",
    ),
):
    """
    Add one or more tests to a model or source.

    This command adds one or more tests to a specified model or source. If columns are provided, the tests are added to those columns.
    If no columns are provided, the tests are added at the model or source level.

    You must specify either a `--model`, `--seed`,`--snapshot`, or a `--source`, but not more than one.

    Options:
      - `test_names`: One or more test names to add (e.g., `not_null`, `unique`).
      - `--model`, `-m`: The model name to add the test(s) to.
      - `--seed`, `-e`: The seed name to add the test(s) to.
      - `--snapshot`, `-n`: The source name to add the test(s) to.
      - `--source`, `-s`: The source name to add the test(s) to.
      - `--columns`, `-c`: Comma-separated column names to add the test(s) to.

    Examples:
      - Add `unique` tests to `customer_id` and `email` columns in the `customers` model:

        \b
        breeze add test unique --model customers --columns "customer_id, email"

      - Add `not_null` and `accepted_values` tests to the `status_code` column in the `status` source:

        \b
        breeze add test not_null accepted_values --source status --columns status_code
    """
    # Ensure only one resource type is specified
    resources = [model, seed, source, snapshot]
    if sum(1 for r in resources if r) != 1:
        typer.echo("❌ Please specify either --model, --seed, --source, or --snapshot.")
        raise typer.Exit(code=1)

    # Parse the comma-separated columns into a list
    if columns:
        columns_list = [col.strip() for col in columns.split(",")]
    else:
        columns_list = None

    target_name = model or seed or source or snapshot
    resource_type = (
        "model" if model else "seed" if seed else "source" if source else "snapshot"
    )

    try:
        if model or seed or snapshot:
            success = add_test_to_model(test_names, target_name, resource_type, columns_list)
        elif source:
            success = add_test_to_source(test_names, target_name, columns_list)
        if success:
            tests_added = ", ".join(test_names)
            typer.echo(
                f"✅  Successfully added test(s) '{tests_added}' to {resource_type} '{target_name}'."
            )
        else:
            typer.echo(f"No changes made. Test(s) may already exist.")
    except Exception as e:
        typer.echo(f"❌  Failed to add test(s) to {target_name}: {e}")


@add_app.command()
def description(
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model name to add AI-generated descriptions to."
    ),
    seed: Optional[str] = typer.Option(
        None, "--seed", "-e", help="Seed name to add AI-generated descriptions to."
    ),
    source: Optional[str] = typer.Option(
        None, "--source", "-s", help="Source name to add AI-generated descriptions to."
    ),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", "-n", help="Snapshot name to add AI-generated descriptions to."
    ),
    columns: Optional[str] = typer.Option(
        None,
        "--columns",
        "-c",
        help="Comma-separated column names to add AI-generated descriptions to.",
    ),
    all: bool = typer.Option(
        False, "--all", "-a", help="Generate AI descriptions for everything in the model, seed, snapshot, or source."
    ),
):
    """
    Add AI-generated descriptions to models, seeds, snapshots, or sources.
    
    Use this command to generate AI-powered descriptions for an entire model, seed, source,
    or specific columns.
    """
    # Ensure only one resource type is specified
    resources = [model, seed, source, snapshot]
    if sum(1 for r in resources if r) != 1:
        typer.echo("❌ Please specify either --model, --seed, --source, or --snapshot.")
        raise typer.Exit(code=1)

    target_name = model or seed or source or snapshot
    resource_type = (
        "model" if model else "seed" if seed else "source" if source else "snapshot"
    )

    columns_list = [col.strip() for col in columns.split(",")] if columns else None

    try:
        success = add_ai_descriptions_to_yaml(
            resource_type=resource_type,
            entity_name=target_name,
            columns=columns_list,
            all=all,
        )

        if success:
            typer.echo(
                f"\n✅ Successfully added AI-generated descriptions to {resource_type} '{target_name}'."
            )
        else:
            typer.echo(f"No changes were made.")
    except Exception as e:
        typer.echo(f"\n❌ Failed to add descriptions to {resource_type} '{target_name}': {e}")

