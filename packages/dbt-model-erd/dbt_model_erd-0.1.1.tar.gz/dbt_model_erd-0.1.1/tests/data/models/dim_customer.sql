WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
),

renamed AS (
    SELECT
        id AS customer_id,
        first_name,
        last_name,
        email,
        created_at
    FROM source
)

SELECT * FROM renamed