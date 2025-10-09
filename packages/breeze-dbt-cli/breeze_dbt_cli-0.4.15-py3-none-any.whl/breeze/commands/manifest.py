# breeze/commands/manifest.py

import typer
from typing import Optional
from breeze.utils.config_utils import config_manager
from breeze.utils.manifest_utils import (
    fetch_manifest_from_branch,
    show_manifest_info,
    validate_manifest_file,
    get_current_branch
)


manifest_app = typer.Typer(
    help="""
Manifest management commands for dbt deferred runs.

Use these commands to manage manifest files from different branches,
enabling deferred runs in dbt by using manifests from production or
main branches.

Commands:
  build  Fetch manifest from a specified branch.
  set    Configure default branch and path settings.
"""
)


@manifest_app.command()
def build(
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Branch to fetch manifest from."),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Path to manifest file in the target branch."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output path for the manifest file."),
    info: bool = typer.Option(False, "--info", "-i", help="Show manifest information after fetching."),
    create: bool = typer.Option(True, "--create/--no-create", help="Create manifest if it doesn't exist on target branch.")
):
    """
    Fetch manifest.json from a specified branch for deferred runs.
    
    This command fetches the manifest.json file from a specified branch
    and copies it to your current branch, enabling deferred runs in dbt.
    This is useful when you want to run dbt with references to models
    from production or main branch without having to build them locally.
    
    Options:
      - `--branch`, `-b`: Branch to fetch manifest from (uses default if not specified).
      - `--path`, `-p`: Path to manifest file in target branch (default: target/manifest.json).
      - `--output`, `-o`: Output path for manifest file (defaults to same as --path).
      - `--info`, `-i`: Show manifest information after fetching.
      - `--create/--no-create`: Create manifest if it doesn't exist on target branch (default: --create).
    
    Examples:
      - Fetch manifest from main branch:
        
        \b
        breeze build manifest --branch main
        
      - Fetch manifest with custom path:
        
        \b
        breeze build manifest --branch main --path custom/manifest.json
        
      - Fetch manifest and show info:
        
        \b
        breeze build manifest --branch main --info
        
      - Fetch manifest without creating if missing:
        
        \b
        breeze build manifest --branch main --no-create
    """
    # Use defaults from config if not provided
    if branch is None:
        branch = config_manager.get_manifest_default_branch()
        if branch is None:
            typer.echo("❌ No branch specified. Use --branch or set a default with 'breeze set manifest --branch <branch>'")
            raise typer.Exit(1)
    
    if path is None:
        path = config_manager.get_manifest_default_path() or "target/manifest.json"
    
    typer.echo(f"🔄 Fetching manifest from branch '{branch}'...")
    
    # Fetch the manifest
    success = fetch_manifest_from_branch(branch, path, output, create)
    
    if success:
        output_path = output or path
        typer.echo(f"✅ Manifest successfully fetched from branch '{branch}'")
        
        if info:
            typer.echo("\n📊 Manifest Information:")
            show_manifest_info(output_path)
        
        typer.echo(f"\n💡 You can now run dbt with deferred references:")
        typer.echo(f"   dbt run --defer --state {output_path}")
    else:
        typer.echo("❌ Failed to fetch manifest")
        raise typer.Exit(1)


@manifest_app.command()
def set(
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
        breeze set manifest --branch main
        
      - Set default path:
        
        \b
        breeze set manifest --path target/manifest.json
        
      - Show current settings:
        
        \b
        breeze set manifest --show
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
