import pytest
from pydantic import BaseModel, ValidationError

from kiln_ai.datamodel.tool_id import (
    MCP_LOCAL_TOOL_ID_PREFIX,
    MCP_REMOTE_TOOL_ID_PREFIX,
    RAG_TOOL_ID_PREFIX,
    KilnBuiltInToolId,
    ToolId,
    _check_tool_id,
    kiln_task_server_id_from_tool_id,
    mcp_server_and_tool_name_from_id,
    rag_config_id_from_id,
)


class TestKilnBuiltInToolId:
    """Test the KilnBuiltInToolId enum."""

    def test_enum_values(self):
        """Test that enum has expected values."""
        assert KilnBuiltInToolId.ADD_NUMBERS == "kiln_tool::add_numbers"
        assert KilnBuiltInToolId.SUBTRACT_NUMBERS == "kiln_tool::subtract_numbers"
        assert KilnBuiltInToolId.MULTIPLY_NUMBERS == "kiln_tool::multiply_numbers"
        assert KilnBuiltInToolId.DIVIDE_NUMBERS == "kiln_tool::divide_numbers"
        for enum_value in KilnBuiltInToolId.__members__.values():
            assert _check_tool_id(enum_value) == enum_value

    def test_enum_membership(self):
        """Test enum membership checks."""
        assert "kiln_tool::add_numbers" in KilnBuiltInToolId.__members__.values()
        assert "invalid_tool" not in KilnBuiltInToolId.__members__.values()


