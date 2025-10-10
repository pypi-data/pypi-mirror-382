# Copyright (c) Saga Inc.
# Distributed under the terms of the GNU Affero General Public License v3.0 License.

from typing import List
from anthropic.types import MessageParam
import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from mito_ai.streamlit_conversion.streamlit_agent_handler import (
    get_response_from_agent,
    generate_new_streamlit_code,
    correct_error_in_generation,
    streamlit_handler
)
from mito_ai.streamlit_conversion.streamlit_utils import clean_directory_check

# Add this line to enable async support
pytest_plugins = ('pytest_asyncio',)


class TestGetResponseFromAgent:
    """Test cases for get_response_from_agent function"""

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.agent_utils.stream_anthropic_completion_from_mito_server')
    async def test_get_response_from_agent_success(self, mock_stream):
        """Test get_response_from_agent with successful response"""
        # Mock the async generator
        async def mock_async_gen():
            yield "Here's your code:\n```python\nimport streamlit\nst.title('Test')\n```"

        mock_stream.return_value = mock_async_gen()
        
        messages: List[MessageParam] = [{"role": "user", "content": [{"type": "text", "text": "test"}]}]
        response = await get_response_from_agent(messages)
        
        assert response is not None
        assert len(response) > 0
        assert "import streamlit" in response

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.agent_utils.stream_anthropic_completion_from_mito_server')
    @pytest.mark.parametrize("mock_items,expected_result", [
        (["Hello", " World", "!"], "Hello World!"),
        ([], ""),
        (["Here's your code: import streamlit"], "Here's your code: import streamlit")
    ])
    async def test_get_response_from_agent_parametrized(self, mock_stream, mock_items, expected_result):
        """Test response from agent with different scenarios"""
        # Mock the async generator
        async def mock_async_gen():
            for item in mock_items:
                yield item

        mock_stream.return_value = mock_async_gen()
        
        messages: List[MessageParam] = [{"role": "user", "content": [{"type": "text", "text": "test"}]}]
        result = await get_response_from_agent(messages)
        
        assert result == expected_result
        mock_stream.assert_called_once()
        

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.agent_utils.stream_anthropic_completion_from_mito_server')
    async def test_get_response_from_agent_exception(self, mock_stream):
        """Test exception handling in get_response_from_agent"""
        mock_stream.side_effect = Exception("API Error")
        
        messages: List[MessageParam] = [{"role": "user", "content": [{"type": "text", "text": "test"}]}]
        
        with pytest.raises(Exception, match="API Error"):
            await get_response_from_agent(messages)


class TestGenerateStreamlitCode:
    """Test cases for generate_new_streamlit_code function"""

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.agent_utils.stream_anthropic_completion_from_mito_server')
    async def test_generate_new_streamlit_code_success(self, mock_stream):
        """Test successful streamlit code generation"""
        mock_response = "Here's your code:\n```python\nimport streamlit\nst.title('Hello')\n```"

        async def mock_async_gen():
            for item in [mock_response]:
                yield item

        mock_stream.return_value = mock_async_gen()
        
        notebook_data: List[dict] = [{"cells": []}]
        result = await generate_new_streamlit_code(notebook_data)
        
        expected_code = "import streamlit\nst.title('Hello')\n"
        assert result == expected_code


class TestCorrectErrorInGeneration:
    """Test cases for correct_error_in_generation function"""

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.agent_utils.stream_anthropic_completion_from_mito_server')
    async def test_correct_error_in_generation_success(self, mock_stream):
        """Test successful error correction"""
        mock_response = """```unified_diff
--- a/app.py
+++ b/app.py
@@ -1,1 +1,1 @@
-import streamlit
-st.title('Test')
+import streamlit
+st.title('Fixed')
```"""
        async def mock_async_gen():
            for item in [mock_response]:
                yield item

        mock_stream.return_value = mock_async_gen()

        result = await correct_error_in_generation("ImportError: No module named 'pandas'", "import streamlit\nst.title('Test')")

        expected_code = "import streamlit\nst.title('Fixed')\n"
        assert result == expected_code

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.agent_utils.stream_anthropic_completion_from_mito_server')
    async def test_correct_error_in_generation_exception(self, mock_stream):
        """Test exception handling in error correction"""
        mock_stream.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            await correct_error_in_generation("Some error", "import streamlit\nst.title('Test')")


