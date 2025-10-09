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


def create_manifest_on_branch(branch: str, fetch_path: str, target: str = "prod") -> str:
    """
    Create a manifest file on the specified branch using git worktree.
    Returns the content of the manifest file.

    Args:
        branch: The branch to create the manifest on
        fetch_path: Path where the manifest should be created
        target: The dbt target to use for compilation
        
    Returns:
        str: The content of the manifest file, or None if failed
    """
    # Create a temporary worktree for the target branch
    temp_worktree_path = Path.home() / ".breeze" / f"temp_worktree_{branch}"
    
    try:
        # Create worktree for the target branch
        success, output = run_git_command(['git', 'worktree', 'add', str(temp_worktree_path), branch])
        if not success:
            typer.echo(f"❌ Failed to create worktree for branch '{branch}': {output}")
            return None
        
        # Change to the worktree directory
        original_cwd = os.getcwd()
        os.chdir(temp_worktree_path)
        
        try:
            # Check if dbt is available
            success, output = run_git_command(['dbt', '--version'])
            if not success:
                typer.echo(f"❌ dbt is not installed or not in PATH: {output}")
                return None

            # Create the target directory if it doesn't exist
            manifest_dir = Path(fetch_path).parent
            manifest_dir.mkdir(parents=True, exist_ok=True)

            # Run dbt clean, deps, and parse to generate a fresh manifest
            success, output = run_git_command(['dbt', 'clean', '--target', target])
            if not success:
                typer.echo(f"❌ dbt clean failed: {output}")
                return None
            
            success, output = run_git_command(['dbt', 'deps', '--target', target])
            if not success:
                typer.echo(f"❌ dbt deps failed: {output}")
                return None
            
            success, output = run_git_command(['dbt', 'parse', '--target', target])
            if not success:
                typer.echo(f"❌ dbt parse failed: {output}")
                return None
            
            # Check if manifest was created
            if not Path(fetch_path).exists():
                typer.echo(f"❌ Manifest file was not created at '{fetch_path}'")
                return None
            
            # Read the manifest content
            with open(fetch_path, 'r') as f:
                manifest_content = f.read()

            return manifest_content
            
        finally:
            # Always return to original directory
            os.chdir(original_cwd)
            
    finally:
        # Clean up worktree
        if temp_worktree_path.exists():
            run_git_command(['git', 'worktree', 'remove', str(temp_worktree_path), '--force'])


def fetch_manifest_from_branch(
    branch: str, 
    fetch_path: str = "target/manifest.json",
    store_path: Optional[str] = None,
    target: str = "prod"
) -> bool:
    """
    Fetch manifest.json from a specified branch and save it to the current branch.
    
    Args:
        branch: The branch to fetch the manifest from
        fetch_path: Path to the manifest file in the target branch
        store_path: Where to save the manifest in the current branch (defaults to breeze/<branch>/manifest.json)
        target: The dbt target to use for compilation
        
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

    if not branch_exists(branch):
        typer.echo(f"❌ Branch '{branch}' does not exist.")
        return False
    
    # Set store path if not provided
    if store_path is None:
        # Default to breeze/<branch>/manifest.json
        store_path = f"breeze/{branch}/manifest.json"
    
    # Always generate fresh manifest from the target branch
    # Generate the manifest by running dbt parse on the target branch
    manifest_content = create_manifest_on_branch(branch, fetch_path, target)
    if manifest_content is None:
        typer.echo(f"❌ Failed to create manifest on branch '{branch}'.")
        return False
    
    # Store manifest content temporarily in .breeze directory
    temp_manifest_path = Path.home() / ".breeze" / f"temp_{branch}_manifest.json"
    temp_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(temp_manifest_path, 'w') as f:
            f.write(manifest_content)

        # Copy to the final destination
        output_path_obj = Path(store_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(store_path, 'w') as f:
            f.write(manifest_content)

        # Clean up temporary file
        temp_manifest_path.unlink()
        
        # Validate the manifest file
        if validate_manifest_file(store_path):
            return True
        else:
            typer.echo("⚠️  Warning: Manifest file may be corrupted")
            return False

    except Exception as e:
        typer.echo(f"❌ Failed to process manifest: {e}")
        # Clean up temporary file if it exists
        if temp_manifest_path.exists():
            temp_manifest_path.unlink()
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