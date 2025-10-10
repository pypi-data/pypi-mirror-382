"""SQLGuardian."""

from __future__ import annotations

__all__: tuple[str, ...] = (
    "DEFAULT",
    "SQL",
    "UNSPECIFIED",
    "AllowedDatabaseInfo",
    "AllowedTableInfo",
    "AllowlistError",
    "ColumnName",
    "DatabaseName",
    "DbRule",
    "Description",
    "Dialect",
    "Policy",
    "TableAlias",
    "TableName",
    "TableRule",
    "UnspecifiedType",
    "describe_allowed_databases",
    "describe_allowed_tables",
    "enforce_policy_where_guards",
    "render_markdown_description",
)

from typing import TYPE_CHECKING, Self, TypedDict

import yaml
from pydantic import BaseModel, ConfigDict, Field
from sqlglot import exp, parse_one

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path
    from typing import Final


# ============================================================================
# Sentinel for distinguishing between "not specified" and "explicitly null"
# ============================================================================


class UnspecifiedType:
    """Sentinel type to distinguish between 'not specified' and 'explicitly null'."""

    def __repr__(self) -> str:
        """Represent as string."""
        return "UNSPECIFIED"


UNSPECIFIED = UnspecifiedType()


# ============================================================================
# Domain type aliases (Python 3.13 style)
# ============================================================================

type DatabaseName = str
type TableName = str
type TableAlias = str
type ColumnName = str
type Description = str
type SQL = str
type Dialect = str


# TypedDict describing each row returned by describe_allowed_*
class AllowedDatabaseInfo(TypedDict):
    """Describes one allowlisted database."""

    database: DatabaseName
    guard_column: ColumnName | None
    description: Description


class AllowedTableInfo(TypedDict):
    """Describes one allowlisted table."""

    database: DatabaseName
    table: TableName
    guard_column: ColumnName | None
    description: Description


DEFAULT: Final[str] = "default"


# ============================================================================
# Exceptions
# ============================================================================


class AllowlistError(PermissionError):
    """Raised when a referenced (db, table) is not allowlisted."""


# ============================================================================
# Pydantic models for YAML policy
# ============================================================================


class TableRule(BaseModel):
    """Rules for one table."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    guard_column: ColumnName | None | UnspecifiedType = UNSPECIFIED
    description: Description | None = None


class DbRule(BaseModel):
    """Rules for one database."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    guard_column: ColumnName | None | UnspecifiedType = UNSPECIFIED
    description: Description | None = None
    tables: dict[TableName, TableRule] = Field(default_factory=dict)


def _resolve_guard_column(
    table_guard: ColumnName | None | UnspecifiedType,
    db_guard: ColumnName | None | UnspecifiedType,
    default_guard: ColumnName | None,
) -> ColumnName | None:  # sourcery skip: assign-if-exp, reintroduce-else
    """Resolve guard column with proper fallback logic."""
    if not isinstance(table_guard, UnspecifiedType):
        return table_guard
    if not isinstance(db_guard, UnspecifiedType):
        return db_guard
    return default_guard


class Policy(BaseModel):
    """The overall multi-tenant policy."""

    default_guard_column: ColumnName | None = None
    databases: dict[DatabaseName, DbRule] = Field(default_factory=dict)

    # ------------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------------
    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        """Load a Policy from a YAML file."""
        with path.open(encoding="utf-8") as f:
            return cls.model_validate(yaml.safe_load(f) or {})

    # ------------------------------------------------------------------------
    # Runtime helpers
    # ------------------------------------------------------------------------
    def is_allowed(self, db: DatabaseName | None, table: TableName) -> bool:
        """Is this (db, table) allowlisted?"""
        db_key = db or DEFAULT
        return db_key in self.databases and table in self.databases[db_key].tables

    def guard_column_for(
        self,
        db: DatabaseName | None,
        table: TableName,
    ) -> ColumnName | None:
        """Get the guard column for this (db, table).

        Raises AllowlistError if not allowlisted.

        Returns:
        - The specific guard column if set for table or database
        - The default guard column if none specified at table/database level
        - None if explicitly set to null at any level (disables guard)
        """
        db_key = db or DEFAULT
        db_rule = self.databases.get(db_key)
        if not db_rule:
            msg = f"Database '{db_key}' not allowlisted"
            raise AllowlistError(msg)
        tbl_rule = db_rule.tables.get(table)
        if not tbl_rule:
            msg = f"Table '{db_key}.{table}' not allowlisted"
            raise AllowlistError(msg)

        return _resolve_guard_column(
            tbl_rule.guard_column, db_rule.guard_column, self.default_guard_column
        )

    def database_description(
        self,
        db: DatabaseName | None,
    ) -> Description | None:
        """Get the human/LLM description for this database, if any."""
        db_key = db or DEFAULT
        db_rule = self.databases.get(db_key)
        return db_rule.description if db_rule else None

    def table_description(
        self,
        db: DatabaseName | None,
        table: TableName,
    ) -> Description | None:
        """Get the human/LLM description for this (db, table), if any."""
        db_key = db or DEFAULT
        db_rule = self.databases.get(db_key)
        if not db_rule:
            return None
        table_rule = db_rule.tables.get(table)
        return table_rule.description if table_rule else None


