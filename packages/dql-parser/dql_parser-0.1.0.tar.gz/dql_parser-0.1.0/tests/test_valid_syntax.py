"""
Unit tests for valid DQL syntax parsing.

Tests that valid DQL code parses successfully and produces correct AST nodes.
Covers all 6 core operators, column/row targets, severity levels, and cleaners.

[Source: docs/stories/1.3.implement-lark-parser.md#task-6]
[Source: docs/dql-specification.md#examples]
"""

import pytest

from dql_parser.ast_nodes import (
    ColumnTarget,
    Comparison,
    DQLFile,
    ExpectationNode,
    FromBlock,
    RowTarget,
    ToBeIn,
    ToBeBetween,
    ToBeNull,
    ToBeUnique,
    ToMatchPattern,
    ToNotBeNull,
    Value,
    ColumnRef,
    FunctionCall,
    ArithmeticExpr,
    LogicalExpr,
)
from dql_parser.parser import DQLParser


class TestBasicParsing:
    """Test basic DQL parsing functionality."""

    def test_parse_empty_from_block_fails(self):
        """FROM block must have at least one expectation."""
        parser = DQLParser()
        with pytest.raises(Exception):  # Lark will raise on incomplete grammar
            parser.parse("from Customer")

    def test_parse_simple_column_expectation(self):
        """Test parsing a simple column-level expectation."""
        parser = DQLParser()
        dql = """
        from Customer
        expect column("email") to_not_be_null
        """
        ast = parser.parse(dql)

        assert isinstance(ast, DQLFile)
        assert len(ast.from_blocks) == 1

        block = ast.from_blocks[0]
        assert isinstance(block, FromBlock)
        assert block.model_name == "Customer"
        assert len(block.expectations) == 1

        exp = block.expectations[0]
        assert isinstance(exp, ExpectationNode)
        assert isinstance(exp.target, ColumnTarget)
        assert exp.target.field_name == "email"
        assert isinstance(exp.operator, ToNotBeNull)
        assert exp.severity is None

    def test_parse_multiple_expectations(self):
        """Test parsing multiple expectations in a single FROM block."""
        parser = DQLParser()
        dql = """
        from Customer
        expect column("email") to_not_be_null
        expect column("age") to_be_between(0, 150)
        expect column("status") to_be_in(["active", "inactive"])
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert len(ast.from_blocks[0].expectations) == 3

    def test_parse_multiple_from_blocks(self):
        """Test parsing multiple FROM blocks in a single file."""
        parser = DQLParser()
        dql = """
        from Customer
        expect column("email") to_not_be_null

        from Order
        expect column("total") to_be_between(0, 10000)

        from Product
        expect column("sku") to_be_unique
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 3
        assert ast.from_blocks[0].model_name == "Customer"
        assert ast.from_blocks[1].model_name == "Order"
        assert ast.from_blocks[2].model_name == "Product"


