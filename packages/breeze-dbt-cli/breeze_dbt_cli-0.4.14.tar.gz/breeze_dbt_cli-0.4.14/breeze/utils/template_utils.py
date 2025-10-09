import os
from typing import Optional
import importlib.resources as pkg_resources

def get_template_content(template_name: str, custom_template_path: Optional[str] = None) -> str:
    """
    Retrieve the content of the template, either from a custom path or from the default templates directory in the library.

    Args:
    - template_name (str): The name of the default template (e.g., "default_model_template.sql").
    - custom_template_path (Optional[str]): Path to a custom template provided by the user.

    Returns:
    - str: Content of the template.

    Raises:
    - FileNotFoundError: If the specified template file is not found.
    """
    if custom_template_path:
        # Use the custom template provided by the user
        if not os.path.exists(custom_template_path):
            raise FileNotFoundError(f"Template file '{custom_template_path}' not found.")
        with open(custom_template_path, "r") as template_file:
            return template_file.read()

    # Load the default template from the package's resources
    try:
        with pkg_resources.open_text('breeze.templates', template_name) as template_file:
            return template_file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Default template '{template_name}' not found in the package resources.")
