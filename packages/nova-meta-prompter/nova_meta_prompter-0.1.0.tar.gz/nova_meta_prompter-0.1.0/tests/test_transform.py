"""
Tests for the transform module
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from nova_meta_prompter.transform import (
    transform_prompt,
    _get_data_path,
    _load_text_file,
    _load_text_files,
    _get_bedrock_client,
    _bedrock_converse,
)


class TestDataLoading:
    """Test data loading functions"""

    def test_get_data_path(self):
        """Test that data path is correctly resolved"""
        result = _get_data_path()
        assert isinstance(result, Path)
        assert result.name == "data"

    def test_load_text_file(self, tmp_path):
        """Test loading a single text file"""
        # Create test file
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        test_file = test_dir / "test.txt"
        test_file.write_text("test content", encoding='utf-8')

        # Test loading
        content = _load_text_file(test_dir, "test.txt")
        assert content == "test content"

    def test_load_text_files(self, tmp_path):
        """Test loading multiple text files"""
        # Create test files
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1", encoding='utf-8')
        (test_dir / "file2.txt").write_text("content2", encoding='utf-8')
        (test_dir / "ignored.md").write_text("ignored", encoding='utf-8')

        # Test loading
        files = _load_text_files(test_dir)
        assert len(files) == 2
        assert files["file1"] == "content1"
        assert files["file2"] == "content2"
        assert "ignored" not in files


class TestBedrockClient:
    """Test Bedrock client functions"""

    @patch('nova_meta_prompter.transform.boto3.client')
    def test_get_bedrock_client(self, mock_boto_client):
        """Test Bedrock client creation"""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        client = _get_bedrock_client()

        mock_boto_client.assert_called_once()
        assert client == mock_client

    @patch('nova_meta_prompter.transform.time.sleep')
    def test_bedrock_converse_throttling_retry(self, mock_sleep):
        """Test that throttling exceptions trigger retry"""
        mock_client = MagicMock()

        # First call raises throttling, second succeeds
        mock_client.converse.side_effect = [
            mock_client.exceptions.ThrottlingException(),
            {"output": {"message": "success"}}
        ]
        mock_client.exceptions.ThrottlingException = Exception

        system_input = {"text": "system"}
        message = {"role": "user", "content": [{"text": "test"}]}
        tool_list = {"tools": []}
        model_id = "test-model"
        inference_config = {"maxTokens": 1000}

        result = _bedrock_converse(mock_client, system_input, message, tool_list, model_id, inference_config)

        assert mock_client.converse.call_count == 2
        mock_sleep.assert_called_once_with(60)

    def test_bedrock_converse_adds_tool_choice(self):
        """Test that tool choice is added when tools are provided"""
        mock_client = MagicMock()
        mock_client.converse.return_value = {"output": {"message": "success"}}

        system_input = {"text": "system"}
        message = {"role": "user", "content": [{"text": "test"}]}
        tool_list = {
            "tools": [{
                "toolSpec": {
                    "name": "test_tool",
                    "description": "test"
                }
            }]
        }
        model_id = "test-model"
        inference_config = {"maxTokens": 1000}

        _bedrock_converse(mock_client, system_input, message, tool_list, model_id, inference_config)

        assert "toolChoice" in tool_list
        assert tool_list["toolChoice"]["tool"]["name"] == "test_tool"


class TestTransformPrompt:
    """Test the main transform_prompt function"""

    @patch('nova_meta_prompter.transform._bedrock_converse')
    @patch('nova_meta_prompter.transform._load_text_files')
    @patch('nova_meta_prompter.transform._load_text_file')
    @patch('nova_meta_prompter.transform._get_bedrock_client')
    def test_transform_prompt_basic(self, mock_get_client, mock_load_file, mock_load_files, mock_converse):
        """Test basic transform_prompt functionality"""
        # Setup mocks
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_load_file.return_value = "template {nova_docs} {migration_guidelines} {current_prompt}"
        mock_load_files.return_value = {"doc1": "nova docs"}

        mock_converse.return_value = {
            "output": {
                "message": {
                    "content": [{
                        "toolUse": {
                            "input": {
                                "thinking": "analysis",
                                "nova_draft": "draft",
                                "reflection": "reflection",
                                "nova_final": "final prompt"
                            }
                        }
                    }]
                }
            }
        }

        # Test
        result = transform_prompt("Test prompt")

        # Verify
        assert result["thinking"] == "analysis"
        assert result["nova_draft"] == "draft"
        assert result["reflection"] == "reflection"
        assert result["nova_final"] == "final prompt"
        mock_client.close.assert_called_once()

    @patch('nova_meta_prompter.transform._bedrock_converse')
    @patch('nova_meta_prompter.transform._load_text_files')
    @patch('nova_meta_prompter.transform._load_text_file')
    def test_transform_prompt_with_custom_client(self, mock_load_file, mock_load_files, mock_converse):
        """Test transform_prompt with provided boto_client"""
        # Setup mocks
        custom_client = MagicMock()
        mock_load_file.return_value = "template {nova_docs} {migration_guidelines} {current_prompt}"
        mock_load_files.return_value = {"doc1": "nova docs"}

        mock_converse.return_value = {
            "output": {
                "message": {
                    "content": [{
                        "toolUse": {
                            "input": {
                                "thinking": "analysis",
                                "nova_draft": "draft",
                                "reflection": "reflection",
                                "nova_final": "final prompt"
                            }
                        }
                    }]
                }
            }
        }

        # Test
        result = transform_prompt("Test prompt", boto_client=custom_client)

        # Verify client was NOT closed (since it was provided)
        custom_client.close.assert_not_called()
        assert result["nova_final"] == "final prompt"

    @patch('nova_meta_prompter.transform._bedrock_converse')
    @patch('nova_meta_prompter.transform._load_text_files')
    @patch('nova_meta_prompter.transform._load_text_file')
    @patch('nova_meta_prompter.transform._get_bedrock_client')
    def test_transform_prompt_custom_model(self, mock_get_client, mock_load_file, mock_load_files, mock_converse):
        """Test transform_prompt with custom model_id"""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_load_file.return_value = "template {nova_docs} {migration_guidelines} {current_prompt}"
        mock_load_files.return_value = {"doc1": "nova docs"}

        mock_converse.return_value = {
            "output": {
                "message": {
                    "content": [{
                        "toolUse": {
                            "input": {
                                "thinking": "analysis",
                                "nova_draft": "draft",
                                "reflection": "reflection",
                                "nova_final": "final prompt"
                            }
                        }
                    }]
                }
            }
        }

        # Test with custom model
        custom_model = "custom-model-id"
        transform_prompt("Test prompt", model_id=custom_model)

        # Verify custom model was used
        call_args = mock_converse.call_args
        assert call_args[0][4] == custom_model  # model_id is 5th positional arg