class TestOperators:
    """Test parsing of all 6 core operators."""

    def test_parse_to_be_null(self):
        """Test to_be_null operator (no arguments)."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("middle_name") to_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.operator, ToBeNull)

    def test_parse_to_not_be_null(self):
        """Test to_not_be_null operator (no arguments)."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.operator, ToNotBeNull)

    def test_parse_to_match_pattern(self):
        """Test to_match_pattern operator (1 string argument)."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_match_pattern("^[a-zA-Z0-9]+@")'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.operator, ToMatchPattern)
        assert exp.operator.pattern == "^[a-zA-Z0-9]+@"

    def test_parse_to_be_between(self):
        """Test to_be_between operator (2 numeric arguments)."""
        parser = DQLParser()
        dql = 'from Order\nexpect column("total") to_be_between(0, 10000)'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.operator, ToBeBetween)
        assert exp.operator.min_value == 0
        assert exp.operator.max_value == 10000

    def test_parse_to_be_between_floats(self):
        """Test to_be_between with float values."""
        parser = DQLParser()
        dql = 'from Product\nexpect column("rating") to_be_between(0.0, 5.0)'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.operator, ToBeBetween)
        assert exp.operator.min_value == 0.0
        assert exp.operator.max_value == 5.0

    def test_parse_to_be_in(self):
        """Test to_be_in operator (list argument)."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("status") to_be_in(["active", "inactive", "pending"])'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.operator, ToBeIn)
        assert exp.operator.values == ["active", "inactive", "pending"]

    def test_parse_to_be_in_numbers(self):
        """Test to_be_in with numeric values."""
        parser = DQLParser()
        dql = 'from Product\nexpect column("category_id") to_be_in([1, 2, 3, 5, 8])'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.operator, ToBeIn)
        assert exp.operator.values == [1, 2, 3, 5, 8]

    def test_parse_to_be_unique(self):
        """Test to_be_unique operator (no arguments)."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_be_unique'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.operator, ToBeUnique)


class TestSeverityLevels:
    """Test parsing of severity levels."""

    def test_parse_severity_critical(self):
        """Test critical severity level."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_not_be_null severity critical'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert exp.severity == "critical"

    def test_parse_severity_warning(self):
        """Test warning severity level."""
        parser = DQLParser()
        dql = (
            'from Customer\nexpect column("phone") to_match_pattern("^[0-9]{10}$") severity warning'
        )
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert exp.severity == "warning"

    def test_parse_severity_info(self):
        """Test info severity level."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("notes") to_not_be_null severity info'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert exp.severity == "info"

    def test_parse_no_severity(self):
        """Test expectation without severity (default behavior)."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert exp.severity is None


class TestRowLevelExpectations:
    """Test parsing of row-level expectations with WHERE conditions."""

    def test_parse_row_target_simple_comparison(self):
        """Test row-level expectation with simple comparison."""
        parser = DQLParser()
        dql = 'from Order\nexpect row where column("total") > 0 to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.target, RowTarget)
        assert isinstance(exp.target.condition, Comparison)
        assert exp.target.condition.operator == ">"
        assert isinstance(exp.target.condition.left, ColumnRef)
        assert exp.target.condition.left.field_name == "total"
        assert isinstance(exp.target.condition.right, Value)
        assert exp.target.condition.right.value == 0

    def test_parse_row_target_logical_and(self):
        """Test row-level expectation with AND condition."""
        parser = DQLParser()
        dql = 'from Customer\nexpect row where column("age") >= 18 and column("status") == "active" to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.target, RowTarget)
        assert isinstance(exp.target.condition, LogicalExpr)
        assert exp.target.condition.operator == "AND"
        assert len(exp.target.condition.operands) == 2

    def test_parse_row_target_logical_or(self):
        """Test row-level expectation with OR condition."""
        parser = DQLParser()
        dql = 'from Product\nexpect row where column("in_stock") == 1 or column("backorder") == 1 to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.target, RowTarget)
        assert isinstance(exp.target.condition, LogicalExpr)
        assert exp.target.condition.operator == "OR"

    def test_parse_row_target_logical_not(self):
        """Test row-level expectation with NOT condition."""
        parser = DQLParser()
        dql = 'from Customer\nexpect row where not column("deleted") == 1 to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert isinstance(exp.target, RowTarget)
        assert isinstance(exp.target.condition, LogicalExpr)
        assert exp.target.condition.operator == "NOT"


class TestFunctionsAndExpressions:
    """Test parsing of functions and arithmetic expressions."""

    def test_parse_concat_function(self):
        """Test CONCAT function in row condition."""
        parser = DQLParser()
        dql = 'from Customer\nexpect row where CONCAT(column("first_name"), " ", column("last_name")) == "John Doe" to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        condition = exp.target.condition
        assert isinstance(condition, Comparison)
        assert isinstance(condition.left, FunctionCall)
        assert condition.left.function_name == "CONCAT"
        assert len(condition.left.args) == 3  # first_name, " ", last_name

    def test_parse_arithmetic_addition(self):
        """Test arithmetic expression with addition."""
        parser = DQLParser()
        dql = 'from Order\nexpect row where column("subtotal") + column("tax") == column("total") to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        condition = exp.target.condition
        assert isinstance(condition, Comparison)
        assert isinstance(condition.left, ArithmeticExpr)
        assert condition.left.operator == "+"

    def test_parse_arithmetic_multiplication(self):
        """Test arithmetic expression with multiplication."""
        parser = DQLParser()
        dql = 'from OrderItem\nexpect row where column("quantity") * column("unit_price") == column("line_total") to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        condition = exp.target.condition
        assert isinstance(condition, Comparison)
        assert isinstance(condition.left, ArithmeticExpr)
        assert condition.left.operator == "*"


