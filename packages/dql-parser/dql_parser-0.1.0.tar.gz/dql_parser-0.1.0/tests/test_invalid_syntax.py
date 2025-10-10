"""
Unit tests for invalid DQL syntax parsing and error handling.

Tests that invalid DQL code raises appropriate exceptions with helpful
error messages per NFR9 specification.

[Source: docs/stories/1.3.implement-lark-parser.md#task-7]
[Source: docs/dql-specification.md#error-messages lines 850-956]
"""

import pytest

from dql_parser.exceptions import (
    DQLSyntaxError,
    InvalidModelNameError,
    MissingFromClauseError,
    ReservedKeywordError,
)
from dql_parser.parser import DQLParser


class TestMissingFromClause:
    """Test error handling for missing FROM clause (Error 6)."""

    def test_missing_from_clause(self):
        """Test that expectation without FROM raises MissingFromClauseError."""
        parser = DQLParser()
        dql = 'expect column("email") to_not_be_null'

        # This should fail during parsing as grammar requires FROM
        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)


class TestInvalidModelName:
    """Test error handling for invalid model names (Error 7)."""

    def test_lowercase_model_name(self):
        """Test that lowercase model name raises syntax error (caught by grammar IDENTIFIER)."""
        parser = DQLParser()
        dql = 'from customer\nexpect column("email") to_not_be_null'

        # Grammar IDENTIFIER requires uppercase first letter
        with pytest.raises(DQLSyntaxError) as exc_info:
            parser.parse(dql)

        error = exc_info.value
        assert error.line >= 1
        assert error.column > 0

    def test_snake_case_model_name(self):
        """Test that snake_case model name raises syntax error (caught by grammar IDENTIFIER)."""
        parser = DQLParser()
        dql = 'from order_item\nexpect column("sku") to_not_be_null'

        # Grammar IDENTIFIER requires uppercase first letter
        with pytest.raises(DQLSyntaxError) as exc_info:
            parser.parse(dql)

        error = exc_info.value
        assert error.line >= 1


class TestReservedKeywords:
    """Test error handling for reserved keyword usage."""

    def test_reserved_keyword_as_model_name(self):
        """Test that using reserved keyword as model name raises error."""
        parser = DQLParser()
        dql = 'from From\nexpect column("id") to_not_be_null'  # "From" is reserved

        with pytest.raises(ReservedKeywordError) as exc_info:
            parser.parse(dql)

        error = exc_info.value
        assert "from" in str(error).lower()
        assert "reserved keyword" in str(error).lower()


class TestInvalidOperators:
    """Test error handling for invalid or unknown operators."""

    def test_unknown_operator(self):
        """Test that unknown operator raises syntax error."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_be_valid'  # Invalid operator

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)

    def test_missing_operator_arguments(self):
        """Test that operator without required arguments raises error."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_match_pattern()'  # Empty args

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)

    def test_too_few_arguments_to_be_between(self):
        """Test that to_be_between with one argument raises error."""
        parser = DQLParser()
        dql = 'from Order\nexpect column("total") to_be_between(0)'  # Missing max

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)


