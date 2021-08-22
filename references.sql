SELECT
    parent_schemas.name AS "FK schema",
    parent_tables.name AS "FK table",
    parent_columns.name AS "FK column",
    referenced_schemas.name AS "Referenced schema",
    referenced_tables.name AS "Referenced table",
    referenced_columns.name AS "Referenced column"
FROM sys.foreign_key_columns AS fk_columns
JOIN sys.tables AS parent_tables ON fk_columns.parent_object_id = parent_tables.object_id
JOIN sys.schemas AS parent_schemas ON parent_tables.schema_id = parent_schemas.schema_id
JOIN sys.columns AS parent_columns ON 
    fk_columns.parent_column_id = parent_columns.column_id
    AND parent_tables.object_id = parent_columns.object_id
JOIN sys.tables AS referenced_tables ON fk_columns.referenced_object_id = referenced_tables.object_id
JOIN sys.schemas AS referenced_schemas ON referenced_tables.schema_id = referenced_schemas.schema_id
JOIN sys.columns AS referenced_columns
    ON fk_columns.referenced_column_id = referenced_columns.column_id
    AND referenced_tables.object_id = referenced_columns.object_id
WHERE 
    parent_tables.schema_id = 5 -- 5 - dlfe
    AND referenced_tables.schema_id = 5 -- 5 - dlfe
ORDER BY
    parent_schemas.name,
    parent_tables.name