class TestCleaners:
    """Test parsing of cleaner syntax (Epic 3 preparation)."""

    def test_parse_cleaner_no_args(self):
        """Test cleaner with no arguments."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_not_be_null severity critical on_failure clean_with("send_alert")'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert len(exp.cleaners) == 1
        assert exp.cleaners[0].cleaner_name == "send_alert"
        assert exp.cleaners[0].args == []

    def test_parse_cleaner_with_args(self):
        """Test cleaner with arguments."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_not_be_null on_failure clean_with("set_default", "noemail@example.com")'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert len(exp.cleaners) == 1
        assert exp.cleaners[0].cleaner_name == "set_default"
        assert exp.cleaners[0].args == ["noemail@example.com"]

    def test_parse_multiple_cleaners(self):
        """Test chaining multiple cleaners."""
        parser = DQLParser()
        dql = """from Customer
expect column("email") to_not_be_null
    on_failure clean_with("log_error", "email_missing")
    on_failure clean_with("send_alert")"""
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert len(exp.cleaners) == 2
        assert exp.cleaners[0].cleaner_name == "log_error"
        assert exp.cleaners[1].cleaner_name == "send_alert"


class TestStringAndNumberFormats:
    """Test parsing of different string and number formats."""

    def test_parse_single_quoted_string(self):
        """Test string with single quotes."""
        parser = DQLParser()
        dql = "from Customer\nexpect column('email') to_not_be_null"
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert exp.target.field_name == "email"

    def test_parse_double_quoted_string(self):
        """Test string with double quotes."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_not_be_null'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert exp.target.field_name == "email"

    def test_parse_negative_number(self):
        """Test negative numbers in to_be_between."""
        parser = DQLParser()
        dql = 'from Temperature\nexpect column("celsius") to_be_between(-50, 50)'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert exp.operator.min_value == -50
        assert exp.operator.max_value == 50

    def test_parse_float_number(self):
        """Test float numbers."""
        parser = DQLParser()
        dql = 'from Product\nexpect column("price") to_be_between(0.01, 999.99)'
        ast = parser.parse(dql)

        exp = ast.from_blocks[0].expectations[0]
        assert exp.operator.min_value == 0.01
        assert exp.operator.max_value == 999.99


class TestCaseInsensitiveKeywords:
    """Test that keywords are case-insensitive."""

    def test_parse_uppercase_from(self):
        """Test FROM in uppercase."""
        parser = DQLParser()
        dql = 'FROM Customer\nexpect column("email") to_not_be_null'
        ast = parser.parse(dql)
        assert ast.from_blocks[0].model_name == "Customer"

    def test_parse_uppercase_expect(self):
        """Test EXPECT in uppercase."""
        parser = DQLParser()
        dql = 'from Customer\nEXPECT column("email") to_not_be_null'
        ast = parser.parse(dql)
        assert len(ast.from_blocks[0].expectations) == 1

    def test_parse_mixed_case_severity(self):
        """Test SEVERITY in mixed case."""
        parser = DQLParser()
        dql = 'from Customer\nexpect column("email") to_not_be_null SeVeRiTy CrItIcAl'
        ast = parser.parse(dql)
        assert ast.from_blocks[0].expectations[0].severity == "critical"


class TestComments:
    """Test that comments are ignored."""

    def test_parse_line_comment(self):
        """Test DQL with line comments."""
        parser = DQLParser()
        dql = """
        # This is a comment
        from Customer  # inline comment
        # Another comment
        expect column("email") to_not_be_null  # expect comment
        """
        ast = parser.parse(dql)
        assert len(ast.from_blocks) == 1
        assert len(ast.from_blocks[0].expectations) == 1
