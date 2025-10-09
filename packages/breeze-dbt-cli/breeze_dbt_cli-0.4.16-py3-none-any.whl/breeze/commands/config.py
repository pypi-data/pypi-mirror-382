# breeze/commands/config.py

import typer
from typing import Optional
from breeze.utils.config_utils import config_manager


config_app = typer.Typer(
    help="""
Configuration commands for Breeze CLI.

Use these commands to manage default settings and configuration
for various Breeze operations.

Commands:
  manifest  Configure default settings for manifest operations.
"""
)


@config_app.command()
def manifest(
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Set default branch for manifest operations."),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Set default path for manifest operations."),
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration.")
):
    """
    Configure default settings for manifest operations.
    
    Set default branch and path values that will be used when not
    explicitly specified in manifest commands.
    
    Options:
      - `--branch`, `-b`: Set default branch for manifest operations.
      - `--path`, `-p`: Set default path for manifest operations.
      - `--show`, `-s`: Show current configuration.
    
    Examples:
      - Set default branch:
        
        \b
        breeze config manifest --branch main
        
      - Set default path:
        
        \b
        breeze config manifest --path target/manifest.json
        
      - Show current settings:
        
        \b
        breeze config manifest --show
    """
    if show:
        config_manager.show_config()
        return
    
    if branch is None and path is None:
        typer.echo("❌ Please specify --branch or --path to set, or use --show to view current settings")
        raise typer.Exit(1)
    
    if branch:
        config_manager.set_manifest_default_branch(branch)
    
    if path:
        config_manager.set_manifest_default_path(path)
    
    typer.echo("✅ Configuration updated successfully")
