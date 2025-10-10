"""Unit tests for sqlguardian."""

import pytest

from sqlguardian import (
    AllowlistError,
    Policy,
    describe_allowed_tables,
    enforce_policy_where_guards,
    render_markdown_description,
)


def make_policy() -> Policy:
    """Create a sample Policy for testing."""
    return Policy.model_validate(
        {
            "default_guard_column": "companyId",
            "databases": {
                "default": {
                    "guard_column": "companyId",
                    "description": "Default database",
                    "tables": {
                        "users": {"description": "User table"},
                        "orders": {
                            "guard_column": "orgId",
                            "description": "Order table",
                        },
                        # No description, should fall back to database description
                        "products": {},
                    },
                },
                "analytics": {
                    "guard_column": "tenantId",
                    "description": "Analytics database",
                    "tables": {
                        "events": {"description": "Event log"},
                        # No description, should fall back to database description
                        "metrics": {},
                        "insights": {"description": "AI insights"},
                        "assets": {"description": "Asset master data"},
                    },
                },
            },
        }
    )


def test_policy_is_allowed() -> None:
    """Test Policy.is_allowed for various cases."""
    policy = make_policy()
    assert policy.is_allowed(None, "users")
    assert policy.is_allowed("default", "orders")
    assert policy.is_allowed("analytics", "events")
    assert not policy.is_allowed("default", "missing")
    assert not policy.is_allowed("unknown", "users")


def test_policy_guard_column_for() -> None:
    """Test Policy.guard_column_for returns correct guard column."""
    policy = make_policy()
    assert policy.guard_column_for(None, "users") == "companyId"
    assert policy.guard_column_for("default", "orders") == "orgId"
    assert policy.guard_column_for("analytics", "events") == "tenantId"


def test_policy_guard_column_for_error() -> None:
    """Test Policy.guard_column_for raises AllowlistError for missing tables."""
    policy = make_policy()
    with pytest.raises(AllowlistError):
        policy.guard_column_for("default", "missing")
    with pytest.raises(AllowlistError):
        policy.guard_column_for("unknown", "users")


def test_policy_table_description() -> None:
    """Test Policy.table_description returns correct descriptions."""
    policy = make_policy()
    assert policy.table_description(None, "users") == "User table"
    assert policy.table_description("default", "orders") == "Order table"
    assert policy.table_description("analytics", "events") == "Event log"
    # Test that table_description only returns table-specific descriptions
    assert policy.table_description("default", "products") is None
    assert policy.table_description("analytics", "metrics") is None
    assert policy.table_description("default", "missing") is None


def test_policy_database_description() -> None:
    """Test Policy.database_description returns correct descriptions."""
    policy = make_policy()
    assert policy.database_description("default") == "Default database"
    assert policy.database_description("analytics") == "Analytics database"
    assert policy.database_description("missing") is None
    # Falls back to "default"
    assert policy.database_description(None) == "Default database"


def test_enforce_policy_where_guards_adds_predicate() -> None:
    """Test enforcement adds guard predicate to SQL."""
    policy = make_policy()
    sql = "SELECT * FROM users"
    out = enforce_policy_where_guards(
        sql,
        guard_value="42",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )
    assert "WHERE users.companyId = '42'" in out


def test_enforce_policy_where_guards_existing_predicate() -> None:
    """Test enforcement does not duplicate existing predicate."""
    policy = make_policy()
    sql = "SELECT * FROM users WHERE users.companyId = '42'"
    out = enforce_policy_where_guards(
        sql,
        guard_value="42",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )
    # Should not duplicate predicate
    assert out.count("users.companyId = '42'") == 1


def test_enforce_policy_where_guards_non_allowlisted() -> None:
    """Test enforcement raises AllowlistError for non-allowlisted tables."""
    policy = make_policy()
    sql = "SELECT * FROM missing"
    with pytest.raises(AllowlistError):
        enforce_policy_where_guards(
            sql,
            guard_value="42",
            policy=policy,
            read_dialect="duckdb",
            write_dialect="duckdb",
        )


