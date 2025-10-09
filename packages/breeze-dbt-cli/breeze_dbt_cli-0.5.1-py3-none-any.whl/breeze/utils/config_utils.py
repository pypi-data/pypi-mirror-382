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
        self._ensure_default_config()
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True)
    
    def _ensure_default_config(self):
        """Ensure default configuration exists if config file doesn't exist."""
        if not self.config_file.exists():
            default_config = {
                "manifest": {
                    "default_branch": "main",
                    "default_fetch_path": "target/manifest.json",
                    "default_target": "prod",
                    "default_store_path": "breeze/{branch}/manifest.json"
                }
            }
            self._save_config(default_config)
    
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
        typer.echo(f"📁 Configuration saved to: {self.config_file}")
    
    def set_manifest_default_fetch_path(self, fetch_path: str):
        """Set the default fetch path for manifest operations."""
        config = self._load_config()
        if "manifest" not in config:
            config["manifest"] = {}
        config["manifest"]["default_fetch_path"] = fetch_path
        self._save_config(config)
        typer.echo(f"✅ Default manifest fetch path set to: {fetch_path}")
        typer.echo(f"📁 Configuration saved to: {self.config_file}")
    
    def set_manifest_default_target(self, target: str):
        """Set the default target for manifest operations."""
        config = self._load_config()
        if "manifest" not in config:
            config["manifest"] = {}
        config["manifest"]["default_target"] = target
        self._save_config(config)
        typer.echo(f"✅ Default manifest target set to: {target}")
        typer.echo(f"📁 Configuration saved to: {self.config_file}")
    
    def set_manifest_default_store_path(self, store_path: str):
        """Set the default store path for manifest operations."""
        config = self._load_config()
        if "manifest" not in config:
            config["manifest"] = {}
        config["manifest"]["default_store_path"] = store_path
        self._save_config(config)
        typer.echo(f"✅ Default manifest store path set to: {store_path}")
        typer.echo(f"📁 Configuration saved to: {self.config_file}")
    
    def get_manifest_default_branch(self) -> Optional[str]:
        """Get the default branch for manifest operations."""
        defaults = self.get_manifest_defaults()
        return defaults.get("default_branch", "main")  # Default to 'main'
    
    def get_manifest_default_fetch_path(self) -> Optional[str]:
        """Get the default fetch path for manifest operations."""
        defaults = self.get_manifest_defaults()
        return defaults.get("default_fetch_path", "target/manifest.json")
    
    def get_manifest_default_target(self) -> str:
        """Get the default target for manifest operations."""
        defaults = self.get_manifest_defaults()
        return defaults.get("default_target", "prod")  # Default to 'prod'
    
    def get_manifest_default_store_path(self) -> str:
        """Get the default store path for manifest operations."""
        defaults = self.get_manifest_defaults()
        return defaults.get("default_store_path", "breeze/{branch}/manifest.json")
    
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
            typer.echo(f"  Default fetch path: {manifest_config.get('default_fetch_path', 'Not set')}")
            typer.echo(f"  Default target: {manifest_config.get('default_target', 'Not set')}")
            typer.echo(f"  Default store path: {manifest_config.get('default_store_path', 'Not set')}")


# Global config manager instance
config_manager = ConfigManager()
