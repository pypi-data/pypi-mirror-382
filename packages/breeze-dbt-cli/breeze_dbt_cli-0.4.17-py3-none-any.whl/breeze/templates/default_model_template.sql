-- This is the default template for models

WITH 

    model AS (
        SELECT *
        FROM {{ ref('model_name') }}
    ),

    source AS (
        SELECT *
        FROM {{ source('schema_name', 'source_name') }}
    )

SELECT * FROM source