class TestCheckToolId:
    """Test the _check_tool_id validation function."""

    def test_valid_builtin_tools(self):
        """Test validation of valid built-in tools."""
        for tool_id in KilnBuiltInToolId:
            result = _check_tool_id(tool_id.value)
            assert result == tool_id.value

    def test_valid_mcp_remote_tools(self):
        """Test validation of valid MCP remote tools."""
        valid_ids = [
            "mcp::remote::server1::tool1",
            "mcp::remote::my_server::my_tool",
            "mcp::remote::test::function_name",
        ]
        for tool_id in valid_ids:
            result = _check_tool_id(tool_id)
            assert result == tool_id

    def test_valid_mcp_local_tools(self):
        """Test validation of valid MCP local tools."""
        valid_ids = [
            "mcp::local::server1::tool1",
            "mcp::local::my_server::my_tool",
            "mcp::local::test::function_name",
        ]
        for tool_id in valid_ids:
            result = _check_tool_id(tool_id)
            assert result == tool_id

    def test_invalid_empty_or_none(self):
        """Test validation fails for empty or None values."""
        with pytest.raises(ValueError, match="Invalid tool ID"):
            _check_tool_id("")

        with pytest.raises(ValueError, match="Invalid tool ID"):
            _check_tool_id(None)  # type: ignore

    def test_invalid_non_string(self):
        """Test validation fails for non-string values."""
        with pytest.raises(ValueError, match="Invalid tool ID"):
            _check_tool_id(123)  # type: ignore

        with pytest.raises(ValueError, match="Invalid tool ID"):
            _check_tool_id(["tool"])  # type: ignore

    def test_invalid_unknown_tool(self):
        """Test validation fails for unknown tool IDs."""
        with pytest.raises(ValueError, match="Invalid tool ID: unknown_tool"):
            _check_tool_id("unknown_tool")

    def test_invalid_mcp_format(self):
        """Test validation fails for invalid MCP tool formats."""
        # These IDs start with the MCP remote prefix but have invalid formats
        mcp_remote_invalid_ids = [
            "mcp::remote::",  # Missing server and tool
            "mcp::remote::server",  # Missing tool
            "mcp::remote::server::",  # Empty tool name
            "mcp::remote::::tool",  # Empty server name
            "mcp::remote::server::tool::extra",  # Too many parts
        ]

        for invalid_id in mcp_remote_invalid_ids:
            with pytest.raises(ValueError, match="Invalid remote MCP tool ID"):
                _check_tool_id(invalid_id)

        # These IDs start with the MCP local prefix but have invalid formats
        mcp_local_invalid_ids = [
            "mcp::local::",  # Missing server and tool
            "mcp::local::server",  # Missing tool
            "mcp::local::server::",  # Empty tool name
            "mcp::local::::tool",  # Empty server name
            "mcp::local::server::tool::extra",  # Too many parts
        ]

        for invalid_id in mcp_local_invalid_ids:
            with pytest.raises(ValueError, match="Invalid local MCP tool ID"):
                _check_tool_id(invalid_id)

        # This ID doesn't start with MCP prefix so gets generic error
        with pytest.raises(ValueError, match="Invalid tool ID"):
            _check_tool_id("mcp::wrong::server::tool")

    def test_valid_rag_tools(self):
        """Test validation of valid RAG tools."""
        valid_ids = [
            "kiln_tool::rag::config1",
            "kiln_tool::rag::my_rag_config",
            "kiln_tool::rag::test_config_123",
        ]
        for tool_id in valid_ids:
            result = _check_tool_id(tool_id)
            assert result == tool_id

    def test_invalid_rag_format(self):
        """Test validation fails for invalid RAG tool formats."""
        # These IDs start with the RAG prefix but have invalid formats
        rag_invalid_ids = [
            "kiln_tool::rag::",  # Missing config ID
            "kiln_tool::rag::config::extra",  # Too many parts
        ]

        for invalid_id in rag_invalid_ids:
            with pytest.raises(ValueError, match="Invalid RAG tool ID"):
                _check_tool_id(invalid_id)

    def test_rag_tool_empty_config_id(self):
        """Test that RAG tool with empty config ID is handled properly."""
        # This tests the case where rag_config_id_from_id returns empty string
        # which should trigger line 66 in the source
        with pytest.raises(ValueError, match="Invalid RAG tool ID"):
            _check_tool_id("kiln_tool::rag::")

    def test_valid_kiln_task_tools(self):
        """Test validation of valid Kiln task tools."""
        valid_ids = [
            "kiln_task::server1",
            "kiln_task::my_server",
            "kiln_task::test_server_123",
            "kiln_task::server_with_underscores",
            "kiln_task::server-with-dashes",
            "kiln_task::server.with.dots",
        ]
        for tool_id in valid_ids:
            result = _check_tool_id(tool_id)
            assert result == tool_id

    def test_invalid_kiln_task_format(self):
        """Test validation fails for invalid Kiln task tool formats."""
        # These IDs start with the Kiln task prefix but have invalid formats
        kiln_task_invalid_ids = [
            "kiln_task::",  # Missing server ID
            "kiln_task::server::extra",  # Too many parts
            "kiln_task::server::tool::extra",  # Too many parts
        ]

        for invalid_id in kiln_task_invalid_ids:
            with pytest.raises(ValueError, match="Invalid Kiln task tool ID"):
                _check_tool_id(invalid_id)

    def test_kiln_task_tool_empty_server_id(self):
        """Test that Kiln task tool with empty server ID is handled properly."""
        # This tests the case where kiln_task_server_id_from_tool_id returns empty string which should raise an error
        with pytest.raises(ValueError, match="Invalid Kiln task tool ID"):
            _check_tool_id("kiln_task::")


