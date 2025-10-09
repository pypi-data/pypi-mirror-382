# breeze/utils/config_utils.py

import os
import json
import typer
from typing import Optional, Dict, Any
from pathlib import Path


class ConfigManager:
    """Manages configuration settings for the Breeze CLI tool."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".breeze"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            typer.echo(f"⚠️  Warning: Could not load config file: {e}")
            return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            typer.echo(f"❌ Error saving config: {e}")
            raise
    
    def get_manifest_defaults(self) -> Dict[str, str]:
        """Get default manifest settings."""
        config = self._load_config()
        return config.get("manifest", {})
    
    def set_manifest_default_branch(self, branch: str):
        """Set the default branch for manifest operations."""
        config = self._load_config()
        if "manifest" not in config:
            config["manifest"] = {}
        config["manifest"]["default_branch"] = branch
        self._save_config(config)
        typer.echo(f"✅ Default manifest branch set to: {branch}")
    
    def set_manifest_default_path(self, path: str):
        """Set the default path for manifest operations."""
        config = self._load_config()
        if "manifest" not in config:
            config["manifest"] = {}
        config["manifest"]["default_path"] = path
        self._save_config(config)
        typer.echo(f"✅ Default manifest path set to: {path}")
    
    def get_manifest_default_branch(self) -> Optional[str]:
        """Get the default branch for manifest operations."""
        defaults = self.get_manifest_defaults()
        return defaults.get("default_branch")
    
    def get_manifest_default_path(self) -> Optional[str]:
        """Get the default path for manifest operations."""
        defaults = self.get_manifest_defaults()
        return defaults.get("default_path")
    
    def show_config(self):
        """Display current configuration."""
        config = self._load_config()
        if not config:
            typer.echo("No configuration found.")
            return
        
        typer.echo("Current Breeze configuration:")
        typer.echo(f"Config file: {self.config_file}")
        
        if "manifest" in config:
            manifest_config = config["manifest"]
            typer.echo("\nManifest settings:")
            typer.echo(f"  Default branch: {manifest_config.get('default_branch', 'Not set')}")
            typer.echo(f"  Default path: {manifest_config.get('default_path', 'Not set')}")


# Global config manager instance
config_manager = ConfigManager()