# ============================================================================
# SQL utilities
# ============================================================================


def _table_alias(t: exp.Table) -> TableAlias | None:
    alias = t.args.get("alias")
    if isinstance(alias, exp.TableAlias):
        ident = alias.args.get("this")
        if isinstance(ident, exp.Identifier):
            return ident.name
    return None


def _table_name(t: exp.Table) -> TableName:
    ident = t.args.get("this")
    return ident.name if isinstance(ident, exp.Identifier) else str(ident)


def _db_name(t: exp.Table) -> DatabaseName | None:
    db = t.args.get("db")
    return db.name if isinstance(db, exp.Identifier) else None


def _predicate_exists(
    where_expr: exp.Where | None,
    pred: exp.Expression,
    dialect: Dialect,
) -> bool:
    if not where_expr:
        return False
    target = pred.sql(dialect=dialect)
    return any(eq.sql(dialect=dialect) == target for eq in where_expr.find_all(exp.EQ))


def _and_where(select: exp.Select, extra_predicates: list[exp.Expression]) -> None:
    if not extra_predicates:
        return
    combined = extra_predicates[0]
    for p in extra_predicates[1:]:
        combined = exp.and_(combined, p)
    existing = select.args.get("where")
    select.set(
        "where",
        exp.Where(this=exp.and_(existing.this, combined) if existing else combined),
    )


def _collect_cte_names(root: exp.Expression) -> set[str]:
    """Collect all CTE names defined in the query."""
    cte_names = set()

    # Find all WITH clauses
    for with_clause in root.find_all(exp.With):
        # Each WITH clause contains CTEs
        for cte in with_clause.expressions:
            if isinstance(cte, exp.CTE) and (alias := cte.alias):
                cte_names.add(alias)

    return cte_names


def _is_actual_table_reference(t: exp.Table, cte_names: set[str]) -> bool:
    # sourcery skip: assign-if-exp, boolean-if-exp-identity, reintroduce-else
    """Check if this Table reference is to an actual database table (not a CTE)."""
    table_name = _table_name(t)

    # If it has a database prefix, it's definitely an actual table
    # (even if there's a CTE with the same base name)
    if _db_name(t) is not None:
        return True

    # If no database prefix but table name matches a CTE, it's a CTE reference
    if table_name in cte_names:  # noqa: SIM103
        return False

    # If no database prefix and not a CTE, assume it's an actual table
    # (this handles cases where tables are referenced without db prefix)
    return True


def _get_tables_excluding_cte_definitions(
    select: exp.Select, cte_names: set[str]
) -> list[exp.Table]:
    """Get tables referenced by this SELECT, excluding those in its CTE definitions.

    When a SELECT has a WITH clause, we don't want to add guards for tables
    inside the CTEs to the outer SELECT's WHERE clause. Those tables will be
    guarded when we process their respective CTE's SELECT statement.
    """
    # Find all tables in the SELECT
    all_tables = list(select.find_all(exp.Table))

    # Find tables that are in CTE definitions attached to this SELECT
    with_clause = select.args.get("with")
    if not with_clause:
        return [t for t in all_tables if _is_actual_table_reference(t, cte_names)]

    tables_in_ctes: set[exp.Table] = set()
    for cte in with_clause.expressions:
        if isinstance(cte, exp.CTE):
            tables_in_ctes.update(cte.find_all(exp.Table))

    # Return only tables not in CTE definitions
    return [
        t
        for t in all_tables
        if _is_actual_table_reference(t, cte_names) and t not in tables_in_ctes
    ]


