import pytest

from mm_print.output import error_exit, print_json, print_plain, print_table, print_toml


class TestErrorExit:
    """Tests for error_exit() function."""

    def test_error_exit_default_code(self, capsys):
        """Test error_exit with default exit code."""
        with pytest.raises(SystemExit) as exc_info:
            error_exit("Test error message")

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert captured.err == "Test error message\n"
        assert captured.out == ""

    def test_error_exit_custom_code(self, capsys):
        """Test error_exit with custom exit code."""
        with pytest.raises(SystemExit) as exc_info:
            error_exit("Custom error", code=42)

        assert exc_info.value.code == 42
        captured = capsys.readouterr()
        assert captured.err == "Custom error\n"


class TestPrintPlain:
    """Tests for print_plain() function."""

    def test_print_plain_basic(self, capsys):
        """Test basic print_plain functionality."""
        print_plain("Hello, world!")
        captured = capsys.readouterr()
        assert captured.out == "Hello, world!\n"
        assert captured.err == ""

        # Test with different types
        print_plain(42)
        captured = capsys.readouterr()
        assert captured.out == "42\n"

        # Test with None
        print_plain(None)
        captured = capsys.readouterr()
        assert captured.out == "None\n"

    def test_print_plain_multiple_args(self, capsys):
        """Test print_plain with multiple arguments."""
        print_plain("Hello", "world", 42)
        captured = capsys.readouterr()
        assert captured.out == "Hello world 42\n"
        assert captured.err == ""


class TestPrintJson:
    """Tests for print_json() function."""

    def test_print_json_basic(self, capsys):
        """Test basic JSON printing with real output."""
        test_data = {"key": "value", "number": 42}
        print_json(test_data)

        captured = capsys.readouterr()
        output = captured.out

        # Check that JSON elements are in output
        assert "key" in output
        assert "value" in output
        assert "42" in output
        assert captured.err == ""

    def test_print_json_with_serializer(self, capsys):
        """Test JSON printing with custom serializer."""

        class CustomObject:
            def __str__(self):
                return "custom_string"

        def custom_serializer(obj):
            return f"serialized: {obj}"

        test_data = {"obj": CustomObject()}
        print_json(test_data, type_handlers={CustomObject: custom_serializer})

        captured = capsys.readouterr()
        output = captured.out

        # Check that serialized data appears in output
        assert "obj" in output
        assert "serialized:" in output


class TestPrintTable:
    """Tests for print_table() function."""

    def test_print_table_creation(self, capsys):
        """Test table creation and printing with real output."""
        title = "Test Table"
        columns = ["Name", "Age", "City"]
        rows = [
            ["Alice", 30, "New York"],
            ["Bob", 25, "London"],
        ]

        print_table(columns, rows, title=title)

        captured = capsys.readouterr()
        output = captured.out

        # Check that table elements are in output
        assert title in output
        assert "Name" in output
        assert "Age" in output
        assert "City" in output
        assert "Alice" in output
        assert "30" in output
        assert "New York" in output
        assert "Bob" in output
        assert "25" in output
        assert "London" in output
        assert captured.err == ""

    def test_print_table_without_title(self, capsys):
        """Test table creation without title."""
        columns = ["Name", "Age"]
        rows = [["Alice", 30]]

        print_table(columns, rows)

        captured = capsys.readouterr()
        output = captured.out

        # Check that table elements are in output
        assert "Name" in output
        assert "Age" in output
        assert "Alice" in output
        assert "30" in output
        assert captured.err == ""


class TestPrintToml:
    """Tests for print_toml() function."""

    def test_toml_string_input(self, capsys):
        """Test TOML printing with string input."""
        toml_data = '[section]\nkey = "value"'
        print_toml(toml_data)

        captured = capsys.readouterr()
        output = captured.out

        # Check that TOML content appears in output
        assert "section" in output
        assert "key" in output
        assert "value" in output
        assert captured.err == ""

    def test_toml_data_input(self, capsys):
        """Test TOML printing with data input."""
        data = {"database": {"server": "192.168.1.1", "port": 5432}}
        print_toml(data)

        captured = capsys.readouterr()
        output = captured.out

        # Check that TOML content appears in output
        assert "database" in output
        assert "server" in output
        assert "192.168.1.1" in output
        assert captured.err == ""

    def test_toml_with_options(self, capsys):
        """Test TOML printing with line numbers and custom theme."""
        toml_data = '[database]\nserver = "192.168.1.1"'
        print_toml(toml_data, line_numbers=True, theme="github")

        captured = capsys.readouterr()
        output = captured.out

        # Check that TOML content appears in output
        assert "database" in output
        assert "server" in output
        assert "192.168.1.1" in output
        assert captured.err == ""
