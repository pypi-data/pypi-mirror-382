WITH orders AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),

customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),

products AS (
    SELECT * FROM {{ ref('dim_product') }}
),

final AS (
    SELECT
        o.id AS order_id,
        o.customer_id,
        o.product_id,
        c.first_name,
        c.last_name,
        p.product_name,
        p.category,
        o.order_date,
        o.amount
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN products p ON o.product_id = p.product_id
)

SELECT * FROM final