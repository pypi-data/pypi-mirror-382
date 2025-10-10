"""Test cases for the new guard_column: null functionality."""

import pytest

from sqlguardian import (
    Policy,
    describe_allowed_databases,
    describe_allowed_tables,
    enforce_policy_where_guards,
)


def test_guard_column_explicit_null_table_level() -> None:
    """Test that guard_column: null at table level disables guard for that table."""
    policy = Policy.model_validate(
        {
            "default_guard_column": "companyId",
            "databases": {
                "default": {
                    "guard_column": "companyId",
                    "tables": {
                        "users": {"description": "User table"},  # Uses database guard
                        "public_data": {
                            "guard_column": None,  # Explicitly disabled
                            "description": "Public data",
                        },
                    },
                },
            },
        }
    )

    # Check guard column resolution
    assert policy.guard_column_for("default", "users") == "companyId"
    assert policy.guard_column_for("default", "public_data") is None

    # Test enforcement - users should get guard, public_data should not
    sql = "SELECT * FROM users JOIN public_data ON users.id = public_data.user_id"
    out = enforce_policy_where_guards(
        sql,
        guard_value="test123",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Should have guard for users but not for public_data
    assert "users.companyId = 'test123'" in out
    assert "public_data.companyId" not in out


def test_guard_column_explicit_null_database_level() -> None:
    """Test that guard_column: null at database level disables guard for all tables."""
    policy = Policy.model_validate(
        {
            "default_guard_column": "companyId",
            "databases": {
                "default": {
                    "guard_column": "companyId",
                    "tables": {
                        "users": {"description": "User table"},
                    },
                },
                "public": {
                    "guard_column": None,  # Explicitly disabled for entire database
                    "description": "Public database",
                    "tables": {
                        "countries": {"description": "Country reference data"},
                        "currencies": {"description": "Currency reference data"},
                    },
                },
            },
        }
    )

    # Check guard column resolution
    assert policy.guard_column_for("default", "users") == "companyId"
    assert policy.guard_column_for("public", "countries") is None
    assert policy.guard_column_for("public", "currencies") is None

    # Test enforcement
    sql = (
        "SELECT * FROM users JOIN public.countries "
        "ON users.country_id = public.countries.id"
    )
    out = enforce_policy_where_guards(
        sql,
        guard_value="test123",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Should have guard for users but not for public tables
    assert "users.companyId = 'test123'" in out
    assert "countries.companyId" not in out


def test_guard_column_table_overrides_database_null() -> None:
    """Test that table-level guard column can override database-level null."""
    policy = Policy.model_validate(
        {
            "default_guard_column": "companyId",
            "databases": {
                "mixed": {
                    "guard_column": None,  # Database-level disabled
                    "description": "Mixed database",
                    "tables": {
                        "public_data": {"description": "Public data"},  # Inherits None
                        "protected_data": {
                            "guard_column": "tenantId",  # Override with specific column
                            "description": "Protected data",
                        },
                    },
                },
            },
        }
    )

    # Check guard column resolution
    assert policy.guard_column_for("mixed", "public_data") is None
    assert policy.guard_column_for("mixed", "protected_data") == "tenantId"

    # Test enforcement
    sql = (
        "SELECT * FROM mixed.public_data JOIN mixed.protected_data "
        "ON public_data.id = protected_data.ref_id"
    )
    out = enforce_policy_where_guards(
        sql,
        guard_value="test123",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Should have guard only for protected_data
    assert "public_data.tenantId" not in out
    assert "public_data.companyId" not in out
    assert "protected_data.tenantId = 'test123'" in out


def test_guard_column_unspecified_uses_fallback() -> None:
    """Test that omitting guard_column uses fallback logic as before."""
    policy = Policy.model_validate(
        {
            "default_guard_column": "companyId",
            "databases": {
                "default": {
                    "guard_column": "orgId",
                    "tables": {
                        # No guard_column specified - should use orgId from database
                        "users": {},
                        "orders": {
                            "guard_column": "customerId",  # Explicit override
                        },
                    },
                },
                "analytics": {
                    # No guard_column specified - should use companyId from default
                    "tables": {
                        "events": {},  # Should use companyId from default
                    },
                },
            },
        }
    )

    # Check guard column resolution
    assert policy.guard_column_for("default", "users") == "orgId"
    assert policy.guard_column_for("default", "orders") == "customerId"
    assert policy.guard_column_for("analytics", "events") == "companyId"


def test_describe_functions_handle_null_guard_columns() -> None:
    """Test that describe functions properly show null guard columns."""
    policy = Policy.model_validate(
        {
            "default_guard_column": "companyId",
            "databases": {
                "default": {
                    "guard_column": "orgId",
                    "tables": {
                        "users": {},  # Uses orgId
                        "public_data": {"guard_column": None},  # Explicit null
                    },
                },
                "public": {
                    "guard_column": None,  # Database-level null
                    "tables": {
                        "countries": {},  # Inherits null
                    },
                },
                "mixed": {
                    # Uses default
                    "tables": {
                        "events": {},  # Uses companyId from default
                    },
                },
            },
        }
    )

    # Test describe_allowed_tables
    tables = describe_allowed_tables(policy)
    table_guards = {(t["database"], t["table"]): t["guard_column"] for t in tables}

    assert table_guards[("default", "users")] == "orgId"
    assert table_guards[("default", "public_data")] is None
    assert table_guards[("public", "countries")] is None
    assert table_guards[("mixed", "events")] == "companyId"

    # Test describe_allowed_databases
    databases = describe_allowed_databases(policy)
    db_guards = {db["database"]: db["guard_column"] for db in databases}

    assert db_guards["default"] == "orgId"
    assert db_guards["public"] is None
    assert db_guards["mixed"] == "companyId"  # Uses default since not specified


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