class TestStreamlitHandler:
    """Test cases for streamlit_handler function"""

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.parse_jupyter_notebook_to_extract_required_content')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.generate_new_streamlit_code')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.validate_app')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.create_app_file')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.clean_directory_check')
    async def test_streamlit_handler_success(self, mock_clean_directory, mock_create_file, mock_validator, mock_generate_code, mock_parse):
        """Test successful streamlit handler execution"""
        # Mock notebook parsing
        mock_notebook_data: List[dict] = [{"cells": [{"cell_type": "code", "source": ["import pandas"]}]}]
        mock_parse.return_value = mock_notebook_data
        
        # Mock code generation
        mock_generate_code.return_value = "import streamlit\nst.title('Test')"
        
        # Mock validation (no errors)
        mock_validator.return_value = (False, "")
        
        # Mock file creation
        mock_create_file.return_value = (True, "/path/to/app.py", "File created successfully")
        
        # Mock clean directory check (no-op)
        mock_clean_directory.return_value = None
        
        # Use a relative path that will work cross-platform
        notebook_path = "notebook.ipynb"
        result = await streamlit_handler(notebook_path)
        
        assert result[0] is True
        assert "File created successfully" in result[2]
        
        # Verify calls
        mock_parse.assert_called_once_with(notebook_path)
        mock_generate_code.assert_called_once_with(mock_notebook_data)
        mock_validator.assert_called_once_with("import streamlit\nst.title('Test')", notebook_path)
        # get_app_directory converts relative paths to absolute, so expect the absolute path directory
        expected_app_dir = os.path.dirname(os.path.abspath(notebook_path))
        mock_create_file.assert_called_once_with(expected_app_dir, "import streamlit\nst.title('Test')")

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.parse_jupyter_notebook_to_extract_required_content')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.generate_new_streamlit_code')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.correct_error_in_generation')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.validate_app')
    async def test_streamlit_handler_max_retries_exceeded(self, mock_validator, mock_correct_error, mock_generate_code, mock_parse):
        """Test streamlit handler when max retries are exceeded"""
        # Mock notebook parsing
        mock_notebook_data: List[dict] = [{"cells": []}]
        mock_parse.return_value = mock_notebook_data
    
        # Mock code generation
        mock_generate_code.return_value = "import streamlit\nst.title('Test')"
        mock_correct_error.return_value = "import streamlit\nst.title('Fixed')"
    
        # Mock validation (always errors) - Return list of errors as expected by validate_app
        mock_validator.return_value = (True, ["Persistent error"])
    
        result = await streamlit_handler("notebook.ipynb")
        
        # Verify the result indicates failure
        assert result[0] is False
        assert "Error generating streamlit code by agent" in result[2]
        
        # Verify that error correction was called 5 times (max retries)
        assert mock_correct_error.call_count == 5

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.parse_jupyter_notebook_to_extract_required_content')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.generate_new_streamlit_code')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.validate_app')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.create_app_file')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.clean_directory_check')
    async def test_streamlit_handler_file_creation_failure(self, mock_clean_directory, mock_create_file, mock_validator, mock_generate_code, mock_parse):
        """Test streamlit handler when file creation fails"""
        # Mock notebook parsing
        mock_notebook_data: List[dict] = [{"cells": []}]
        mock_parse.return_value = mock_notebook_data
        
        # Mock code generation
        mock_generate_code.return_value = "import streamlit\nst.title('Test')"
        
        # Mock validation (no errors)
        mock_validator.return_value = (False, "")
        
        # Mock file creation failure
        mock_create_file.return_value = (False, None, "Permission denied")
        
        # Mock clean directory check (no-op)
        mock_clean_directory.return_value = None
        
        result = await streamlit_handler("notebook.ipynb")
        
        assert result[0] is False
        assert "Permission denied" in result[2]

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.parse_jupyter_notebook_to_extract_required_content')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.clean_directory_check')
    async def test_streamlit_handler_parse_notebook_exception(self, mock_clean_directory, mock_parse):
        """Test streamlit handler when notebook parsing fails"""
        # Mock clean directory check (no-op)
        mock_clean_directory.return_value = None
        
        mock_parse.side_effect = FileNotFoundError("Notebook not found")
        
        with pytest.raises(FileNotFoundError, match="Notebook not found"):
            await streamlit_handler("notebook.ipynb")

    @pytest.mark.asyncio
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.parse_jupyter_notebook_to_extract_required_content')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.generate_new_streamlit_code')
    @patch('mito_ai.streamlit_conversion.streamlit_agent_handler.clean_directory_check')
    async def test_streamlit_handler_generation_exception(self, mock_clean_directory, mock_generate_code, mock_parse):
        """Test streamlit handler when code generation fails"""
        # Mock notebook parsing
        mock_notebook_data: List[dict] = [{"cells": []}]
        mock_parse.return_value = mock_notebook_data
        
        # Mock code generation failure
        mock_generate_code.side_effect = Exception("Generation failed")
        
        # Mock clean directory check (no-op)
        mock_clean_directory.return_value = None
        
        with pytest.raises(Exception, match="Generation failed"):
            await streamlit_handler("notebook.ipynb")



