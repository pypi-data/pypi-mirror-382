# breeze/utils/manifest_utils.py

import os
import subprocess
import typer
from pathlib import Path
from typing import Optional, Tuple
import json


def run_git_command(command: list, cwd: Optional[str] = None) -> Tuple[bool, str]:
    """
    Run a git command and return success status and output.
    
    Args:
        command: List of command arguments (e.g., ['git', 'checkout', 'main'])
        cwd: Working directory for the command
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()
    except FileNotFoundError:
        return False, "Git is not installed or not in PATH"


def is_git_repository(path: str = ".") -> bool:
    """Check if the current directory is a git repository."""
    git_dir = Path(path) / ".git"
    return git_dir.exists()


def get_current_branch() -> Optional[str]:
    """Get the current git branch name."""
    success, output = run_git_command(['git', 'branch', '--show-current'])
    if success and output:
        return output
    return None


def branch_exists(branch_name: str) -> bool:
    """Check if a branch exists in the repository."""
    success, output = run_git_command(['git', 'branch', '-a'])
    if not success:
        return False
    
    # Check both local and remote branches
    branches = output.split('\n')
    for branch in branches:
        if branch_name in branch.strip():
            return True
    return False


def create_manifest_on_branch(branch: str, manifest_path: str) -> bool:
    """
    Create a manifest file on the specified branch by running dbt compile.
    
    Args:
        branch: The branch to create the manifest on
        manifest_path: Path where the manifest should be created
        
    Returns:
        bool: True if successful, False otherwise
    """
    current_branch = get_current_branch()
    if not current_branch:
        return False
    
    # Checkout the target branch
    success, output = run_git_command(['git', 'checkout', branch])
    if not success:
        typer.echo(f"❌ Failed to checkout branch '{branch}': {output}")
        return False
    
    try:
        # Check if dbt is available
        success, output = run_git_command(['dbt', '--version'])
        if not success:
            typer.echo(f"❌ dbt is not installed or not in PATH: {output}")
            return False
        
        # Create the target directory if it doesn't exist
        manifest_dir = Path(manifest_path).parent
        manifest_dir.mkdir(parents=True, exist_ok=True)
        
        # Run dbt compile to generate the manifest
        typer.echo(f"🔄 Running 'dbt compile' on branch '{branch}'...")
        success, output = run_git_command(['dbt', 'compile'])
        if not success:
            typer.echo(f"❌ dbt compile failed: {output}")
            return False
        
        # Check if manifest was created
        if not Path(manifest_path).exists():
            typer.echo(f"❌ Manifest file was not created at '{manifest_path}'")
            return False
        
        typer.echo(f"✅ Manifest created successfully on branch '{branch}'")
        return True
        
    finally:
        # Always return to the original branch
        checkout_success, checkout_output = run_git_command(['git', 'checkout', current_branch])
        if not checkout_success:
            typer.echo(f"⚠️  Warning: Failed to return to original branch '{current_branch}': {checkout_output}")
            typer.echo(f"   You may need to manually checkout '{current_branch}'")


def fetch_manifest_from_branch(
    branch: str, 
    manifest_path: str = "target/manifest.json",
    output_path: Optional[str] = None,
    create_if_missing: bool = True
) -> bool:
    """
    Fetch manifest.json from a specified branch and save it to the current branch.
    
    Args:
        branch: The branch to fetch the manifest from
        manifest_path: Path to the manifest file in the target branch
        output_path: Where to save the manifest in the current branch (defaults to manifest_path)
        create_if_missing: Whether to create the manifest if it doesn't exist on the target branch
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not is_git_repository():
        typer.echo("❌ Not in a git repository. Please run this command from a git repository.")
        return False
    
    current_branch = get_current_branch()
    if not current_branch:
        typer.echo("❌ Could not determine current branch.")
        return False
    
    if current_branch == branch:
        typer.echo(f"ℹ️  Already on branch '{branch}'. No need to fetch manifest.")
        return True
    
    if not branch_exists(branch):
        typer.echo(f"❌ Branch '{branch}' does not exist.")
        return False
    
    # Set output path if not provided
    if output_path is None:
        output_path = manifest_path
    
    typer.echo(f"🔄 Fetching manifest from branch '{branch}'...")
    
    # Use git show to fetch the file directly from the target branch
    success, output = run_git_command(['git', 'show', f'{branch}:{manifest_path}'])
    if not success:
        if create_if_missing:
            typer.echo(f"⚠️  Manifest file not found at '{manifest_path}' in branch '{branch}'.")
            typer.echo(f"🔄 Attempting to create manifest by running dbt compile on branch '{branch}'...")
            
            # Try to create the manifest by running dbt compile on the target branch
            if not create_manifest_on_branch(branch, manifest_path):
                typer.echo(f"❌ Failed to create manifest on branch '{branch}'.")
                return False
            
            # Try to fetch the manifest again after creation
            success, output = run_git_command(['git', 'show', f'{branch}:{manifest_path}'])
            if not success:
                typer.echo(f"❌ Manifest still not found after creation attempt.")
                return False
        else:
            typer.echo(f"❌ Manifest file not found at '{manifest_path}' in branch '{branch}'.")
            typer.echo(f"   Use --create flag to automatically create the manifest.")
            return False
    
    # Create output directory if it doesn't exist
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the manifest content to the output file
    try:
        with open(output_path, 'w') as f:
            f.write(output)
        
        typer.echo(f"✅ Manifest successfully copied from branch '{branch}' to '{output_path}'")
        
        # Validate the manifest file
        if validate_manifest_file(output_path):
            typer.echo("✅ Manifest file is valid JSON")
            return True
        else:
            typer.echo("⚠️  Warning: Manifest file may be corrupted")
            return False
            
    except Exception as e:
        typer.echo(f"❌ Failed to write manifest file: {e}")
        return False


def validate_manifest_file(manifest_path: str) -> bool:
    """
    Validate that the manifest file is valid JSON.
    
    Args:
        manifest_path: Path to the manifest file
        
    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        with open(manifest_path, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, IOError):
        return False


def get_manifest_info(manifest_path: str) -> Optional[dict]:
    """
    Get basic information from the manifest file.
    
    Args:
        manifest_path: Path to the manifest file
        
    Returns:
        dict: Basic manifest info or None if invalid
    """
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        info = {
            "metadata": manifest.get("metadata", {}),
            "nodes_count": len(manifest.get("nodes", {})),
            "sources_count": len(manifest.get("sources", {})),
            "macros_count": len(manifest.get("macros", {})),
            "docs_count": len(manifest.get("docs", {}))
        }
        
        return info
    except (json.JSONDecodeError, IOError):
        return None


def show_manifest_info(manifest_path: str):
    """Display information about the manifest file."""
    info = get_manifest_info(manifest_path)
    if not info:
        typer.echo("❌ Could not read manifest file")
        return
    
    metadata = info.get("metadata", {})
    typer.echo(f"\n📊 Manifest Information:")
    typer.echo(f"  Generated at: {metadata.get('generated_at', 'Unknown')}")
    typer.echo(f"  dbt version: {metadata.get('dbt_version', 'Unknown')}")
    typer.echo(f"  Project name: {metadata.get('project_name', 'Unknown')}")
    typer.echo(f"  Nodes: {info.get('nodes_count', 0)}")
    typer.echo(f"  Sources: {info.get('sources_count', 0)}")
    typer.echo(f"  Macros: {info.get('macros_count', 0)}")
    typer.echo(f"  Docs: {info.get('docs_count', 0)}")