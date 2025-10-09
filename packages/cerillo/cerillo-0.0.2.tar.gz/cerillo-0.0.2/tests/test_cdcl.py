from cerillo import CDCLParser, CDCLParseError
import pytest


class TestCDCLParser:
    """Test suite for CDCL parses/producers"""

    def test_parse_basic_response_without_cmd_id(self):
        """Test parsing a basic response without command ID"""
        message = ":12345 R params"
        response = CDCLParser.parse_response(message)

        assert response.serial_number == "12345"
        assert response.command_id is None
        assert response.prefix == "R"
        assert response.params == ["params"]
        assert response.raw_message == message

    def test_parse_basic_response_without_cmd_id(self):
        """Test parsing a basic response without command ID"""
        message = ":12345 xR params"
        response = CDCLParser.parse_response(message)

        assert response.serial_number == "12345"
        assert response.command_id is None
        assert response.prefix == "x"
        assert response.params == ["R", "params"]
        assert response.raw_message == message

    def test_parse_response_with_cmd_id(self):
        """Test parsing a response with command ID"""
        message = ":12345*aB3d R multiple params"
        response = CDCLParser.parse_response(message)

        assert response.serial_number == "12345"
        assert response.command_id == "aB3d"
        assert response.prefix == "R"
        assert response.params == ["multiple", "params"]

    def test_parse_response_multiple_params(self):
        """Test parsing a response with multiple numeric parameters"""
        message = ":98765 v 450 490 590 600"
        response = CDCLParser.parse_response(message)

        assert response.serial_number == "98765"
        assert response.command_id is None
        assert response.prefix == "v"
        assert len(response.params) == 4
        assert response.params[0] == "450"
        assert response.params[1] == "490"
        assert response.params[2] == "590"
        assert response.params[3] == "600"

    def test_parse_error_missing_colon(self):
        """Test that missing colon raises error"""
        message = "12345 xR"

        with pytest.raises(CDCLParseError, match="must start with ':'"):
            CDCLParser.parse_response(message)

    def test_parse_error_empty_message(self):
        """Test that empty message raises error"""
        with pytest.raises(CDCLParseError, match="Empty message"):
            CDCLParser.parse_response("")

    def test_is_cdcl_message_valid(self):
        """Test CDCL message detection"""
        assert CDCLParser.is_cdcl_response(":12345 xR 0x00000") is True
        assert CDCLParser.is_cdcl_response("  :12345 xR 0x000000  ") is True

    def test_is_cdcl_message_invalid(self):
        """Test CDCL message detection with invalid messages"""
        assert CDCLParser.is_cdcl_response("12345 xR 0x000000") is False
        assert CDCLParser.is_cdcl_response("") is False
        assert CDCLParser.is_cdcl_response(None) is False

    def test_parse_param_as_int(self):
        """Test integer parameter parsing"""
        assert CDCLParser.parse_param_as_int("123") == 123
        assert CDCLParser.parse_param_as_int("0") == 0
        assert CDCLParser.parse_param_as_int("-456") == -456

    def test_parse_param_as_int_error(self):
        """Test integer parameter parsing error"""
        with pytest.raises(CDCLParseError, match="Cannot parse"):
            CDCLParser.parse_param_as_int("not_a_number")

    def test_parse_param_as_float(self):
        """Test float parameter parsing"""
        assert CDCLParser.parse_param_as_float("123.45") == 123.45
        assert CDCLParser.parse_param_as_float("0.001") == 0.001
        assert CDCLParser.parse_param_as_float("-3.14") == -3.14

    def test_parse_param_as_float_error(self):
        """Test float parameter parsing error"""
        with pytest.raises(CDCLParseError, match="Cannot parse"):
            CDCLParser.parse_param_as_float("not_a_float")

    def test_cmd_id_chars(self):
        """Test that command ID accepts A-Za-z0-9 characters"""
        # Test various valid base64 characters
        valid_ids = ["aB3d", "AAAA", "zZ9+", "0123", "abc/"]

        for cmd_id in valid_ids:
            message = f":12345*{cmd_id} xR 0x000000"
            response = CDCLParser.parse_response(message)
            assert response.command_id == cmd_id

    def test_basic_command_parse(self):
        """Tests basic command"""
        command_str = "x"
        command = CDCLParser.parse_command(command_str)
        assert command.command == "x"
        assert command.command_id == None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