def test_enforce_policy_where_guards_with_cte() -> None:
    """Test enforcement works with CTEs - should not validate CTE names."""
    policy = make_policy()
    sql = """
    WITH user_stats AS (
        SELECT user_id, COUNT(*) as order_count
        FROM orders
        GROUP BY user_id
    )
    SELECT u.name, us.order_count
    FROM users u
    JOIN user_stats us ON u.user_id = us.user_id
    """

    # This should work - user_stats is a CTE, not a real table
    out = enforce_policy_where_guards(
        sql,
        guard_value="42",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Should add guards to real tables (users, orders) but not CTE (user_stats)
    assert "u.companyId = '42'" in out
    assert "orders.orgId = '42'" in out
    # Should not try to add guard to CTE
    assert "user_stats.companyId" not in out
    assert "user_stats.tenantId" not in out


def test_enforce_policy_where_guards_complex_cte() -> None:
    """Test enforcement with multiple CTEs and nested queries."""
    policy = make_policy()
    sql = """
    WITH recent_events AS (
        SELECT user_id, event_type, COUNT(*) as event_count
        FROM analytics.events
        WHERE event_date >= '2023-01-01'
        GROUP BY user_id, event_type
    ),
    user_metrics AS (
        SELECT user_id, SUM(event_count) as total_events
        FROM recent_events
        GROUP BY user_id
    )
    SELECT u.name, um.total_events, re.event_type
    FROM users u
    JOIN user_metrics um ON u.user_id = um.user_id
    JOIN recent_events re ON u.user_id = re.user_id
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="company123",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Should add guards to real tables
    assert "u.companyId = 'company123'" in out
    assert "events.tenantId = 'company123'" in out

    # Should not add guards to CTEs
    assert "recent_events.tenantId" not in out
    assert "user_metrics.companyId" not in out


def test_enforce_policy_where_guards_cte_with_non_allowlisted_name() -> None:
    """Test that CTEs with names that would fail allowlist check still work."""
    policy = make_policy()
    sql = """
    WITH forbidden_table_name AS (
        SELECT user_id, name
        FROM users
    )
    SELECT * FROM forbidden_table_name
    """

    # This should work - forbidden_table_name is just a CTE alias
    out = enforce_policy_where_guards(
        sql,
        guard_value="test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Should only validate the real table (users)
    assert "users.companyId = 'test'" in out


def test_enforce_policy_where_guards_mixed_real_and_cte_tables() -> None:
    """Test query with both real tables and CTE references."""
    policy = make_policy()
    sql = """
    WITH insight_summary AS (
        SELECT asset_id, COUNT(*) as insight_count
        FROM analytics.insights
        GROUP BY asset_id
    )
    SELECT a.name, i.insight_count, e.event_type
    FROM analytics.assets a
    LEFT JOIN insight_summary i ON a.asset_id = i.asset_id
    LEFT JOIN analytics.events e ON a.asset_id = e.asset_id
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="tenant456",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Should add guards to all real tables
    assert "insights.tenantId = 'tenant456'" in out
    assert "a.tenantId = 'tenant456'" in out
    assert "e.tenantId = 'tenant456'" in out

    # Should not add guard to CTE
    assert "insight_summary.tenantId" not in out


def test_enforce_policy_where_guards_cte_shadows_real_table() -> None:
    """Test CTE that has same name as a real table."""
    policy = make_policy()
    sql = """
    WITH users AS (
        SELECT 'fake' as name
    )
    SELECT u1.name as real_name, u2.name as fake_name
    FROM default.users u1
    CROSS JOIN users u2
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="shadow_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Should add guard only to the real table (with db prefix)
    assert "u1.companyId = 'shadow_test'" in out
    # Should not add guard to the CTE reference
    assert "u2.companyId" not in out


def test_describe_allowed_tables() -> None:
    """Test describe_allowed_tables returns all allowed tables."""
    policy = make_policy()
    rows = describe_allowed_tables(policy)
    assert any(r["table"] == "users" for r in rows)
    assert any(r["table"] == "orders" for r in rows)
    assert any(r["table"] == "events" for r in rows)
    # Check that tables without descriptions have empty descriptions
    products_row = next(r for r in rows if r["table"] == "products")
    assert products_row["description"] == ""
    metrics_row = next(r for r in rows if r["table"] == "metrics")
    assert metrics_row["description"] == ""


def test_render_markdown_description() -> None:
    """Test render_markdown_description outputs correct markdown."""
    policy = make_policy()
    md = render_markdown_description(policy)
    assert "| Database | Table | Guard Column | Description |" in md
    assert "`default`" in md
    assert "`users`" in md


def test_security_nested_subqueries() -> None:
    """Test that nested subqueries cannot bypass security."""
    policy = make_policy()
    sql = """
    SELECT u.name
    FROM users u
    WHERE u.id IN (
        SELECT o.user_id
        FROM orders o
        WHERE o.amount > (
            SELECT AVG(p.price)
            FROM products p
        )
    )
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="company123",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # All real tables should have guard predicates
    assert "u.companyId = 'company123'" in out
    assert "o.orgId = 'company123'" in out  # orders uses orgId guard column
    assert "p.companyId = 'company123'" in out


def test_security_cte_accessing_sensitive_data() -> None:
    """Test that CTEs cannot access sensitive data without guards."""
    policy = make_policy()
    sql = """
    WITH admin_data AS (
        SELECT * FROM users WHERE role = 'admin'
    ),
    order_summary AS (
        SELECT user_id, SUM(amount) as total
        FROM orders
        GROUP BY user_id
    )
    SELECT a.name, o.total
    FROM admin_data a
    JOIN order_summary o ON a.id = o.user_id
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="tenant456",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Both tables referenced in CTEs must have guards
    assert "users.companyId = 'tenant456'" in out
    assert "orders.orgId = 'tenant456'" in out
    # CTE references themselves should not have guards
    assert "admin_data.companyId" not in out
    assert "order_summary.orgId" not in out


def test_security_union_attack() -> None:
    """Test that UNION queries cannot bypass security."""
    policy = make_policy()
    sql = """
    SELECT name FROM users WHERE active = true
    UNION
    SELECT name FROM users WHERE role = 'admin'
    UNION ALL
    SELECT 'fake' as name FROM orders WHERE amount > 1000
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="secure123",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Each SELECT in UNION should have appropriate guards
    assert (
        out.count("users.companyId = 'secure123'") >= 2  # noqa: PLR2004
    )  # At least 2 users references
    assert "orders.orgId = 'secure123'" in out


def test_security_correlated_subquery() -> None:
    """Test that correlated subqueries have proper guards."""
    policy = make_policy()
    sql = """
    SELECT u.name, u.email
    FROM users u
    WHERE EXISTS (
        SELECT 1 FROM orders o
        WHERE o.user_id = u.id
        AND o.status = 'completed'
    )
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="correlation_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Both outer and inner queries should have guards
    assert "u.companyId = 'correlation_test'" in out
    assert "o.orgId = 'correlation_test'" in out


def test_security_insert_with_subquery() -> None:
    """Test that INSERT with subquery has proper guards."""
    policy = make_policy()
    sql = """
    INSERT INTO products (name, price)
    SELECT CONCAT('Product-', u.name), 100
    FROM users u
    WHERE u.active = true
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="insert_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Subquery in INSERT should have guards
    assert "u.companyId = 'insert_test'" in out


def test_security_window_function_with_subquery() -> None:
    """Test that window functions with subqueries have proper guards."""
    policy = make_policy()
    sql = """
    SELECT
        u.name,
        ROW_NUMBER() OVER (
            PARTITION BY (
                SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id
            )
        ) as rank
    FROM users u
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="window_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Both main query and subquery in window function should have guards
    assert "u.companyId = 'window_test'" in out
    assert "o.orgId = 'window_test'" in out


def test_security_complex_cte_chain() -> None:
    """Test complex chain of CTEs referencing each other and real tables."""
    policy = make_policy()
    sql = """
    WITH user_orders AS (
        SELECT u.id, u.name, o.amount
        FROM users u
        JOIN orders o ON u.id = o.user_id
    ),
    high_value_users AS (
        SELECT uo.id, uo.name, SUM(uo.amount) as total
        FROM user_orders uo
        GROUP BY uo.id, uo.name
        HAVING SUM(uo.amount) > 1000
    ),
    user_products AS (
        SELECT hvu.name, p.name as product_name
        FROM high_value_users hvu
        CROSS JOIN products p
        WHERE p.price < hvu.total * 0.1
    )
    SELECT * FROM user_products
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="chain_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # All real tables should have guards, even when accessed through CTE chain
    assert "u.companyId = 'chain_test'" in out
    assert "o.orgId = 'chain_test'" in out
    assert "p.companyId = 'chain_test'" in out
    # CTE references should not have guards
    assert "user_orders.companyId" not in out
    assert "high_value_users.companyId" not in out
    assert "user_products.companyId" not in out


def test_security_recursive_cte() -> None:
    """Test that recursive CTEs have proper guards on real tables."""
    policy = make_policy()
    sql = """
    WITH RECURSIVE user_hierarchy AS (
        SELECT id, name, manager_id, 0 as level
        FROM users
        WHERE manager_id IS NULL

        UNION ALL

        SELECT u.id, u.name, u.manager_id, uh.level + 1
        FROM users u
        JOIN user_hierarchy uh ON u.manager_id = uh.id
        WHERE uh.level < 5
    )
    SELECT * FROM user_hierarchy
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="recursive_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Base case should have guard on users table (no alias)
    assert "users.companyId = 'recursive_test'" in out
    # Recursive case should have guard on aliased users table
    assert "u.companyId = 'recursive_test'" in out
    # CTE reference should not have guard
    assert "user_hierarchy.companyId" not in out


def test_security_case_expression_with_subquery() -> None:
    """Test that CASE expressions with subqueries have proper guards."""
    policy = make_policy()
    sql = """
    SELECT
        u.name,
        CASE
            WHEN (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) > 5 THEN 'VIP'
            WHEN (SELECT SUM(p.price) FROM products p) > 1000 THEN 'Premium'
            ELSE 'Regular'
        END as customer_type
    FROM users u
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="case_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # All table references should have guards
    assert "u.companyId = 'case_test'" in out
    assert "o.orgId = 'case_test'" in out
    assert "p.companyId = 'case_test'" in out


def test_security_database_qualification_attack() -> None:
    """Test that using database qualifiers cannot bypass security."""
    policy = make_policy()
    sql = """
    WITH sneaky_data AS (
        SELECT u1.name as public_name, u2.name as private_name
        FROM default.users u1
        CROSS JOIN users u2
        WHERE u1.role = 'public'
    )
    SELECT sd.public_name, sd.private_name
    FROM sneaky_data sd
    JOIN analytics.events e ON e.user_name = sd.private_name
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="qualify_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # All real tables should have guards regardless of qualification
    assert "u1.companyId = 'qualify_test'" in out  # default.users
    assert "u2.companyId = 'qualify_test'" in out  # users (unqualified)
    assert "e.tenantId = 'qualify_test'" in out  # analytics.events
    # CTE should not have guard
    assert "sd.companyId" not in out
    assert "sneaky_data.companyId" not in out


def test_security_mixed_guard_columns() -> None:
    """Test that different guard columns are applied correctly."""
    policy = make_policy()
    sql = """
    SELECT u.name, o.amount, e.event_type, a.name as asset_name
    FROM users u
    JOIN orders o ON u.id = o.user_id
    JOIN analytics.events e ON u.id = e.user_id
    JOIN analytics.assets a ON e.asset_id = a.id
    """

    out = enforce_policy_where_guards(
        sql,
        guard_value="mixed_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Each table should use its appropriate guard column
    assert "u.companyId = 'mixed_test'" in out  # users uses companyId
    assert "o.orgId = 'mixed_test'" in out  # orders uses orgId
    assert "e.tenantId = 'mixed_test'" in out  # events uses tenantId
    assert "a.tenantId = 'mixed_test'" in out  # assets uses tenantId


def test_security_non_allowlisted_database_attack() -> None:
    """Test that accessing tables from non-allowlisted databases fails."""
    policy = make_policy()
    sql = """
    SELECT u.name, h.secret
    FROM users u
    JOIN hacker_db.users h ON u.email = h.email
    """

    # This should raise an AllowlistError since hacker_db is not allowlisted
    with pytest.raises(
        AllowlistError, match=r"non-allowlisted table: hacker_db\.users"
    ):
        enforce_policy_where_guards(
            sql,
            guard_value="attack_test",
            policy=policy,
            read_dialect="duckdb",
            write_dialect="duckdb",
        )


def test_security_injection_through_cte_names() -> None:
    """Test that CTE names cannot be used to inject malicious table references."""
    policy = make_policy()
    # Try to create a CTE with a name that looks like a qualified table
    sql = """
    WITH "hacker_db.secret_table" AS (
        SELECT 'fake' as data
    )
    SELECT u.name, h.data
    FROM users u
    CROSS JOIN "hacker_db.secret_table" h
    """

    # This should work because the quoted name is just a CTE alias
    out = enforce_policy_where_guards(
        sql,
        guard_value="injection_test",
        policy=policy,
        read_dialect="duckdb",
        write_dialect="duckdb",
    )

    # Only the real table should have a guard
    assert "u.companyId = 'injection_test'" in out
    # The CTE reference should not have a guard predicate
    assert '"hacker_db.secret_table".companyId' not in out
    assert '"hacker_db.secret_table".tenantId' not in out
