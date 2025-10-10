"""
DQL Parser: Parses Data Quality Language into Abstract Syntax Trees.

The DQLParser class provides the main entry point for parsing DQL code.
It uses Lark for parsing with a LALR(1) parser for performance, then
transforms the parse tree into strongly-typed AST nodes.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Union

from lark import Lark, UnexpectedInput, UnexpectedToken

from .ast_nodes import DQLFile
from .exceptions import (
    DQLSyntaxError,
    InvalidModelNameError,
    MissingFromClauseError,
    ReservedKeywordError,
)
from .transformer import DQLTransformer


class DQLParser:
    """
    Parser for Data Quality Language (DQL).

    Parses DQL text into a DQLFile AST node containing all FROM blocks
    and expectations. Provides detailed error messages with line/column
    information.

    Example:
        >>> parser = DQLParser()
        >>> dql = '''
        ... from Customer
        ... expect column("email") to_not_be_null severity critical
        ... '''
        >>> ast = parser.parse(dql)
        >>> print(ast.from_blocks[0].model_name)
        Customer
    """

    # Reserved keywords from DQL specification
    RESERVED_KEYWORDS = {
        # Current MVP keywords
        "from",
        "expect",
        "column",
        "row",
        "where",
        "severity",
        "to_be_null",
        "to_not_be_null",
        "to_match_pattern",
        "to_be_between",
        "to_be_in",
        "to_be_unique",
        "on_failure",
        "clean_with",
        "critical",
        "warning",
        "info",
        "null",
        # Future reserved keywords
        "to_be_greater_than",
        "to_be_less_than",
        "to_contain",
        "to_start_with",
        "to_end_with",
        "percentile",
        "mean",
        "median",
        "stddev",
        "count",
        "sum",
        "min",
        "max",
        "avg",
        "group_by",
        "having",
        "order_by",
        "limit",
        "offset",
        "join",
        "inner",
        "left",
        "right",
        "outer",
        "on",
        "as",
        "distinct",
    }

    # PascalCase regex for model names
    PASCALCASE_REGEX = re.compile(r"^[A-Z][a-zA-Z0-9_]*$")

    def __init__(self):
        """
        Initialize DQL parser with Lark grammar.

        Loads grammar from dql_parser/grammar.lark and configures LALR(1)
        parser with position propagation for error reporting.
        """
        # Find grammar file relative to this module
        grammar_path = Path(__file__).parent / "grammar.lark"

        # Initialize Lark parser with LALR for speed
        self._lark = Lark.open(
            grammar_path,
            start="dql_file",
            parser="lalr",  # LALR(1) for performance
            propagate_positions=True,  # Enable line/column tracking
        )

        # Initialize transformer
        self._transformer = DQLTransformer()

    def parse(self, dql_text: str) -> DQLFile:
        """
        Parse DQL text into AST.

        Args:
            dql_text: DQL source code as string

        Returns:
            DQLFile: Root AST node containing all FROM blocks

        Raises:
            DQLSyntaxError: If parsing fails with detailed error message
            MissingFromClauseError: If expectation appears without FROM
            InvalidModelNameError: If model name is not PascalCase
            ReservedKeywordError: If reserved keyword used as identifier

        Example:
            >>> parser = DQLParser()
            >>> ast = parser.parse('from Customer\\nexpect column("email") to_not_be_null')
            >>> len(ast.from_blocks)
            1
        """
        try:
            # Parse with Lark
            tree = self._lark.parse(dql_text)

            # Transform to AST
            ast = self._transformer.transform(tree)

            # Validate AST (FROM clause presence, model names, keywords)
            self._validate_ast(ast, dql_text)

            return ast

        except UnexpectedInput as e:
            # Lark parsing error - convert to DQLSyntaxError
            self._raise_syntax_error(e, dql_text)

        except (
            DQLSyntaxError,
            MissingFromClauseError,
            InvalidModelNameError,
            ReservedKeywordError,
        ):
            # Our custom exceptions - re-raise as-is
            raise

        except Exception as e:
            # Unexpected error - wrap in DQLSyntaxError
            raise DQLSyntaxError(
                message=f"Unexpected parsing error: {str(e)}",
                line=0,
                column=0,
                context="",
            ) from e

    def parse_file(self, filepath: Union[str, Path]) -> DQLFile:
        """
        Parse DQL file and return AST.

        Args:
            filepath: Path to .dql file

        Returns:
            DQLFile: Root AST node

        Raises:
            DQLSyntaxError: If syntax is invalid
            FileNotFoundError: If file doesn't exist

        Example:
            >>> parser = DQLParser()
            >>> ast = parser.parse_file('expectations/customer.dql')
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"DQL file not found: {filepath}")

        dql_text = filepath.read_text(encoding="utf-8")
        return self.parse(dql_text)

    def _validate_ast(self, ast: DQLFile, dql_text: str) -> None:
        """
        Validate AST for semantic correctness.

        Checks:
        1. FROM clause exists
        2. Model names are PascalCase
        3. No reserved keywords used as identifiers

        Args:
            ast: Parsed AST to validate
            dql_text: Original DQL text for context in error messages

        Raises:
            MissingFromClauseError: If no FROM blocks found
            InvalidModelNameError: If model name not PascalCase
            ReservedKeywordError: If reserved keyword used as identifier
        """
        # Check FROM clause exists
        if not ast.from_blocks:
            raise MissingFromClauseError(line=1, column=1, context=self._get_line(dql_text, 1))

        # Validate each FROM block
        for block in ast.from_blocks:
            # Validate model name is PascalCase
            if not self.PASCALCASE_REGEX.match(block.model_name):
                # Find line number for this model name
                line_num = self._find_model_line(dql_text, block.model_name)
                context = self._get_line(dql_text, line_num)
                # Column is position after "from " keyword
                col_num = context.lower().index("from") + 6

                raise InvalidModelNameError(
                    model_name=block.model_name,
                    line=line_num,
                    column=col_num,
                    context=context,
                )

            # Check if model name is a reserved keyword
            if block.model_name.lower() in self.RESERVED_KEYWORDS:
                line_num = self._find_model_line(dql_text, block.model_name)
                context = self._get_line(dql_text, line_num)
                col_num = context.lower().index("from") + 6

                raise ReservedKeywordError(
                    keyword=block.model_name,
                    line=line_num,
                    column=col_num,
                    context=context,
                )

    def _raise_syntax_error(self, lark_error: UnexpectedInput, dql_text: str) -> None:
        """
        Convert Lark parsing error to DQLSyntaxError with formatted message.

        Args:
            lark_error: Lark exception with line/column info
            dql_text: Original DQL text for context

        Raises:
            DQLSyntaxError: Always raises with formatted error message
        """
        line = getattr(lark_error, "line", 0)
        column = getattr(lark_error, "column", 0)
        context = self._get_line(dql_text, line)

        # Extract expected tokens for better error message
        message = str(lark_error)

        # Check for common error patterns and provide helpful messages
        if "expected" in message.lower():
            # Parse expected tokens from Lark error
            if isinstance(lark_error, UnexpectedToken):
                expected = getattr(lark_error, "expected", set())
                if expected:
                    expected_list = ", ".join(sorted(expected)[:5])  # Show first 5
                    message = f"Unexpected token. Expected one of: {expected_list}"

        raise DQLSyntaxError(
            message=message,
            line=line,
            column=column,
            context=context,
        )

    def _get_line(self, text: str, line_num: int) -> str:
        """
        Extract a specific line from text.

        Args:
            text: Full text
            line_num: Line number (1-indexed)

        Returns:
            The line at line_num, or empty string if out of range
        """
        lines = text.splitlines()
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""

    def _find_model_line(self, text: str, model_name: str) -> int:
        """
        Find the line number where a model name appears after FROM keyword.

        Args:
            text: Full DQL text
            model_name: Model name to find

        Returns:
            Line number (1-indexed) where model appears, or 1 if not found
        """
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            # Look for "from ModelName" pattern (case-insensitive for "from")
            if re.search(rf"\bfrom\s+{re.escape(model_name)}\b", line, re.IGNORECASE):
                return i
        return 1


# Convenience functions


def parse_dql(dql_text: str) -> DQLFile:
    """
    Convenience function to parse DQL text.

    Args:
        dql_text: DQL source code as string

    Returns:
        DQLFile: Root AST node

    Example:
        >>> from dql_parser import parse_dql
        >>> ast = parse_dql('from Customer\\nexpect column("email") to_not_be_null')
    """
    parser = DQLParser()
    return parser.parse(dql_text)


def parse_dql_file(filepath: Union[str, Path]) -> DQLFile:
    """
    Convenience function to parse DQL file.

    Args:
        filepath: Path to .dql file

    Returns:
        DQLFile: Root AST node

    Example:
        >>> from dql_parser import parse_dql_file
        >>> ast = parse_dql_file('expectations/customer.dql')
    """
    parser = DQLParser()
    return parser.parse_file(filepath)
