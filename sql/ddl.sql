DECLARE @SCHEMA_ID int = 5; -- 5 - dlfe

SELECT
    schemas.name AS "schema",
    tables.name AS "table",
    columns.name AS "column",
    column_types.name AS "column_type"
FROM sys.schemas AS schemas
JOIN sys.tables AS tables ON schemas.schema_id = tables.schema_id
JOIN sys.columns AS columns ON tables.object_id = columns.object_id
JOIN sys.types AS column_types ON columns.user_type_id = column_types.user_type_id
WHERE
    schemas.schema_id = @SCHEMA_ID
    OR EXISTS (
        SELECT *
        FROM sys.foreign_key_columns AS fk_columns
        JOIN sys.tables AS parent_tables ON fk_columns.parent_object_id = parent_tables.object_id
        JOIN sys.tables AS referenced_tables ON fk_columns.referenced_object_id = referenced_tables.object_id
        WHERE
            tables.object_id IN (fk_columns.parent_object_id, fk_columns.referenced_object_id)
            AND @SCHEMA_ID IN (parent_tables.schema_id, referenced_tables.schema_id)
    )
ORDER BY
    schemas.name,
    tables.name,
    columns.column_id