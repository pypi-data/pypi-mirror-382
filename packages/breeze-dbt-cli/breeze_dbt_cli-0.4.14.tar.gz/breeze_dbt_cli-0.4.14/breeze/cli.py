# breeze/cli.py

import typer
from breeze.commands.build import build_app
from breeze.commands.add import add_app

app = typer.Typer(
    help="""
Breeze CLI Tool

Breeze is a CLI tool designed to streamline the development of dbt models
and sources, automate the creation of .sql and YAML files, and easily add
tests to models and sources.

You can use Breeze to generate model and source YAML files, add dbt tests
to columns, and customize the creation process with templates.

Available command groups:
  - `build`: Generate model, YAML, or source files.
  - `add`: Add dbt tests to models or sources.

Options:
  --help  Show this message and exit.

Commands:
  build  Build commands to generate models, YAML files, and sources.
  add    Add commands to apply tests to models or sources.
"""
)

# Add sub-commands
app.add_typer(build_app, name="build")
app.add_typer(add_app, name="add")  # Add the add_app

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        typer.echo(f"❌ An unexpected error occurred: {e}")
        raise e
