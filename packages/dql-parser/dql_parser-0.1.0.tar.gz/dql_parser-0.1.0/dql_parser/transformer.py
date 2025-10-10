"""
Lark Transformer for converting parse tree to DQL AST nodes.

This module transforms the Lark parse tree generated from grammar.lark
into strongly-typed AST node dataclasses defined in ast_nodes.py.
"""

from __future__ import annotations

from typing import Any, List, Union

from lark import Token, Transformer

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


class DQLTransformer(Transformer):
    """
    Transforms Lark parse tree into DQL AST nodes.

    Each method corresponds to a grammar rule and transforms the parsed
    children into appropriate AST node instances.
    """

    # Top-level structure

    def dql_file(self, children: List[FromBlock]) -> DQLFile:
        """Transform dql_file: from_block+ → DQLFile"""
        return DQLFile(from_blocks=children)

    def from_block(self, children: List[Any]) -> FromBlock:
        """Transform from_block: FROM model_name expectation+ → FromBlock"""
        # Filter out FROM terminal token, keep only transformed nodes
        filtered = [c for c in children if not isinstance(c, Token)]
        model_name = filtered[0]
        expectations = filtered[1:]
        return FromBlock(model_name=model_name, expectations=expectations)

    def model_name(self, children: List[Token]) -> str:
        """Transform model_name: IDENTIFIER → str"""
        return str(children[0])

    # Expectation structure

    def expectation(self, children: List[Any]) -> ExpectationNode:
        """Transform expectation: EXPECT target operator_clause severity? cleaners? → ExpectationNode"""
        # Filter out EXPECT terminal token
        filtered = [c for c in children if not isinstance(c, Token)]

        target = filtered[0]
        operator = filtered[1]
        severity = None
        cleaners = []

        # Process optional severity and cleaners
        for child in filtered[2:]:
            if isinstance(child, str):  # severity level
                severity = child
            elif isinstance(child, list):  # cleaners list
                cleaners = child

        return ExpectationNode(
            target=target, operator=operator, severity=severity, cleaners=cleaners
        )

    # Target types

    def target(
        self, children: List[Union[ColumnTarget, RowTarget]]
    ) -> Union[ColumnTarget, RowTarget]:
        """Transform target: column_target | row_target"""
        return children[0]

    def column_target(self, children: List[Token]) -> ColumnTarget:
        """Transform column_target: "column" "(" STRING ")" → ColumnTarget"""
        field_name = self._unquote_string(children[0])
        return ColumnTarget(field_name=field_name)

    def row_target(self, children: List[Any]) -> RowTarget:
        """Transform row_target: "row" WHERE condition → RowTarget"""
        # Filter out WHERE terminal token
        filtered = [c for c in children if not isinstance(c, Token)]
        condition = filtered[0]
        return RowTarget(condition=condition)

    # Operators

    def operator_clause(
        self, children: List[Any]
    ) -> Union[ToBeNull, ToNotBeNull, ToMatchPattern, ToBeBetween, ToBeIn, ToBeUnique]:
        """Transform operator_clause: operator_name operator_args? → Operator"""
        operator = children[0]  # Already transformed by operator_name

        # If operator needs args, get them from children[1]
        if len(children) > 1:
            args = children[1]
            # Update operator with args
            if isinstance(operator, ToMatchPattern):
                return ToMatchPattern(pattern=self._unquote_string(args[0]))
            elif isinstance(operator, ToBeBetween):
                return ToBeBetween(min_value=args[0], max_value=args[1])
            elif isinstance(operator, ToBeIn):
                return ToBeIn(values=args[0])  # args[0] is already a list

        return operator

    def operator_name(
        self, children: List[Any]
    ) -> Union[ToBeNull, ToNotBeNull, ToMatchPattern, ToBeBetween, ToBeIn, ToBeUnique]:
        """Transform operator_name: operator_rule → Operator"""
        # children[0] is the specific operator instance
        return children[0]

    # Individual operator rules

    def to_be_null(self, children: List[Any]) -> ToBeNull:
        """Transform to_be_null: "to_be_null" → ToBeNull()"""
        return ToBeNull()

    def to_not_be_null(self, children: List[Any]) -> ToNotBeNull:
        """Transform to_not_be_null: "to_not_be_null" → ToNotBeNull()"""
        return ToNotBeNull()

    def to_match_pattern(self, children: List[Any]) -> ToMatchPattern:
        """Transform to_match_pattern: "to_match_pattern" → ToMatchPattern()"""
        # Args will be added by operator_clause
        return ToMatchPattern(pattern="")

    def to_be_between(self, children: List[Any]) -> ToBeBetween:
        """Transform to_be_between: "to_be_between" → ToBeBetween()"""
        # Args will be added by operator_clause
        return ToBeBetween(min_value=0, max_value=0)

    def to_be_in(self, children: List[Any]) -> ToBeIn:
        """Transform to_be_in: "to_be_in" → ToBeIn()"""
        # Args will be added by operator_clause
        return ToBeIn(values=[])

    def to_be_unique(self, children: List[Any]) -> ToBeUnique:
        """Transform to_be_unique: "to_be_unique" → ToBeUnique()"""
        return ToBeUnique()

    def operator_args(self, children: List[Any]) -> Any:
        """Transform operator_args: "(" arg_list ")" → pass through arg_list"""
        return children[0] if len(children) == 1 else children

    def arg_list(self, children: List[Any]) -> List[Any]:
        """Transform arg_list: arg ("," arg)* → List[Any]"""
        return children

    def arg(self, children: List[Any]) -> Any:
        """Transform arg: STRING | NUMBER | list → value"""
        value = children[0]
        if isinstance(value, Token):
            if value.type == "STRING":
                return self._unquote_string(value)
            elif value.type == "NUMBER":
                return self._parse_number(value)
        return value  # Already transformed list

    def list(self, children: List[Any]) -> List[Any]:
        """Transform list: "[" arg_list "]" → List[Any]"""
        return children[0] if children else []

    # Severity

    def severity_clause(self, children: List[Any]) -> str:
        """Transform severity_clause: "severity" severity_level → str"""
        # Filter out "severity" terminal
        filtered = [
            c for c in children if not isinstance(c, Token) or c.type.startswith("SEVERITY_")
        ]
        return filtered[0] if filtered else children[0]

    def severity_level(self, children: List[Token]) -> str:
        """Transform severity_level: SEVERITY_CRITICAL | SEVERITY_WARNING | SEVERITY_INFO → str"""
        severity_token = children[0]
        # Extract the severity level from token type
        if severity_token.type == "SEVERITY_CRITICAL":
            return "critical"
        elif severity_token.type == "SEVERITY_WARNING":
            return "warning"
        elif severity_token.type == "SEVERITY_INFO":
            return "info"
        return str(severity_token)

    # Cleaners

    def cleaner_clause(self, children: List[CleanerNode]) -> List[CleanerNode]:
        """Transform cleaner_clause: cleaner_call+ → List[CleanerNode]"""
        return children

    def cleaner_call(self, children: List[Any]) -> CleanerNode:
        """Transform cleaner_call: ON_FAILURE CLEAN_WITH "(" STRING args? ")" → CleanerNode"""
        # Filter out ON_FAILURE and CLEAN_WITH terminals
        filtered = [c for c in children if not isinstance(c, Token) or c.type == "STRING"]
        cleaner_name = self._unquote_string(filtered[0])
        args = filtered[1] if len(filtered) > 1 else []
        return CleanerNode(cleaner_name=cleaner_name, args=args)

    def cleaner_args(self, children: List[Any]) -> List[Any]:
        """Transform cleaner_args: "," arg_list → List[Any]"""
        return children[0]

    # Row-level conditions

    def condition(self, children: List[Any]) -> Union[Comparison, LogicalExpr]:
        """Transform condition: comparison | logical_expr | "(" condition ")" → Condition"""
        return children[0]

    def comparison(self, children: List[Any]) -> Comparison:
        """Transform comparison: expr COMPARATOR expr → Comparison"""
        left = children[0]
        operator = str(children[1])
        right = children[2]
        return Comparison(left=left, operator=operator, right=right)

    def logical_expr(self, children: List[Any]) -> LogicalExpr:
        """Transform logical_expr: condition (AND|OR) condition | NOT condition → LogicalExpr"""
        if len(children) == 1:  # NOT condition (NOT is filtered out)
            operator = "NOT"
            operands = [children[0]]
        elif len(children) == 2 and isinstance(children[0], Token):  # NOT token, condition
            operator = "NOT"
            operands = [children[1]]
        else:  # condition (AND|OR) condition
            # Filter to get: condition, operator_token, condition
            filtered = [c for c in children if not isinstance(c, Token) or c.type in ("AND", "OR")]
            left = filtered[0] if not isinstance(filtered[0], Token) else filtered[1]
            right = filtered[2] if len(filtered) > 2 else filtered[1]
            # Find the operator token
            op_token = next(
                (c for c in filtered if isinstance(c, Token) and c.type in ("AND", "OR")), None
            )
            operator = op_token.type if op_token else "AND"
            operands = [left, right]
        return LogicalExpr(operator=operator, operands=operands)

    # Expressions

    def expr(self, children: List[Any]) -> Union[ColumnRef, Value, FunctionCall, ArithmeticExpr]:
        """Transform expr: column_ref | value | function_call | arithmetic_expr | "(" expr ")" → Expr"""
        return children[0]

    def column_ref(self, children: List[Token]) -> ColumnRef:
        """Transform column_ref: "column" "(" STRING ")" → ColumnRef"""
        field_name = self._unquote_string(children[0])
        return ColumnRef(field_name=field_name)

    def value(self, children: List[Token]) -> Value:
        """Transform value: STRING | NUMBER | NULL → Value"""
        token = children[0]
        if token.type == "STRING":
            return Value(value=self._unquote_string(token))
        elif token.type == "NUMBER":
            return Value(value=self._parse_number(token))
        elif token.type == "NULL":
            return Value(value=None)
        return Value(value=str(token))

    # Functions

    def function_call(self, children: List[FunctionCall]) -> FunctionCall:
        """Transform function_call: concat_func → FunctionCall"""
        return children[0]

    def concat_func(self, children: List[Any]) -> FunctionCall:
        """Transform concat_func: "CONCAT" "(" expr ("," expr)+ ")" → FunctionCall"""
        return FunctionCall(function_name="CONCAT", args=children)

    # Arithmetic

    def arithmetic_expr(self, children: List[Any]) -> ArithmeticExpr:
        """Transform arithmetic_expr: expr ARITH_OP expr → ArithmeticExpr"""
        left = children[0]
        operator = str(children[1])
        right = children[2]
        return ArithmeticExpr(operator=operator, left=left, right=right)

    # Helper methods

    def _unquote_string(self, token: Token) -> str:
        """Remove surrounding quotes from STRING token"""
        s = str(token)
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
        return s

    def _parse_number(self, token: Token) -> Union[int, float]:
        """Parse NUMBER token to int or float"""
        s = str(token)
        if "." in s:
            return float(s)
        return int(s)
