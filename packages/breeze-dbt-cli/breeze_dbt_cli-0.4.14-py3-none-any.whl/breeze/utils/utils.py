from ruamel.yaml.scalarstring import FoldedScalarString

def format_description(description: str, command: str, resource_type: str = None, line_length: int = 70) -> str:
    """
    Format a description to use the YAML block-style `>` with wrapped lines.

    Args:
    - description: The description text to format.
    - line_length: Maximum length of each line.

    Returns:
    - str: The formatted description.
    """
    if not description or len(description) <= line_length:
        return description  # Return as-is if no formatting is needed

    words = description.split()
    formatted_lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 > line_length:  # +1 for space
            formatted_lines.append(current_line)
            current_line = word
        else:
            current_line += (" " + word) if current_line else word

    if current_line:
        formatted_lines.append(current_line)

    if command == "build":
        # Construct the formatted YAML block manually
        formatted_description = "> \n"  # Start with the block style marker
        for line in formatted_lines:
            if resource_type in ["snapshot_column", "seed_column", "model_column", "source_table"]:
                formatted_description += f"          {line}\n"  # Add 10 spaces for indentation
            if resource_type in ["model_table", "seed_table", "snapshot_table"]:
                formatted_description += f"      {line}\n"  # Add 6 spaces for indentation
            if resource_type in ["source_column"]:
                formatted_description += f"              {line}\n"  # Add 14 spaces for indentation

        return formatted_description.strip()
    
    if command == "add":
        formatted_description = " ".join(formatted_lines)
        folded_string = FoldedScalarString(formatted_description)
        return folded_string