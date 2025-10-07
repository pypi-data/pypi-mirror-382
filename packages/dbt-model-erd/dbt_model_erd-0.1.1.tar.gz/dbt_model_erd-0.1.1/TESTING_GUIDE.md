# Testing dbt-model-erd Locally

## Step 1: Install in Development Mode

```bash
# Install in editable mode so changes are immediately reflected
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Step 2: Create a Test dbt Project

Create a minimal test project structure:

```bash
mkdir -p ~/test-dbt-erd/models/fact
mkdir -p ~/test-dbt-erd/models/dim
cd ~/test-dbt-erd
```

### Create dimension table: `models/dim/dim_customer.sql`

```sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
),
renamed AS (
    SELECT
        id AS customer_id,
        first_name,
        last_name,
        email
    FROM source
)
SELECT * FROM renamed
```

### Create dimension schema: `models/dim/schema.yml`

```yaml
version: 2
models:
  - name: dim_customer
    description: Customer dimension
    columns:
      - name: customer_id
        description: Primary key
        tests: [unique, not_null]
      - name: first_name
      - name: last_name
      - name: email
```

### Create fact table: `models/fact/fact_orders.sql`

```sql
WITH orders AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),
customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),
final AS (
    SELECT
        o.id AS order_id,
        o.customer_id,
        c.first_name,
        o.order_date,
        o.amount
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
)
SELECT * FROM final
```

### Create fact schema: `models/fact/schema.yml`

```yaml
version: 2
models:
  - name: fact_orders
    description: Order facts
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: customer_id
        tests: [not_null]
      - name: first_name
      - name: order_date
      - name: amount
```

## Step 3: Run dbt-erd

```bash
cd ~/test-dbt-erd

# Generate diagrams
python -m dbt_erd --model-path models/fact --verbose

# Or if installed globally
dbt-erd --model-path models/fact
```

## Step 4: Check Output

1. **Check console output** - Should show processing messages
2. **Check assets directory** - Should have `assets/img/fact/` with `.mmd` and `.html` files
3. **Open HTML file** - Open `assets/img/fact/fact_orders_model.html` in browser to see diagram
4. **Check YAML** - Verify `models/fact/schema.yml` has diagram link added

## Expected Output

```
Collecting column information from YAML files...
Found 2 YAML files to scan for column information
Loaded 1 columns for model dim_customer from models/dim/schema.yml
Loaded column information for 1 models

Processing fact_orders...
Found 1 dimension references: dim_customer
Generated MMD: /path/to/assets/img/fact/fact_orders_model.mmd
Generated HTML: /path/to/assets/img/fact/fact_orders_model.html
Updated model description in models/fact/schema.yml
```

## Troubleshooting

**No dimension references found:**
- Check your SQL file has `{{ ref('dim_*') }}` statements
- Verify dimension naming matches config patterns (default: `dim_`)

**YAML not updated:**
- Check YAML file exists and is valid
- Ensure model name in YAML matches SQL file name

**Permission errors:**
- Make sure you have write access to the project directory
