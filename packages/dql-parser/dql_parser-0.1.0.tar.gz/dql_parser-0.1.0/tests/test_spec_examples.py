"""
Unit tests that validate all 12 DQL specification examples parse successfully.

Each test corresponds to an example from docs/dql-specification.md lines 598-856.
Tests verify that all examples in the spec are valid parseable DQL.

[Source: docs/stories/1.3.implement-lark-parser.md#task-8]
[Source: docs/dql-specification.md#example-library lines 616-856]
"""

import pytest

from dql_parser.parser import DQLParser


class TestSpecificationExamples:
    """Test that all 12 specification examples parse without errors."""

    def test_example_01_customer_email_validation(self):
        """Example 1: Customer Email Validation [lines 618-627]"""
        parser = DQLParser()
        dql = """
        from Customer

        # Customer email is required and must match standard format
        expect column("email") to_not_be_null severity critical
        expect column("email") to_match_pattern("[email protected]+\\.[a-zA-Z]{2,}") severity critical
            on_failure clean_with("normalize_email")
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert ast.from_blocks[0].model_name == "Customer"
        assert len(ast.from_blocks[0].expectations) == 2

    def test_example_02_order_total_validation(self):
        """Example 2: Order Total Validation [lines 636-644]"""
        parser = DQLParser()
        dql = """
        from Order

        # Order total must be positive and within reasonable bounds
        expect column("total_amount") to_not_be_null severity critical
        expect column("total_amount") to_be_between(0.01, 1000000.00) severity critical
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert ast.from_blocks[0].model_name == "Order"
        assert len(ast.from_blocks[0].expectations) == 2

    def test_example_03_product_status_validation(self):
        """Example 3: Product Status Validation [lines 653-660]"""
        parser = DQLParser()
        dql = """
        from Product

        # Product status must be one of predefined values
        expect column("status") to_be_in(["active", "inactive", "discontinued", "out_of_stock"]) severity warning
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert ast.from_blocks[0].model_name == "Product"
        assert len(ast.from_blocks[0].expectations) == 1

    def test_example_04_customer_phone_uniqueness(self):
        """Example 4: Customer Phone Uniqueness [lines 668-677]"""
        parser = DQLParser()
        dql = """
        from Customer

        # Phone numbers should be unique per customer
        expect column("phone") to_be_unique severity warning
        expect column("phone") to_match_pattern("\\d{3}-\\d{3}-\\d{4}") severity info
            on_failure clean_with("format_phone_number")
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert ast.from_blocks[0].model_name == "Customer"
        assert len(ast.from_blocks[0].expectations) == 2

    def test_example_05_optional_field_handling(self):
        """Example 5: Optional Field Handling [lines 686-693]"""
        parser = DQLParser()
        dql = """
        from Customer

        # Middle name is optional, but if provided, must not be empty string
        expect column("middle_name") to_match_pattern(".+") severity info
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert ast.from_blocks[0].model_name == "Customer"
        assert len(ast.from_blocks[0].expectations) == 1

    def test_example_06_multi_field_date_validation(self):
        """Example 6: Multi-Field Date Validation [lines 701-711]"""
        parser = DQLParser()
        dql = """
        from Order

        # Order ship date must be after order date
        expect row where column("ship_date") >= column("order_date") to_not_be_null severity critical

        # Delivery date must be after ship date
        expect row where column("delivery_date") >= column("ship_date") to_not_be_null severity critical
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert ast.from_blocks[0].model_name == "Order"
        assert len(ast.from_blocks[0].expectations) == 2

    def test_example_07_severity_escalation(self):
        """Example 7: Severity Escalation [lines 719-727]"""
        parser = DQLParser()
        dql = """
        from Customer

        # Email format: warning for missing, critical for invalid format
        expect column("email") to_not_be_null severity warning
        expect column("email") to_match_pattern("[email protected]+\\.[a-zA-Z]{2,}") severity critical
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert ast.from_blocks[0].model_name == "Customer"
        assert len(ast.from_blocks[0].expectations) == 2

    def test_example_08_cleaner_function_attachment(self):
        """Example 8: Cleaner Function Attachment [lines 735-744]"""
        parser = DQLParser()
        dql = """
        from Customer

        # Standardize address before validation
        expect column("address") to_not_be_null severity critical
            on_failure clean_with("standardize_address")
            on_failure clean_with("geocode_address")
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert ast.from_blocks[0].model_name == "Customer"
        assert len(ast.from_blocks[0].expectations) == 1
        assert len(ast.from_blocks[0].expectations[0].cleaners) == 2

    def test_example_09_complex_pattern_matching(self):
        """Example 9: Complex Pattern Matching [lines 753-766]"""
        parser = DQLParser()
        dql = """
        from Customer

        # SSN format validation (XXX-XX-XXXX)
        expect column("ssn") to_match_pattern("\\d{3}-\\d{2}-\\d{4}") severity critical

        # Credit card format (16 digits, with optional spaces)
        expect column("credit_card") to_match_pattern("(\\d{4}\\s?){4}") severity critical

        # URL validation
        expect column("website") to_match_pattern("https?://[^\\s]+") severity warning
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        assert ast.from_blocks[0].model_name == "Customer"
        assert len(ast.from_blocks[0].expectations) == 3

    def test_example_10_date_range_validation(self):
        """Example 10: Date Range Validation [lines 774-791]"""
        parser = DQLParser()
        dql = """
        from Employee

        # Employee hire date must be in the past
        expect row where column("hire_date") < column("current_date") to_not_be_null severity critical

        from Project

        # Project end date must be after start date
        expect row where column("end_date") > column("start_date") to_not_be_null severity critical

        from Contract

        # Contract expiration must be in the future (for active contracts)
        expect row where column("status") == "active" AND column("expiration_date") > column("current_date") to_not_be_null severity warning
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 3
        assert ast.from_blocks[0].model_name == "Employee"
        assert ast.from_blocks[1].model_name == "Project"
        assert ast.from_blocks[2].model_name == "Contract"

    def test_example_11_string_concatenation_and_computed_fields(self):
        """Example 11: String Concatenation and Computed Fields [lines 800-825]"""
        parser = DQLParser()
        dql = """
        from Product

        # Product name must match format: ID-COLOR
        expect row where column("product_name") == CONCAT(column("id"), "-", column("color")) to_not_be_null severity warning

        from Customer

        # Display name should be "Last, First"
        expect row where column("display_name") == CONCAT(column("last_name"), ", ", column("first_name")) to_not_be_null severity info

        # Full address validation with concatenation
        expect row where column("full_address") == CONCAT(
            column("street"), ", ",
            column("city"), ", ",
            column("state"), " ",
            column("zip_code")
        ) to_not_be_null severity warning

        from Order

        # Total price calculation with arithmetic
        expect row where column("total_price") == column("unit_price") * column("quantity") + column("shipping_cost") to_not_be_null severity critical
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 3
        assert ast.from_blocks[0].model_name == "Product"
        assert ast.from_blocks[1].model_name == "Customer"
        assert ast.from_blocks[2].model_name == "Order"

    def test_example_12_multi_model_validation(self):
        """Example 12: Multi-Model Validation in Single File [lines 835-853]"""
        parser = DQLParser()
        dql = """
        from Customer

        # Customer validations
        expect column("email") to_not_be_null severity critical
        expect column("phone") to_match_pattern("\\d{3}-\\d{3}-\\d{4}") severity warning

        from Order

        # Order validations
        expect column("total_amount") to_be_between(0.01, 1000000.00) severity critical
        expect row where column("ship_date") >= column("order_date") to_not_be_null severity critical

        from Product

        # Product validations
        expect column("status") to_be_in(["active", "inactive", "discontinued"]) severity warning
        """
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 3
        assert ast.from_blocks[0].model_name == "Customer"
        assert ast.from_blocks[1].model_name == "Order"
        assert ast.from_blocks[2].model_name == "Product"
        assert len(ast.from_blocks[0].expectations) == 2
        assert len(ast.from_blocks[1].expectations) == 2
        assert len(ast.from_blocks[2].expectations) == 1
