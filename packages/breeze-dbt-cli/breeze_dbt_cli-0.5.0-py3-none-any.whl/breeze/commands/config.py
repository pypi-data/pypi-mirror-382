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
    fetch_path: Optional[str] = typer.Option(None, "--fetch-path", "-f", help="Set default fetch path for manifest operations."),
    target: Optional[str] = typer.Option(None, "--target", help="Set default target for manifest operations."),
    store_path: Optional[str] = typer.Option(None, "--store-path", help="Set default store path for manifest operations."),
    show: bool = typer.Option(False, "--show", help="Show current configuration.")
):
    """
    Configure default settings for manifest operations.
    
    Set default branch and path values that will be used when not
    explicitly specified in manifest commands.
    
    Options:
      - `--branch`, `-b`: Set default branch for manifest operations.
      - `--fetch-path`, `-f`: Set default fetch path for manifest operations.
      - `--target`: Set default target for manifest operations.
      - `--store-path`: Set default store path for manifest operations.
      - `--show`: Show current configuration.
    
    Examples:
      - Set default branch:
        
        \b
        breeze config manifest --branch main
        
      - Set default fetch path:
        
        \b
        breeze config manifest --fetch-path target/manifest.json
        
      - Set default target:
        
        \b
        breeze config manifest --target prod
        
      - Set default store path:
        
        \b
        breeze config manifest --store-path custom/{branch}/manifest.json
        
      - Show current settings:
        
        \b
        breeze config manifest --show
    """
    if show:
        config_manager.show_config()
        return
    
    if branch is None and fetch_path is None and target is None and store_path is None:
        typer.echo("❌ Please specify --branch, --fetch-path, --target, or --store-path to set, or use --show to view current settings")
        raise typer.Exit(1)
    
    if branch:
        config_manager.set_manifest_default_branch(branch)
    
    if fetch_path:
        config_manager.set_manifest_default_fetch_path(fetch_path)
    
    if target:
        config_manager.set_manifest_default_target(target)
    
    if store_path:
        config_manager.set_manifest_default_store_path(store_path)
    
    typer.echo("✅ Configuration updated successfully")