class TestMcpServerAndToolNameFromId:
    """Test the mcp_server_and_tool_name_from_id function."""

    def test_valid_mcp_ids(self):
        """Test parsing valid MCP tool IDs."""
        test_cases = [
            # Remote MCP tools
            ("mcp::remote::server1::tool1", ("server1", "tool1")),
            ("mcp::remote::my_server::my_tool", ("my_server", "my_tool")),
            ("mcp::remote::test::function_name", ("test", "function_name")),
            # Local MCP tools
            ("mcp::local::server1::tool1", ("server1", "tool1")),
            ("mcp::local::my_server::my_tool", ("my_server", "my_tool")),
            ("mcp::local::test::function_name", ("test", "function_name")),
        ]

        for tool_id, expected in test_cases:
            result = mcp_server_and_tool_name_from_id(tool_id)
            assert result == expected

    def test_invalid_mcp_ids(self):
        """Test parsing fails for invalid MCP tool IDs."""
        # Test remote MCP tool ID errors
        remote_invalid_ids = [
            "mcp::remote::",  # Only 3 parts
            "mcp::remote::server",  # Only 3 parts
            "mcp::remote::server::tool::extra",  # 5 parts
        ]

        for invalid_id in remote_invalid_ids:
            with pytest.raises(ValueError, match="Invalid remote MCP tool ID"):
                mcp_server_and_tool_name_from_id(invalid_id)

        # Test local MCP tool ID errors
        local_invalid_ids = [
            "mcp::local::",  # Only 3 parts
            "mcp::local::server",  # Only 3 parts
            "mcp::local::server::tool::extra",  # 5 parts
        ]

        for invalid_id in local_invalid_ids:
            with pytest.raises(ValueError, match="Invalid local MCP tool ID"):
                mcp_server_and_tool_name_from_id(invalid_id)

        # Test generic MCP tool ID errors (not remote or local)
        generic_invalid_ids = [
            "not_mcp_format",  # Only 1 part
            "single_part",  # Only 1 part
            "",  # Empty string
        ]

        for invalid_id in generic_invalid_ids:
            with pytest.raises(ValueError, match="Invalid MCP tool ID"):
                mcp_server_and_tool_name_from_id(invalid_id)

    def test_mcp_ids_with_wrong_prefix_still_parse(self):
        """Test that IDs with wrong prefix but correct structure still parse (validation happens elsewhere)."""
        # This function only checks structure (4 parts), not content
        result = mcp_server_and_tool_name_from_id("mcp::wrong::server::tool")
        assert result == ("server", "tool")


class TestToolIdPydanticType:
    """Test the ToolId pydantic type annotation."""

    class _ModelWithToolId(BaseModel):
        tool_id: ToolId

    def test_valid_builtin_tools(self):
        """Test ToolId validates built-in tools."""
        for tool_id in KilnBuiltInToolId:
            model = self._ModelWithToolId(tool_id=tool_id.value)
            assert model.tool_id == tool_id.value

    def test_valid_tool_ids(self):
        """Test ToolId validates MCP remote and local tools."""
        valid_ids = [
            # Remote MCP tools
            "mcp::remote::server1::tool1",
            "mcp::remote::my_server::my_tool",
            # Local MCP tools
            "mcp::local::server1::tool1",
            "mcp::local::my_server::my_tool",
            # RAG tools
            "kiln_tool::rag::config1",
            "kiln_tool::rag::my_rag_config",
            # Kiln task tools
            "kiln_task::server1",
            "kiln_task::my_server",
        ]

        for tool_id in valid_ids:
            model = self._ModelWithToolId(tool_id=tool_id)
            assert model.tool_id == tool_id

    def test_invalid_tools_raise_validation_error(self):
        """Test ToolId raises ValidationError for invalid tools."""
        invalid_ids = [
            "",
            "unknown_tool",
            "mcp::remote::",
            "mcp::remote::server",
            "mcp::local::",
            "mcp::local::server",
            "kiln_tool::rag::",
            "kiln_tool::rag::config::extra",
            "kiln_task::",
            "kiln_task::server::extra",
        ]

        for invalid_id in invalid_ids:
            with pytest.raises(ValidationError):
                self._ModelWithToolId(tool_id=invalid_id)

    def test_non_string_raises_validation_error(self):
        """Test ToolId raises ValidationError for non-string values."""
        with pytest.raises(ValidationError):
            self._ModelWithToolId(tool_id=123)  # type: ignore

        with pytest.raises(ValidationError):
            self._ModelWithToolId(tool_id=None)  # type: ignore


class TestConstants:
    """Test module constants."""

    def test_mcp_remote_tool_id_prefix(self):
        """Test the MCP remote tool ID prefix constant."""
        assert MCP_REMOTE_TOOL_ID_PREFIX == "mcp::remote::"

    def test_mcp_local_tool_id_prefix(self):
        """Test the MCP local tool ID prefix constant."""
        assert MCP_LOCAL_TOOL_ID_PREFIX == "mcp::local::"

    def test_rag_tool_id_prefix(self):
        """Test the RAG tool ID prefix constant."""
        assert RAG_TOOL_ID_PREFIX == "kiln_tool::rag::"


