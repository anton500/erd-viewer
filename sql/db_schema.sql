SELECT
    schemas.name AS "name",
    tables.name AS "name",
    (
        SELECT
            col.name AS "name",
            CASE
                WHEN column_types.name IN ('varchar', 'char', 'varbinary', 'binary') THEN column_types.name + '(' + IIF(col.max_length = -1, 'max', CAST(col.max_length AS VARCHAR(25))) + ')'
                WHEN column_types.name IN ('nvarchar', 'nchar') THEN column_types.name + '(' + IIF(col.max_length = -1, 'max', CAST(col.max_length / 2 AS VARCHAR(25)))+ ')'
                WHEN column_types.name IN ('decimal', 'numeric') THEN column_types.name + '(' + CAST(col.precision AS VARCHAR(25)) + ',' + CAST(col.scale AS VARCHAR(25)) + ')'
                WHEN column_types.name IN ('datetime2') THEN column_types.name + '(' + CAST(col.scale AS VARCHAR(25)) + ')'
                ELSE column_types.name
            END AS "type",
            CASE col.is_nullable
                WHEN 0 THEN 'NOT NULL'
                WHEN 1 THEN 'NULL'
            END AS "null",
            (
                SELECT
                    schemas.name AS "schema",
                    tables.name AS "table",
                    columns.name AS "column"
                FROM sys.foreign_key_columns AS ref
                JOIN sys.tables AS tables ON ref.parent_object_id = tables.object_id
                JOIN sys.schemas AS schemas ON tables.schema_id = schemas.schema_id
                JOIN sys.columns AS columns ON
                    ref.parent_column_id = columns.column_id
                    AND tables.object_id = columns.object_id
                WHERE
                    ref.referenced_object_id = col.object_id
                    AND ref.referenced_column_id = col.column_id
                ORDER BY
                    schemas.name,
                    tables.name,
                    columns.column_id
                FOR JSON PATH
            ) AS "fk_references",
            (
                SELECT
                    schemas.name AS "schema",
                    tables.name AS "table",
                    columns.name AS "column"
                FROM sys.foreign_key_columns AS ref
                JOIN sys.tables AS tables ON ref.referenced_object_id = tables.object_id
                JOIN sys.schemas AS schemas ON tables.schema_id = schemas.schema_id
                JOIN sys.columns AS columns ON
                    ref.referenced_column_id = columns.column_id
                    AND tables.object_id = columns.object_id
                WHERE
                    ref.parent_object_id = col.object_id
                    AND ref.parent_column_id = col.column_id
                ORDER BY
                    schemas.name,
                    tables.name,
                    columns.column_id
                FOR JSON PATH
            ) AS "pk_references"
        FROM sys.columns AS col
        JOIN sys.types AS column_types ON col.user_type_id = column_types.user_type_id
        WHERE col.object_id = tables.object_id
        ORDER BY col.column_id
        FOR JSON PATH
    ) AS columns
FROM sys.schemas AS schemas
JOIN sys.tables AS tables ON schemas.schema_id = tables.schema_id
ORDER BY
    schemas.name,
    tables.name
FOR JSON AUTO;