# ============================================================================
# Core enforcement
# ============================================================================


def enforce_policy_where_guards(
    sql: SQL,
    *,
    guard_value: str,
    policy: Policy,
    read_dialect: Dialect,
    write_dialect: Dialect,
) -> SQL:
    """Enforce the multi-tenant policy on the given SQL query.

    - Validates that every referenced (db, table) is allowlisted.
    - Adds WHERE `<alias>.<guard_col> = <company_value>` for each referenced table
      in every SELECT (joins, subqueries, CTEs included).
    - Skips adding a predicate if an identical one already exists.
    - Ignores CTE references (they're not actual database tables).
    """
    root = parse_one(sql, read=read_dialect)

    # Collect all CTE names first
    cte_names = _collect_cte_names(root)

    # Check all ACTUAL table references (not CTEs)
    for t in root.find_all(exp.Table):
        if _is_actual_table_reference(t, cte_names):
            db, tbl = _db_name(t), _table_name(t)
            if not policy.is_allowed(db, tbl):
                db_key = db or DEFAULT
                msg = f"Reference to non-allowlisted table: {db_key}.{tbl}"
                raise AllowlistError(msg)

    # Add guards to all actual tables (including those in CTEs/subqueries)
    for sel in root.find_all(exp.Select):
        # Get tables directly referenced by this SELECT (not in its CTE definitions)
        tables = _get_tables_excluding_cte_definitions(sel, cte_names)
        if not tables:
            continue

        predicates: list[exp.Expression] = []
        for t in tables:
            db, tbl = _db_name(t), _table_name(t)
            guard_col = policy.guard_column_for(db, tbl)
            if not guard_col:
                continue
            qualifier: TableAlias | TableName = _table_alias(t) or tbl
            pred = exp.EQ(
                this=exp.column(guard_col, table=qualifier),
                expression=exp.Literal.string(guard_value),
            )
            if not _predicate_exists(
                sel.args.get("where"),
                pred,
                dialect=write_dialect,
            ):
                predicates.append(pred)
        _and_where(sel, predicates)

    return root.sql(dialect=write_dialect)


# ============================================================================
# Human/LLM descriptions of the allowlist
# ============================================================================


def describe_allowed_databases(policy: Policy) -> list[AllowedDatabaseInfo]:
    """Describe the allowlisted databases in the policy."""
    return [
        AllowedDatabaseInfo(
            database=db_name,
            guard_column=_resolve_guard_column(
                UNSPECIFIED, db_rule.guard_column, policy.default_guard_column
            ),
            description=db_rule.description or "",
        )
        for db_name, db_rule in sorted(policy.databases.items())
    ]


def describe_allowed_tables(policy: Policy) -> list[AllowedTableInfo]:
    """Describe the allowlisted tables in the policy.

    Return a list of AllowedTableInfo dicts describing every allowed table.
    """
    rows: list[AllowedTableInfo] = []
    for db_name, db_rule in sorted(policy.databases.items()):
        rows.extend(
            AllowedTableInfo(
                database=db_name,
                table=tbl_name,
                guard_column=policy.guard_column_for(db_name, tbl_name),
                description=tbl_rule.description or "",
            )
            for tbl_name, tbl_rule in sorted(db_rule.tables.items())
        )
    return rows


def render_markdown_description(policy: Policy) -> str:
    """Pretty Markdown table of all allowed tables for documentation or LLM priming."""
    rows = describe_allowed_tables(policy)
    lines: list[str] = [
        "### Allowed Databases",
        "",
        "| Database | Guard Column | Description |",
        "|---|---|---|",
    ]
    for db in describe_allowed_databases(policy):
        desc = db["description"].replace("\n", " ").strip()
        lines.append(f"| `{db['database']}` | `{db['guard_column'] or ''}` | {desc} |")
    lines.extend(
        [
            "",
            "### Allowed Tables",
            "",
            "| Database | Table | Guard Column | Description |",
            "|---|---|---|---|",
        ]
    )
    for r in rows:
        desc = r["description"].replace("\n", " ").strip()
        lines.append(
            f"| `{r['database']}` | `{r['table']}` | `{r['guard_column']}` | {desc} |"
        )
    return "\n".join(lines)
