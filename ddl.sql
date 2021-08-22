SELECT
    tables.TABLE_CATALOG,
    tables.TABLE_SCHEMA,
    tables.TABLE_NAME,
    columns.COLUMN_NAME,
    columns.DATA_TYPE,
    CASE columns.IS_NULLABLE
        WHEN 'YES' THEN 'NULL'
        WHEN 'NO' THEN 'NOT NULL'
    END AS IS_NULLABLE
FROM INFORMATION_SCHEMA.TABLES AS tables
JOIN INFORMATION_SCHEMA.COLUMNS AS columns ON 
    tables.TABLE_CATALOG = columns.TABLE_CATALOG
    AND tables.TABLE_SCHEMA = columns.TABLE_SCHEMA
    AND tables.TABLE_NAME = columns.TABLE_NAME
WHERE 
    tables.TABLE_CATALOG = 'portal'
    AND tables.TABLE_SCHEMA = 'dlfe'
    AND tables.TABLE_TYPE = 'BASE TABLE'
ORDER BY
    tables.TABLE_CATALOG,
    tables.TABLE_SCHEMA,
    tables.TABLE_NAME,
    columns.ORDINAL_POSITION;