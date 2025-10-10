"""
Custom exception classes for DQL parsing errors.

Provides structured error reporting with line/column information and
helpful error messages.
"""

from __future__ import annotations


class DQLSyntaxError(Exception):
    """
    Base exception for DQL syntax errors.

    Attributes:
        message: Human-readable error description
        line: Line number where error occurred (1-indexed)
        column: Column number where error occurred (1-indexed)
        context: The problematic line of DQL code
        suggested_fix: Optional suggestion for how to fix the error
    """

    def __init__(
        self,
        message: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
        suggested_fix: str = "",
    ):
        self.message = message
        self.line = line
        self.column = column
        self.context = context
        self.suggested_fix = suggested_fix
        super().__init__(self.get_formatted_message())

    def __str__(self) -> str:
        return self.get_formatted_message()

    def get_formatted_message(self) -> str:
        """
        Format error message with line/column information.

        Format:
            DQLSyntaxError at line {line}, column {column}:
                {problematic_line}
                {caret_pointer}
            {error_description}
            {suggested_fix}
        """
        parts = [f"DQLSyntaxError at line {self.line}, column {self.column}:"]

        # Add context line with caret pointer if available
        if self.context:
            parts.append(f"    {self.context}")
            if self.column > 0:
                # Create caret pointer aligned to error column
                caret = " " * (self.column - 1 + 4) + "^"  # +4 for indentation
                parts.append(caret)

        # Add error message
        parts.append(self.message)

        # Add suggested fix if available
        if self.suggested_fix:
            parts.append("")
            parts.append(f"Suggested fix: {self.suggested_fix}")

        return "\n".join(parts)


class InvalidOperatorError(DQLSyntaxError):
    """
    Raised when an unknown or invalid operator is used.

    Example:
        expect column("email") to_be_valid
        # "to_be_valid" is not a recognized operator
    """

    def __init__(
        self,
        operator: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
    ):
        message = f"Invalid operator: '{operator}'"
        suggested_fix = (
            "Valid operators: to_be_null, to_not_be_null, to_match_pattern, "
            "to_be_between, to_be_in, to_be_unique"
        )
        super().__init__(message, line, column, context, suggested_fix)


class InvalidFieldError(DQLSyntaxError):
    """
    Raised when an invalid field reference is encountered.

    Example:
        expect column("") to_be_null
        # Empty field name
    """

    def __init__(
        self,
        field: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
    ):
        message = f"Invalid field reference: '{field}'"
        suggested_fix = "Field names must be non-empty strings"
        super().__init__(message, line, column, context, suggested_fix)


class MissingFromClauseError(DQLSyntaxError):
    """
    Raised when an expectation is defined without a FROM clause.

    Example:
        expect column("email") to_not_be_null
        # Missing FROM clause before expectation
    """

    def __init__(
        self,
        line: int = 1,
        column: int = 1,
        context: str = "",
    ):
        message = "Missing 'from' clause before expectation statement"
        suggested_fix = (
            "Add 'from ModelName' before expect statement:\n"
            "    from Customer\n"
            '    expect column("email") to_not_be_null severity critical'
        )
        super().__init__(message, line, column, context, suggested_fix)


class InvalidModelNameError(DQLSyntaxError):
    """
    Raised when model name doesn't follow PascalCase convention.

    Model names must start with uppercase letter and follow PascalCase.

    Example:
        from customer_model
        # Should be "Customer" or "CustomerModel" (PascalCase)
    """

    def __init__(
        self,
        model_name: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
    ):
        message = (
            f"Invalid model name: '{model_name}'\n"
            "Model names must be PascalCase (e.g., Customer, OrderItem)"
        )
        # Convert snake_case to PascalCase for suggestion
        suggested_name = "".join(word.capitalize() for word in model_name.split("_"))
        suggested_fix = f"from {suggested_name}"
        super().__init__(message, line, column, context, suggested_fix)


class ReservedKeywordError(DQLSyntaxError):
    """
    Raised when a reserved keyword is used as an identifier.

    DQL has reserved keywords that cannot be used as model names
    or field names.
    """

    def __init__(
        self,
        keyword: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
    ):
        message = f"Cannot use reserved keyword '{keyword}' as identifier"
        suggested_fix = (
            "Reserved keywords cannot be used as model names or field names. "
            "Choose a different name."
        )
        super().__init__(message, line, column, context, suggested_fix)
