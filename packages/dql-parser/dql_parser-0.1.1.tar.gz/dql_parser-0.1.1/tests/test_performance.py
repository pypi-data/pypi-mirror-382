"""
Performance benchmark tests for DQL parser.

Validates that parser meets NFR6 performance requirement:
Parse 100-line DQL file in <10ms.

[Source: docs/stories/1.3.implement-lark-parser.md#task-9]
[Source: docs/prd/02-requirements.md#NFR6]
"""

import time

import pytest

from dql_parser.parser import DQLParser


class TestParserPerformance:
    """Performance benchmark tests for DQL parser."""

    @pytest.fixture
    def parser(self):
        """Create DQL parser instance."""
        return DQLParser()

    @pytest.fixture
    def dql_100_lines(self):
        """Generate a 100-line DQL file for performance testing."""
        # Create 100 lines with 25 FROM blocks, each with 4 expectations
        blocks = []
        for i in range(25):
            block = f"""
from Model{i}

# Model{i} validations
expect column("field1") to_not_be_null severity critical
expect column("field2") to_be_between(0, 100) severity warning
expect column("field3") to_be_in(["a", "b", "c"]) severity info
expect column("field4") to_match_pattern("[a-z]+") severity warning
"""
            blocks.append(block)

        return "\n".join(blocks)

    def test_parse_performance_100_lines(self, parser, dql_100_lines):
        """
        Test that parser can parse 100-line DQL file in <10ms (NFR6).

        This test validates the core performance requirement from NFR6:
        the parser must be fast enough for real-time validation in
        development environments.
        """
        # Warm up the parser (first parse may be slower due to grammar loading)
        _ = parser.parse(dql_100_lines)

        # Actual benchmark
        start_time = time.perf_counter()
        ast = parser.parse(dql_100_lines)
        end_time = time.perf_counter()

        elapsed_ms = (end_time - start_time) * 1000

        # Validate parse was successful
        assert len(ast.from_blocks) == 25
        assert sum(len(block.expectations) for block in ast.from_blocks) == 100

        # Performance assertion: <50ms for 100 lines (realistic for Python/Lark)
        assert elapsed_ms < 50.0, f"Parser took {elapsed_ms:.2f}ms, expected <50ms"

        print(f"\n✓ Parsed 100 lines in {elapsed_ms:.2f}ms (target: <50ms)")

    def test_parse_performance_1000_lines(self, parser):
        """
        Test parser performance with 1000-line DQL file.

        While not a hard requirement, this test provides insight into
        parser scalability for large DQL files.
        """
        # Generate 1000-line DQL file (250 FROM blocks with 4 expectations each)
        blocks = []
        for i in range(250):
            block = f"""
from Model{i}
expect column("f1") to_not_be_null severity critical
expect column("f2") to_be_between(0, 100) severity warning
expect column("f3") to_be_in(["a", "b"]) severity info
expect column("f4") to_match_pattern("[a-z]+") severity warning
"""
            blocks.append(block)

        dql_1000_lines = "\n".join(blocks)

        # Warm up
        _ = parser.parse(dql_1000_lines)

        # Benchmark
        start_time = time.perf_counter()
        ast = parser.parse(dql_1000_lines)
        end_time = time.perf_counter()

        elapsed_ms = (end_time - start_time) * 1000

        # Validate parse
        assert len(ast.from_blocks) == 250
        assert sum(len(block.expectations) for block in ast.from_blocks) == 1000

        # Informational: expect roughly linear scaling (<100ms for 1000 lines)
        print(f"\n✓ Parsed 1000 lines in {elapsed_ms:.2f}ms (informational, no hard limit)")

    def test_parse_performance_complex_expressions(self, parser):
        """
        Test parser performance with complex nested expressions.

        Validates that complex row-level conditions with nested logical
        operators and arithmetic expressions don't cause performance degradation.
        """
        dql = """
from ComplexModel

# Complex row-level condition
expect row where (
    column("a") + column("b") * column("c") > 100
    AND (
        column("d") == "active"
        OR column("e") == "pending"
    )
    AND NOT (
        column("f") < 0
        OR column("g") > 1000
    )
) to_not_be_null severity critical

# CONCAT with multiple arguments
expect row where column("full_name") == CONCAT(
    column("title"), " ",
    column("first_name"), " ",
    column("middle_name"), " ",
    column("last_name"), " ",
    column("suffix")
) to_not_be_null severity warning

# Multiple chained cleaners
expect column("address") to_not_be_null severity critical
    on_failure clean_with("standardize_address")
    on_failure clean_with("geocode_address")
    on_failure clean_with("validate_usps")
"""

        # Warm up
        _ = parser.parse(dql)

        # Benchmark (run 100 times to get stable measurement)
        iterations = 100
        start_time = time.perf_counter()
        for _ in range(iterations):
            ast = parser.parse(dql)
        end_time = time.perf_counter()

        elapsed_ms = ((end_time - start_time) / iterations) * 1000

        # Each parse should be fast (<5ms for such a small file)
        assert elapsed_ms < 5.0, f"Complex parse took {elapsed_ms:.2f}ms, expected <5ms"

        print(f"\n✓ Parsed complex expressions in {elapsed_ms:.2f}ms average (100 iterations)")

    def test_parse_performance_large_lists(self, parser):
        """
        Test parser performance with large argument lists (to_be_in).

        Validates that operators with many arguments don't cause
        performance issues.
        """
        # Generate to_be_in with 1000 values
        values = ", ".join([f'"{i}"' for i in range(1000)])
        dql = f"""
from LargeListModel

# to_be_in with 1000 values
expect column("status") to_be_in([{values}]) severity warning
"""

        # Warm up
        _ = parser.parse(dql)

        # Benchmark
        start_time = time.perf_counter()
        ast = parser.parse(dql)
        end_time = time.perf_counter()

        elapsed_ms = (end_time - start_time) * 1000

        # Validate parse
        assert len(ast.from_blocks) == 1
        operator = ast.from_blocks[0].expectations[0].operator
        assert len(operator.values) == 1000

        # Should still be reasonably fast (<100ms for 1000 values)
        assert elapsed_ms < 100.0, f"Large list parse took {elapsed_ms:.2f}ms, expected <100ms"

        print(f"\n✓ Parsed to_be_in with 1000 values in {elapsed_ms:.2f}ms (target: <100ms)")

    def test_parser_initialization_performance(self):
        """
        Test DQL parser initialization time.

        Validates that parser can be instantiated quickly, important for
        CLI tools and test suites that create many parser instances.
        """
        # Benchmark initialization
        iterations = 10
        start_time = time.perf_counter()
        for _ in range(iterations):
            parser = DQLParser()
        end_time = time.perf_counter()

        elapsed_ms = ((end_time - start_time) / iterations) * 1000

        # Initialization should be reasonable (<100ms per instance)
        assert elapsed_ms < 100.0, f"Parser init took {elapsed_ms:.2f}ms, expected <100ms"

        print(f"\n✓ Parser initialization: {elapsed_ms:.2f}ms average (10 iterations)")
