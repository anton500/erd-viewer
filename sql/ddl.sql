SELECT
    schemas.name AS "name",
    tables.name AS "name",
    (
        SELECT
            columns.name AS "name",
            CASE
                WHEN column_types.name IN ('varchar', 'char', 'varbinary', 'binary') THEN column_types.name + '(' + IIF(columns.max_length = -1, 'max', CAST(columns.max_length AS VARCHAR(25))) + ')'
                WHEN column_types.name IN ('nvarchar', 'nchar') THEN column_types.name + '(' + IIF(columns.max_length = -1, 'max', CAST(columns.max_length / 2 AS VARCHAR(25)))+ ')'
                WHEN column_types.name IN ('decimal', 'numeric') THEN column_types.name + '(' + CAST(columns.precision AS VARCHAR(25)) + ',' + CAST(columns.scale AS VARCHAR(25)) + ')'
                WHEN column_types.name IN ('datetime2') THEN column_types.name + '(' + CAST(columns.scale AS VARCHAR(25)) + ')'
                ELSE column_types.name
            END AS "type",
            CASE columns.is_nullable
                WHEN 0 THEN 'NOT NULL'
                WHEN 1 THEN 'NULL'
            END AS "null",
            CASE
                WHEN i_columns.column_id IS NOT NULL THEN 'PK'
                WHEN fk_columns.parent_column_id IS NOT NULL THEN 'FK'
                ELSE ''
            END AS "key"
        FROM sys.columns AS columns
        JOIN sys.types AS column_types ON columns.user_type_id = column_types.user_type_id
        LEFT JOIN
            sys.index_columns AS i_columns
            JOIN sys.indexes AS indexes ON
                i_columns.object_id = indexes.object_id
                AND i_columns.index_id = indexes.index_id
                AND indexes.is_primary_key = 1
        ON columns.object_id = i_columns.object_id AND columns.column_id = i_columns.column_id
        LEFT JOIN sys.foreign_key_columns AS fk_columns ON
            columns.object_id = fk_columns.parent_object_id
            AND columns.column_id = fk_columns.parent_column_id
        WHERE columns.object_id = tables.object_id
        ORDER BY columns.column_id
        FOR JSON PATH
    ) AS columns
FROM sys.schemas AS schemas
JOIN sys.tables AS tables ON schemas.schema_id = tables.schema_id
WHERE tables.type = 'U'
ORDER BY
    schemas.name,
    tables.name
FOR JSON AUTO, ROOT('schemas');