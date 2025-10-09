from openai import OpenAI
from breeze.utils.dbt_utils import get_profile, get_profile_name_from_dbt_project, load_manifest
from breeze.utils.utils import format_description
import time
import json
import typer
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel
from alive_progress import alive_bar 
import time
import os

class Columns(BaseModel):
    column: str
    description: str

class Model(BaseModel):
    model: str
    description: str
    columns: list[Columns]

def get_ai_token() -> str:
    """
    Retrieve the AI token from the dbt `profiles.yml` file.

    Returns:
        - str: The AI token required for interacting with OpenAI services.

    Raises:
        - Exception: If the `ai_token` key is not found in the dbt `profiles.yml` file.
    """
    profile_name = get_profile_name_from_dbt_project()
    profile = get_profile()
    ai_token = (
        profile.get(profile_name, {})
        .get("outputs", {})
        .get(profile[profile_name].get("target", ""), {})
        .get("ai_token")
    )
    
    if not ai_token:
        raise Exception("❌ AI token not found in dbt profiles.yml. Please add 'ai_token' to your profile.")
    
    return ai_token

def generate_description(prompt: str) -> str:
    """
    Generate a structured description using the AI assistant with context 
    from the dbt `manifest.json` file.

    Args:
        - prompt (str): The prompt text to send to the AI assistant for description generation.

    Returns:
        - str: A JSON-structured string containing the AI-generated description, including 
        the entity and its columns.

    Raises:
        - Exception: If the AI token is not found or the AI interaction fails.

    """

    openai_api_key = get_ai_token()
    client = OpenAI(api_key=openai_api_key)

    file = client.files.create(
        file=open(os.path.join("target", "manifest.json"), "rb"),
        purpose='assistants'
        )    
    
    assistant_instructions = """
        You are a data analyst that is an expert about the database objects in the dbt project. 
        Your job is to create consice descriptions of models, and their columns by understanding 
        the relationship between models, sources, and seeds using the manifest file. 
        When describing the model itself, take into account its schema and resource type, as it 
        indicates what layer of the data pipleline that model belongs to. Your response should list 
        the model and its description, as well as each column and its description. Do not make any 
        assumptions and keep the descriptions short. When relevant, talk about the relationship about 
        the model in question and its parents / children.
        """

    # First assistant to get unstructured answer using the manifest
    assistant = client.beta.assistants.create(
        name="Data Describer",
        instructions=assistant_instructions,
        model="gpt-4o-mini",
        tools=[{"type": "code_interpreter"}],
        tool_resources={
            "code_interpreter": {
                "file_ids": [file.id]
                }
            }
        )

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
        )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        )

    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id).data
        message_content = messages[-1].content[0].text.value
    else:
        raise Exception(f"❌ Assistant run failed with status: {run.status}")


    completion_assistant_instructions = """
        You are an expert at structured data extraction. You will be given 
        unstructured text and should convert it into the given structure.
        """

    # 2nd response that formats the output
    completion = client.beta.chat.completions.parse(
        messages=[
            {"role": "system", "content": completion_assistant_instructions},
            {"role": "user", "content": f"Format the following as JSON:\n\n{message_content}\n"}
            ],
        model="gpt-4o-mini",
        response_format={
            'type': 'json_schema',
            'json_schema': {
                "name":"Model", 
                "schema": Model.model_json_schema(),
                }
            }
        )

    structured_message = completion.choices[0].message.content

    return structured_message

def generate_descriptions_for_entity(
    entity_name: str, 
    resource_type: str,
    schema: str,
    columns_data: List[Dict[str, str]], 
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Generate AI-powered descriptions for a given dbt entity (model, source, etc.) and its columns.

    Args:
        - entity_name (str): The name of the entity (e.g., model, source).
        - resource_type (str): The type of resource (e.g., "model", "source").
        - schema (str): The schema to which the entity belongs.
        - columns_data (List[Dict[str, str]]): A list of dictionaries containing column metadata 
            (e.g., column name and data type).

    Returns:
        Tuple[str, List[Dict[str, str]]]: 
            - A string containing the description for the entity.
            - An updated list of column metadata, each with its description.

    Raises:
        - Exception: If AI description generation fails.
    """

    # Prepare prompt for the AI assistant
    prompt_dict = {
        "entity": entity_name,
        "resource_type": resource_type,
        "columns": [col["name"] for col in columns_data],
        "context": f"Provide a concise description for the {resource_type} {entity_name} with schema {schema} and each column using the manifest for context."
    }

    # Convert the dictionary to a JSON-formatted string
    prompt = json.dumps(prompt_dict, indent=2)

    with alive_bar(1, spinner="wait4", bar=None, title=f"🧠 Using AI assistant to generate descriptions for {resource_type} '{schema}.{entity_name}'...") as bar:
        ai_response = json.loads(generate_description(prompt))
        bar()

    # Extract entity description
    entity_description = ai_response.get("description", "")

    # Update column descriptions
    for col_data in columns_data:
        for ai_col in ai_response.get("columns", []):
            if col_data["name"] == ai_col.get("column"):
                col_data["description"] = ai_col.get("description", "")

    return entity_description, columns_data
