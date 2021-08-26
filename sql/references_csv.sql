SELECT
    fk_schemas.name AS "fk_schema",
    fk_tables.name AS "fk_table",
    fk_columns.name AS "fk_column",
    key_schemas.name AS "key_schema",
    key_tables.name AS "key_table",
    key_columns.name AS "key_column"
FROM sys.foreign_key_columns AS ref
JOIN sys.tables AS fk_tables ON ref.parent_object_id = fk_tables.object_id
JOIN sys.schemas AS fk_schemas ON fk_tables.schema_id = fk_schemas.schema_id
JOIN sys.columns AS fk_columns ON
    ref.parent_column_id = fk_columns.column_id
    AND fk_tables.object_id = fk_columns.object_id
JOIN sys.tables AS key_tables ON ref.referenced_object_id = key_tables.object_id
JOIN sys.schemas AS key_schemas ON key_tables.schema_id = key_schemas.schema_id
JOIN sys.columns AS key_columns
    ON ref.referenced_column_id = key_columns.column_id
    AND key_tables.object_id = key_columns.object_id
WHERE
    fk_tables.type = 'U'
    OR key_tables.type = 'U'
ORDER BY
    fk_schemas.name,
    fk_tables.name;