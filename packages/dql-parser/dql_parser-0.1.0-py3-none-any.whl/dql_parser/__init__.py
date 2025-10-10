"""
dql-parser: Pure Python parser for Data Quality Language (DQL).

This package provides a standalone DQL parser with zero dependencies on Django
or any web framework. It parses DQL text into Abstract Syntax Trees (AST) composed
of strongly-typed dataclass nodes.

Example:
    >>> from dql_parser import DQLParser
    >>> parser = DQLParser()
    >>> ast = parser.parse('''
    ... from Customer
    ... expect column("email") to_not_be_null severity critical
    ... ''')
    >>> print(ast.from_blocks[0].model_name)
    Customer
"""

__version__ = "0.1.0"

# Parser
from .parser import DQLParser, parse_dql, parse_dql_file

# AST Nodes
from .ast_nodes import (
    ArithmeticExpr,
    CleanerNode,
    ColumnRef,
    ColumnTarget,
    Comparison,
    DQLFile,
    ExpectationNode,
    FromBlock,
    FunctionCall,
    LogicalExpr,
    RowTarget,
    ToBeIn,
    ToBeBetween,
    ToBeNull,
    ToBeUnique,
    ToMatchPattern,
    ToNotBeNull,
    Value,
)

# Exceptions
from .exceptions import (
    DQLSyntaxError,
    InvalidFieldError,
    InvalidModelNameError,
    InvalidOperatorError,
    MissingFromClauseError,
    ReservedKeywordError,
)

__all__ = [
    # Version
    "__version__",
    # Parser
    "DQLParser",
    "parse_dql",
    "parse_dql_file",
    # AST Nodes - Core
    "DQLFile",
    "FromBlock",
    "ExpectationNode",
    # AST Nodes - Targets
    "ColumnTarget",
    "RowTarget",
    # AST Nodes - Operators
    "ToBeNull",
    "ToNotBeNull",
    "ToMatchPattern",
    "ToBeBetween",
    "ToBeIn",
    "ToBeUnique",
    # AST Nodes - Conditions/Expressions
    "Comparison",
    "LogicalExpr",
    "ColumnRef",
    "Value",
    "FunctionCall",
    "ArithmeticExpr",
    # AST Nodes - Cleaners
    "CleanerNode",
    # Exceptions
    "DQLSyntaxError",
    "InvalidOperatorError",
    "InvalidFieldError",
    "MissingFromClauseError",
    "InvalidModelNameError",
    "ReservedKeywordError",
]
