# 🚀 Quick Start Guide

## Installation

### From PyPI (after publishing)

```bash
pip install dbt-model-erd
```

### For Development

```bash
git clone https://github.com/entechlog/dbt-model-erd.git
cd dbt-model-erd
python setup.py install --user
```

---

## Basic Usage

### 1. Prepare Your dbt Project

Ensure your dbt project has:
- SQL files with `{{ ref('...') }}` statements
- YAML schema files with column definitions

**Example structure:**
```
your-dbt-project/
├── models/
│   ├── dim/
│   │   ├── dim_customer.sql
│   │   └── schema.yml
│   └── fact/
│       ├── fact_orders.sql
│       └── schema.yml
```

### 2. Run dbt-model-erd

```bash
cd your-dbt-project
python -m dbt_erd --model-path models/fact
```

### 3. View Results

Open the generated HTML file:
```
your-dbt-project/assets/img/fact/<model_name>_model.html
```

---

## Example: Create Test Project

### Directory Structure

```bash
mkdir -p test-project/models/{dim,fact}
cd test-project
```

### Create Dimension Table

**models/dim/dim_customer.sql:**
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

**models/dim/schema.yml:**
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

### Create Fact Table

**models/fact/fact_orders.sql:**
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

**models/fact/schema.yml:**
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
      - name: order_date
      - name: amount
```

### Generate Diagram

```bash
python -m dbt_erd --model-path models/fact --verbose
```

### Expected Output

```
Collecting column information from YAML files...
Found 2 YAML files to scan for column information
Loaded column information for 2 models

Processing fact_orders...
Found 1 dimension references: dim_customer
Generated MMD: assets/img/fact/fact_orders_model.mmd
Generated HTML: assets/img/fact/fact_orders_model.html
Updated model description in models/fact/schema.yml
```

---

## Advanced Usage

### Custom Configuration

Generate default config:
```bash
python -m dbt_erd --output-config my_config.yml
```

Customize and use:
```bash
python -m dbt_erd --model-path models/fact --config my_config.yml
```

### Parallel Processing

For large projects:
```bash
python -m dbt_erd --model-path models/fact --parallel
```

### Verbose Output

For debugging:
```bash
python -m dbt_erd --model-path models/fact --verbose
```

---

## Viewing Diagrams

### In Browser
Open the generated HTML file directly in any browser.

### In dbt Docs
The diagram link is automatically added to your model's description:
```bash
dbt docs generate
dbt docs serve
```

Navigate to your model and click the diagram link.

---

## Troubleshooting

### "No SQL files found"
- Check that `--model-path` points to directory with SQL files
- Verify you're running from project root

### "No dimension references found"
- Ensure your SQL has `{{ ref('dim_*') }}` statements
- Check naming patterns match config (default: `dim_` prefix)
- Use `--verbose` to see what's being detected

### "YAML file not found"
- Ensure schema.yml exists in same directory as SQL files
- Check file is named `schema.yml` or matches `yaml_extension` config

### Diagram not rendering
- Check browser console for JavaScript errors
- Verify HTML file isn't blocked by corporate firewall
- Try opening in different browser

---

## Configuration Options

See `examples/basic_config.yml` and `examples/advanced_config.yml` for full options.

**Key settings:**
- `naming.dimension_patterns` - How to identify dimension tables
- `naming.fact_patterns` - How to identify fact tables
- `visualization.max_dimensions` - Max dimensions to show per fact
- `visualization.show_columns` - Whether to show columns
- `mermaid.theme` - Diagram theme (default, neutral, forest, dark)
- `mermaid.direction` - Layout direction (LR or TB)

---

## Next Steps

- Read full documentation: [README.md](README.md)
- Contribute: [CONTRIBUTING.md](CONTRIBUTING.md)
- Report issues: [GitHub Issues](https://github.com/entechlog/dbt-model-erd/issues)
