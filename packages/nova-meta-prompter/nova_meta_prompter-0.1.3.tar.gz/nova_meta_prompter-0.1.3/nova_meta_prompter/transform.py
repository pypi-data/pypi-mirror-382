"""
Amazon Nova Prompt Transformer

Simple API to align prompts with Amazon Nova guidelines.
"""

import time
import boto3
from pathlib import Path
from botocore.config import Config


def _get_data_path():
    """Get the path to the data directory."""
    return Path(__file__).parent.parent / "data"


def _load_text_file(directory, filename):
    """Load a specific text file."""
    with open(Path(directory) / filename, 'r', encoding='utf-8') as f:
        return f.read()


def _load_text_files(directory):
    """Load all text files from a directory into a dictionary."""
    files_dict = {}
    for filepath in Path(directory).glob('*.txt'):
        files_dict[filepath.stem] = filepath.read_text(encoding='utf-8')
    return files_dict


def _get_bedrock_client():
    """Create and configure a Bedrock client."""
    config = Config(read_timeout=1000, max_pool_connections=1000)
    return boto3.client(service_name='bedrock-runtime', config=config)


def _bedrock_converse(client, system_input, message, tool_list, model_id, inference_config):
    """Make a conversation request to Bedrock with retry logic."""
    # Set tool choice if tools are provided
    if tool_list and 'tools' in tool_list and tool_list['tools']:
        tool_list["toolChoice"] = {"tool": {"name": tool_list['tools'][0]['toolSpec']['name']}}

    try:
        return client.converse(
            modelId=model_id,
            system=[system_input],
            messages=[message],
            inferenceConfig=inference_config,
            toolConfig=tool_list
        )
    except client.exceptions.ThrottlingException:
        print('Request throttled, waiting 60 seconds...')
        # nosemgrep: arbitrary-sleep
        time.sleep(60)
        return _bedrock_converse(client, system_input, message, tool_list, model_id, inference_config)


def transform_prompt(prompt, model_id=None, boto_client=None):
    """Transform any prompt to align with Amazon Nova guidelines.

    Args:
        prompt (str): The prompt to transform
        model_id (str, optional): Model to use. Defaults to 'us.amazon.nova-premier-v1:0'
        boto_client: Boto3 bedrock-runtime client. If None, creates a new client.

    Returns:
        dict: Dictionary containing:
            - thinking: Analysis of the transformation process
            - nova_draft: Initial transformed prompt
            - reflection: Reflection on the draft
            - nova_final: Final Nova-aligned prompt

    Example:
        >>> from nova_meta_prompter import transform_prompt
        >>> result = transform_prompt("Summarize this document: {document}")
        >>> print(result['nova_final'])
    """
    # Default model
    if model_id is None:
        model_id = 'us.amazon.nova-premier-v1:0'

    # Create client if not provided
    client = boto_client or _get_bedrock_client()
    client_provided = boto_client is not None

    try:
        # Load data files
        data_path = _get_data_path()
        system_prompt = _load_text_file(data_path / "prompts", "prompt_nova_migration_system.txt")
        prompt_template = _load_text_file(data_path / "prompts", "prompt_nova_migration.txt")
        migration_guidelines = _load_text_file(data_path / "docs" / "nova", "migration_guidelines.txt")
        nova_docs = "\n".join(_load_text_files(data_path / "nova" / "general").values())

        # Format prompt
        formatted_prompt = prompt_template.format(
            nova_docs=nova_docs,
            migration_guidelines=migration_guidelines,
            current_prompt=prompt,
        )

        # Define tool for structured output
        tool_list = {
            "tools": [{
                "toolSpec": {
                    "name": "convert_prompt",
                    "description": "Transforms any prompt to Nova-aligned format",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "thinking": {
                                    "type": "string",
                                    "description": "Detailed analysis of the transformation process"
                                },
                                "nova_draft": {
                                    "type": "string",
                                    "description": "The transformed Nova-aligned prompt"
                                },
                                "reflection": {
                                    "type": "string",
                                    "description": "Reflection on the draft prompt"
                                },
                                "nova_final": {
                                    "type": "string",
                                    "description": "Final Nova-aligned prompt based on reflections"
                                }
                            },
                            "required": ["thinking", "nova_draft", "reflection", "nova_final"]
                        }
                    }
                }
            }]
        }

        # Prepare messages
        system_message = {"text": system_prompt}
        message = {"role": "user", "content": [{"text": formatted_prompt}]}
        inference_config = {"maxTokens": 16000, "topP": 0.4}

        # Execute transformation
        response = _bedrock_converse(client, system_message, message, tool_list, model_id, inference_config)
        return response["output"]["message"]["content"][0]["toolUse"]["input"]

    finally:
        # Only close client if we created it
        if not client_provided:
            client.close()


if __name__ == "__main__":
    result = transform_prompt("Summarize this document: {MY_DOCUMENT}")
    print("=" * 80)
    print("FINAL NOVA-ALIGNED PROMPT:")
    print("=" * 80)
    print(result['nova_final'])
