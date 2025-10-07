WITH source AS (
    SELECT * FROM {{ source('raw', 'products') }}
),

renamed AS (
    SELECT
        id AS product_id,
        name AS product_name,
        category,
        price,
        created_at
    FROM source
)

SELECT * FROM renamed
