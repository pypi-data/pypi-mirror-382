# XWQuery Interactive Console

An interactive console for testing and demonstrating all 50 XWQuery operations with realistic sample data.

## Features

- **Interactive Testing** - Test all 50 XWQuery operations interactively
- **5 Sample Collections** - Pre-loaded with realistic data (users, products, orders, posts, events)
- **Example Queries** - Built-in examples for all operation categories
- **Formatted Output** - Results displayed in nice ASCII tables
- **Help System** - Comprehensive help and command reference

## Quick Start

```bash
# From xwnode directory
cd xwnode
python examples/xwnode_console/run.py

# Or with options
python examples/xwnode_console/run.py --seed 42 --verbose
```

## Collections

The console comes pre-loaded with 5 realistic collections:

1. **users** (50 records) - User accounts with demographics
2. **products** (100 records) - Products across multiple categories  
3. **orders** (200 records) - Purchase orders linking users and products
4. **posts** (30 records) - Blog posts with tags and metrics
5. **events** (500 records) - Analytics events for tracking

## Console Commands

| Command | Description |
|---------|-------------|
| `.help` | Show help message |
| `.collections` | List all collections with counts |
| `.show <name>` | Show sample records from collection |
| `.examples [type]` | Show example queries by category |
| `.clear` | Clear the screen |
| `.history` | Show query history |
| `.random` | Get a random example query |
| `.exit` | Exit the console |

## Example Queries

### Core Operations
```sql
SELECT * FROM users WHERE age > 30
SELECT name, age FROM users
INSERT INTO users VALUES {name: 'John', age: 30}
UPDATE users SET age = 31 WHERE id = 5
DELETE FROM users WHERE active = false
```

### Filtering
```sql
SELECT * FROM products WHERE price BETWEEN 50 AND 500
SELECT * FROM users WHERE name LIKE '%Smith%'
SELECT * FROM products WHERE category IN ['Electronics', 'Books']
```

### Aggregation
```sql
SELECT COUNT(*) FROM users
SELECT AVG(price) FROM products
SELECT category, COUNT(*), AVG(price) FROM products GROUP BY category
```

### Advanced
```sql
SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id
SELECT * FROM products ORDER BY price DESC
SELECT DISTINCT city FROM users
```

## Example Session

```
╔══════════════════════════════════════════════════════════════╗
║             XWQuery Interactive Console v0.0.1               ║
║                                                              ║
║  Type .help for commands | .examples for sample queries     ║
║  Type .exit or Ctrl+C to quit                               ║
╚══════════════════════════════════════════════════════════════╝

Collections loaded:
  • users        (  50 records)
  • products     ( 100 records)
  • orders       ( 200 records)
  • posts        (  30 records)
  • events       ( 500 records)

XWQuery> SELECT * FROM users WHERE age > 30

┌────┬──────────────────┬──────────────────────┬─────┬─────────────┬──────────┐
│ id │ name             │ email                │ age │ city        │ role     │
├────┼──────────────────┼──────────────────────┼─────┼─────────────┼──────────┤
│ 2  │ Bob Johnson      │ user2@example.com    │ 35  │ Los Angeles │ user     │
│ 5  │ Charlie Williams │ user5@example.com    │ 42  │ Chicago     │ admin    │
│ ...│ ...              │ ...                  │ ... │ ...         │ ...      │
└────┴──────────────────┴──────────────────────┴─────┴─────────────┴──────────┘

Total: 15 results

Execution time: 0.003s

XWQuery> .examples aggregation

Aggregation Operations:
============================================================
1. COUNT all
   SELECT COUNT(*) FROM users

2. SUM total
   SELECT SUM(total) FROM orders

3. GROUP BY category
   SELECT category, COUNT(*) FROM products GROUP BY category

...

XWQuery> .exit

Exiting XWQuery Console. Goodbye!
```

## Data Generation

All data is generated with a random seed (default: 42) for reproducibility. You can change the seed:

```bash
python examples/xwnode_console/run.py --seed 123
```

## Implementation Notes

**Current Status:**
- ✅ Interactive console with command system
- ✅ 5 collections with realistic data
- ✅ Example queries for all 50 operations
- ✅ Formatted output and error handling
- ⏳ Mock execution (full parser integration in progress)

**Future Enhancements:**
- Full XWQuery parser integration
- Query file execution
- Result export (JSON, CSV)
- Query performance metrics
- Syntax highlighting
- Auto-completion

## Architecture

```
xwnode_console/
├── run.py             - Entry point with argument parsing
├── console.py         - Main console implementation
├── data.py            - Test data generation (5 collections)
├── utils.py           - Formatting and display utilities
├── query_examples.py  - Example queries for all operations
└── README.md          - This file
```

## Development

The console uses:
- **XWNode** - Data storage with HASH_MAP strategy
- **ExecutionEngine** - Query execution (integration in progress)
- **XWQueryScriptStrategy** - Query parsing (integration in progress)

## Testing

Great for:
- Testing new XWQuery operations
- Demonstrating XWNode capabilities
- Learning XWQuery syntax
- Quick prototyping of queries
- Integration testing

## License

Part of the eXonware xwnode library.

---

*For more information about XWQuery operations, see `docs/XWQUERY_SCRIPT.md`*