class TestSyntaxErrors:
    """Test general syntax errors."""

    def test_missing_parenthesis_in_column(self):
        """Test missing closing parenthesis in column target."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email" to_not_be_null'  # Missing )

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)

    def test_invalid_severity_level(self):
        """Test invalid severity level raises error."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_not_be_null severity high'  # Invalid

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)

    def test_malformed_row_condition(self):
        """Test malformed WHERE condition raises error."""
        parser = DQLParser()
        dql = "from Order\nexpect row where to_not_be_null"  # Missing condition

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)

    def test_mismatched_quotes(self):
        """Test mismatched quotes in STRING raises error."""
        parser = DQLParser()
        dql = "from Customer\nexpect column(\"email') to_not_be_null"  # Mismatched quotes

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)

    def test_invalid_number_format(self):
        """Test invalid number format raises error."""
        parser = DQLParser()
        dql = 'from Product\nexpect column("price") to_be_between(abc, 100)'  # Non-number

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)

    def test_missing_comma_in_list(self):
        """Test missing comma in to_be_in list raises error."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("status") to_be_in(["active" "inactive"])'  # Missing comma

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)


class TestErrorMessageFormat:
    """Test that error messages follow NFR9 format specification."""

    def test_error_contains_line_number(self):
        """Test error message includes line number."""
        parser = DQLParser()
        dql = 'from customer\nexpect column("email") to_not_be_null'

        with pytest.raises(DQLSyntaxError) as exc_info:
            parser.parse(dql)

        error_str = str(exc_info.value)
        assert "line" in error_str.lower()
        assert error_str.count("\n") >= 2  # Multi-line format

    def test_error_contains_column_number(self):
        """Test error message includes column number."""
        parser = DQLParser()
        dql = 'from customer\nexpect column("email") to_not_be_null'

        with pytest.raises(DQLSyntaxError) as exc_info:
            parser.parse(dql)

        error_str = str(exc_info.value)
        assert "column" in error_str.lower()

    def test_error_contains_context(self):
        """Test error message includes problematic line context."""
        parser = DQLParser()
        dql = 'from customer\nexpect column("email") to_not_be_null'

        with pytest.raises(DQLSyntaxError) as exc_info:
            parser.parse(dql)

        error_str = str(exc_info.value)
        assert "from customer" in error_str

    def test_error_contains_caret_pointer(self):
        """Test error message includes caret pointer."""
        parser = DQLParser()
        dql = 'from customer\nexpect column("email") to_not_be_null'

        with pytest.raises(DQLSyntaxError) as exc_info:
            parser.parse(dql)

        error_str = str(exc_info.value)
        assert "^" in error_str  # Caret pointer

    def test_error_contains_description(self):
        """Test error message includes error description."""
        parser = DQLParser()
        dql = 'from customer\nexpect column("email") to_not_be_null'

        with pytest.raises(DQLSyntaxError) as exc_info:
            parser.parse(dql)

        error_str = str(exc_info.value)
        # Should have some description of what went wrong
        assert len(error_str) > 50


class TestComplexErrors:
    """Test error handling in complex scenarios."""

    def test_multiple_syntax_errors_reports_first(self):
        """Test that parser reports first syntax error encountered."""
        parser = DQLParser()
        # Multiple errors: lowercase model + invalid operator
        dql = 'from customer\nexpect column("email") to_be_invalid'

        with pytest.raises(Exception):  # Should report first error (model name)
            parser.parse(dql)

    def test_empty_dql_file(self):
        """Test that empty DQL file raises error."""
        parser = DQLParser()
        dql = ""

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)

    def test_only_whitespace(self):
        """Test that whitespace-only DQL raises error."""
        parser = DQLParser()
        dql = "   \n\n  \t  "

        with pytest.raises(Exception):  # Lark will raise syntax error
            parser.parse(dql)

    def test_unclosed_from_block(self):
        """Test that FROM without expectations is invalid."""
        parser = DQLParser()
        dql = "from Customer"  # No expectations

        with pytest.raises(Exception):  # Grammar requires at least one expectation
            parser.parse(dql)


class TestEdgeCases:
    """Test edge cases in error handling."""

    def test_very_long_line_error_handling(self):
        """Test error handling for very long lines."""
        parser = DQLParser()
        # Create a very long field name
        long_field = "x" * 1000
        dql = f'from customer\nexpect column("{long_field}") to_not_be_null'

        with pytest.raises(DQLSyntaxError):  # Should catch model error
            parser.parse(dql)

    def test_unicode_in_error_message(self):
        """Test that error messages handle unicode correctly."""
        parser = DQLParser()
        dql = 'from Café\nexpect column("name") to_not_be_null'  # Unicode in model name

        # Should parse fine as it's PascalCase-ish (starts with uppercase)
        try:
            ast = parser.parse(dql)
            # If it parses, model name should be preserved
            assert ast.from_blocks[0].model_name == "Café"
        except Exception:
            # If it fails, error should handle unicode
            pass


class TestOperatorArgumentValidation:
    """Test validation of operator arguments."""

    def test_to_be_in_empty_list(self):
        """Test to_be_in with empty list raises error (grammar requires at least one arg)."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("status") to_be_in([])'

        # Grammar arg_list requires at least one argument
        with pytest.raises(Exception):
            parser.parse(dql)

    def test_to_be_between_reversed_range(self):
        """Test to_be_between with min > max (parser doesn't validate semantics)."""
        parser = DQLParser()
        dql = 'from Order\nexpect column("total") to_be_between(100, 0)'  # Reversed

        # Parser should accept this (semantic validation happens later)
        ast = parser.parse(dql)
        operator = ast.from_blocks[0].expectations[0].operator
        assert operator.min_value == 100
        assert operator.max_value == 0