class TestRagConfigIdFromId:
    """Test the rag_config_id_from_id function."""

    def test_valid_rag_ids(self):
        """Test parsing valid RAG tool IDs."""
        test_cases = [
            ("kiln_tool::rag::config1", "config1"),
            ("kiln_tool::rag::my_rag_config", "my_rag_config"),
            ("kiln_tool::rag::test_config_123", "test_config_123"),
            ("kiln_tool::rag::a", "a"),  # Minimal valid case
        ]

        for tool_id, expected in test_cases:
            result = rag_config_id_from_id(tool_id)
            assert result == expected

    def test_invalid_rag_ids(self):
        """Test parsing fails for invalid RAG tool IDs."""
        # Test various invalid formats that should trigger line 104
        invalid_ids = [
            "kiln_tool::rag::config::extra",  # Too many parts (4 parts)
            "wrong::rag::config",  # Wrong prefix
            "kiln_tool::wrong::config",  # Wrong middle part
            "rag::config",  # Too few parts (2 parts)
            "",  # Empty string
            "single_part",  # Only 1 part
        ]

        for invalid_id in invalid_ids:
            with pytest.raises(ValueError, match="Invalid RAG tool ID"):
                rag_config_id_from_id(invalid_id)

    def test_rag_id_with_empty_config_id(self):
        """Test that RAG tool ID with empty config ID returns empty string."""
        # This is actually valid according to the parser - it returns empty string
        # The validation for empty config ID happens in _check_tool_id
        result = rag_config_id_from_id("kiln_tool::rag::")
        assert result == ""


class TestKilnTaskServerIdFromToolId:
    """Test the kiln_task_server_id_from_tool_id function."""

    def test_valid_kiln_task_ids(self):
        """Test parsing valid Kiln task tool IDs."""
        test_cases = [
            ("kiln_task::server1", "server1"),
            ("kiln_task::my_server", "my_server"),
            ("kiln_task::test_server_123", "test_server_123"),
            ("kiln_task::a", "a"),  # Minimal valid case
            ("kiln_task::server_with_underscores", "server_with_underscores"),
            ("kiln_task::server-with-dashes", "server-with-dashes"),
            ("kiln_task::server.with.dots", "server.with.dots"),
        ]

        for tool_id, expected in test_cases:
            result = kiln_task_server_id_from_tool_id(tool_id)
            assert result == expected

    def test_invalid_kiln_task_ids(self):
        """Test parsing fails for invalid Kiln task tool IDs."""
        # Test various invalid formats
        invalid_ids = [
            "kiln_task::",  # Empty server ID
            "kiln_task::server::extra",  # Too many parts (3 parts)
            "kiln_task::server::tool::extra",  # Too many parts (4 parts)
            "wrong::server",  # Wrong prefix
            "kiln_wrong::server",  # Wrong prefix
            "task::server",  # Too few parts (2 parts)
            "",  # Empty string
            "single_part",  # Only 1 part
            "kiln_task",  # Missing server ID
        ]

        for invalid_id in invalid_ids:
            with pytest.raises(ValueError, match="Invalid Kiln task tool ID format"):
                kiln_task_server_id_from_tool_id(invalid_id)

    def test_kiln_task_id_with_empty_server_id(self):
        """Test that Kiln task tool ID with empty server ID raises error."""
        with pytest.raises(ValueError, match="Invalid Kiln task tool ID format"):
            kiln_task_server_id_from_tool_id("kiln_task::")

    def test_kiln_task_id_with_whitespace_server_id(self):
        """Test that Kiln task tool ID with whitespace-only server ID raises error."""
        with pytest.raises(ValueError, match="Invalid Kiln task tool ID format"):
            kiln_task_server_id_from_tool_id("kiln_task::")

    def test_kiln_task_id_with_multiple_colons(self):
        """Test that Kiln task tool ID with multiple colons raises error."""
        with pytest.raises(ValueError, match="Invalid Kiln task tool ID format"):
            kiln_task_server_id_from_tool_id("kiln_task::server::extra")

    def test_kiln_task_id_case_sensitivity(self):
        """Test that Kiln task tool IDs are case sensitive."""
        # These should work
        result1 = kiln_task_server_id_from_tool_id("kiln_task::Server")
        assert result1 == "Server"

        result2 = kiln_task_server_id_from_tool_id("kiln_task::SERVER")
        assert result2 == "SERVER"

        result3 = kiln_task_server_id_from_tool_id("kiln_task::server")
        assert result3 == "server"
