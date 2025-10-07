import hashlib
from typing import Optional, Set, Tuple

import pandas as pd
from datadict_connector_base import MetadataSource
from pydantic import BaseModel, model_validator
from sqlalchemy import Engine, create_engine, text
from sqlglot import exp, parse_one


class MysqlCredentials(BaseModel):
    """
    Pydantic model for MySQL/MariaDB connection credentials.

    Supports either:
    1. A connection_string in standard MySQL format: mysql://user:pass@host:port/db or mariadb://...
    2. Individual parameters: host, port, database, username, password

    If connection_string is provided, it takes precedence.
    """

    type: Optional[str] = None

    connection_string: Optional[str] = None

    host: Optional[str] = None
    port: Optional[int] = 3306
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @model_validator(mode="after")
    def validate_credentials(self):
        """Ensure either connection_string or individual parameters are provided"""
        if self.connection_string:
            return self

        required_fields = ["host", "database", "username", "password"]
        missing_fields = [field for field in required_fields if getattr(self, field) is None]

        if missing_fields:
            raise ValueError(
                f"Either 'connection_string' must be provided, or all of these fields: "
                f"{', '.join(required_fields)}. Missing: {', '.join(missing_fields)}"
            )

        return self

    def to_connection_string(self) -> str:
        """Convert credentials to SQLAlchemy connection string"""
        if self.connection_string:
            normalized = self.connection_string

            # Handle both mysql:// and mariadb:// prefixes
            if normalized.startswith("mariadb://"):
                return normalized.replace("mariadb://", "mysql+pymysql://", 1)

            if normalized.startswith("mysql+"):
                return normalized

            if normalized.startswith("mysql://"):
                return normalized.replace("mysql://", "mysql+pymysql://", 1)

            if not normalized.startswith("mysql+"):
                return f"mysql+pymysql://{normalized}"

            return normalized

        # Build from individual parameters
        return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class MysqlSource(MetadataSource):
    """
    MySQL/MariaDB metadata source implementation using SQLAlchemy
    """

    def __init__(self):
        self.credentials: Optional[MysqlCredentials] = None
        self._engine: Optional[Engine] = None
        self._database_name: Optional[str] = None
        self._table_schema_index: dict[str, Set[str]] = {}

    def set_credentials(self, credentials: dict):
        """
        Set MySQL/MariaDB connection credentials
        """
        self.credentials = MysqlCredentials(**credentials)
        # Reset engine when credentials change
        self._engine = None

    def _get_engine(self) -> Engine:
        """Get or create SQLAlchemy engine"""
        if not self.credentials:
            raise ValueError("Credentials must be set before connecting")

        if self._engine is None:
            connection_string = self.credentials.to_connection_string()
            self._engine = create_engine(connection_string)
        return self._engine

    def _resolve_database_name(self, engine: Engine) -> str:
        """Return and cache the current database name for the connection."""
        if not self._database_name:
            query = text("SELECT DATABASE() AS database_name")
            result = pd.read_sql_query(query, engine)
            if result.empty:
                raise ValueError("Unable to determine current database name")
            self._database_name = result.iloc[0]["database_name"]
        return self._database_name

    def read_metadata(self) -> pd.DataFrame:
        """
        Read metadata from MySQL/MariaDB and return as pandas DataFrame compatible with sync system.

        Returns DataFrame with columns required by sync system:
        - type: Item type (database, schema, table, column)
        - name: Item name
        - key: Fully qualified name (e.g., "database.schema.table")
        - sub_type: Optional subtype classification
        - data_type: Data type information (for columns)
        - parent_key: Parent item's fully qualified name (null for root items)
        """
        engine = self._get_engine()

        database_name = self._resolve_database_name(engine)

        # Get all schemas, tables, and columns in one optimized query
        metadata_query = text("""
        SELECT DISTINCT
            t.table_schema as schema_name,
            t.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            c.ordinal_position,
            t.table_type
        FROM information_schema.tables t
        LEFT JOIN information_schema.columns c
            ON t.table_schema = c.table_schema
            AND t.table_name = c.table_name
        WHERE t.table_type IN ('BASE TABLE', 'VIEW', 'SYSTEM VIEW')
            AND t.table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
        ORDER BY t.table_schema, t.table_name, c.ordinal_position
        """)

        raw_metadata = pd.read_sql_query(metadata_query, engine)

        # Build hierarchical DataFrame with all levels
        all_items = []
        id_map: dict[str, str] = {}

        def make_id(key: str) -> str:
            digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
            return f"{digest[:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}"

        def register_item(record: dict) -> None:
            key = record["key"]
            item_id = make_id(key)
            record["id"] = item_id
            id_map[key] = item_id
            all_items.append(record)

        # 1. Database level
        register_item(
            {
                "type": "database",
                "name": database_name,
                "key": database_name,
                "sub_type": None,
                "data_type": None,
                "parent_key": None,
            }
        )

        # 2. Schema level
        schemas = raw_metadata["schema_name"].unique()
        for schema_name in schemas:
            schema_fqn = f"{database_name}.{schema_name}"
            parent_id = id_map.get(database_name)
            register_item(
                {
                    "type": "schema",
                    "name": schema_name,
                    "key": schema_fqn,
                    "sub_type": None,
                    "data_type": None,
                    "parent_key": parent_id,
                }
            )

        # 3. Table level
        tables = raw_metadata[["schema_name", "table_name", "table_type"]].drop_duplicates()
        self._populate_table_schema_index(tables)

        for _, row in tables.iterrows():
            schema_name = row["schema_name"]
            table_name = row["table_name"]
            table_fqn = f"{database_name}.{schema_name}.{table_name}"
            table_type = row.get("table_type")

            register_item(
                {
                    "type": "table",
                    "name": table_name,
                    "key": table_fqn,
                    "sub_type": table_type,
                    "data_type": None,
                    "parent_key": f"{database_name}.{schema_name}",
                }
            )

        # 4. Column level
        for _, row in raw_metadata.iterrows():
            # Skip rows without column data
            if pd.isna(row["column_name"]):
                continue

            schema_name = row["schema_name"]
            table_name = row["table_name"]
            column_name = row["column_name"]
            column_fqn = f"{database_name}.{schema_name}.{table_name}.{column_name}"
            # Format data type with nullable info
            data_type = row["data_type"]
            if row["is_nullable"] == "NO":
                data_type = f"{data_type} NOT NULL"

            register_item(
                {
                    "type": "column",
                    "name": column_name,
                    "key": column_fqn,
                    "sub_type": None,
                    "data_type": data_type,
                    "parent_key": f"{database_name}.{schema_name}.{table_name}",
                }
            )

        df = pd.DataFrame(all_items)
        return df

    @staticmethod
    def _normalize_identifier(value) -> Optional[str]:
        if isinstance(value, exp.Identifier):
            return value.this
        return value

    def _populate_table_schema_index(self, tables_df: pd.DataFrame) -> None:
        index: dict[str, Set[str]] = {}
        for _, row in tables_df.iterrows():
            schema = row.get("schema_name")
            table_name = row.get("table_name")
            if not schema or not table_name:
                continue
            index.setdefault(str(table_name).lower(), set()).add(str(schema))
        self._table_schema_index = index

    def _get_table_schema_index(self, engine: Engine) -> dict[str, Set[str]]:
        if self._table_schema_index:
            return self._table_schema_index

        schema_query = text(
            """
            SELECT table_schema AS schema_name, table_name
            FROM information_schema.tables
            WHERE table_type IN ('BASE TABLE', 'VIEW', 'SYSTEM VIEW')
              AND table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
            """
        )
        tables_df = pd.read_sql_query(schema_query, engine)
        self._populate_table_schema_index(tables_df)
        return self._table_schema_index

    def _extract_view_dependencies(
        self,
        definition: str,
        default_schema: str,
        default_database: str,
        table_schema_index: dict[str, Set[str]],
    ) -> Set[Tuple[str, str, str]]:
        """Return fully-qualified table references used by a view definition."""
        dependencies: Set[Tuple[str, str, str]] = set()

        try:
            expression = parse_one(definition, read="mysql")
        except Exception:
            return dependencies

        cte_names = {cte.alias_or_name for cte in expression.find_all(exp.CTE)}

        for table in expression.find_all(exp.Table):
            table_name = table.name
            if not table_name or table_name in cte_names:
                continue

            schema = self._normalize_identifier(table.db)
            catalog = self._normalize_identifier(table.catalog) or default_database
            table_key = str(table_name).lower()

            if not schema:
                candidates = table_schema_index.get(table_key, set())
                if len(candidates) == 1:
                    schema = next(iter(candidates))
                elif default_schema and default_schema in candidates:
                    schema = default_schema
                elif candidates:
                    schema = next(iter(candidates))
                else:
                    schema = default_schema

            if not schema:
                continue

            dependencies.add((str(catalog), str(schema), str(table_name)))

        return dependencies

    def read_lineage(self) -> Optional[pd.DataFrame]:
        """Extract lineage edges between views and their upstream tables."""
        engine = self._get_engine()
        database_name = self._resolve_database_name(engine)

        lineage_query = text(
            """
            SELECT
                table_schema AS schema_name,
                table_name AS view_name,
                view_definition AS definition
            FROM information_schema.views
            WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
            """
        )

        views_df = pd.read_sql_query(lineage_query, engine)
        table_schema_index = self._get_table_schema_index(engine)
        edges: list[dict] = []

        for row in views_df.itertuples(index=False):
            definition = getattr(row, "definition", None)
            if not definition:
                continue

            schema_name = row.schema_name
            view_name = row.view_name
            downstream_key = f"{database_name}.{schema_name}.{view_name}"

            dependencies = self._extract_view_dependencies(
                definition, schema_name, database_name, table_schema_index
            )

            if not dependencies:
                continue

            for catalog, schema, table_name in dependencies:
                if schema in {"mysql", "sys", "performance_schema", "information_schema"}:
                    continue
                upstream_key = f"{catalog}.{schema}.{table_name}"
                if upstream_key == downstream_key:
                    continue
                edges.append(
                    {
                        "src_key": upstream_key,
                        "dst_key": downstream_key,
                        "edge_type": "depends_on",
                        "properties": {
                            "source": "mysql_view",
                            "exact_match": True,
                        },
                    }
                )

        if not edges:
            return None

        return pd.DataFrame(edges)

    def close(self):
        """Close database engine"""
        if self._engine:
            self._engine.dispose()
            self._engine = None

