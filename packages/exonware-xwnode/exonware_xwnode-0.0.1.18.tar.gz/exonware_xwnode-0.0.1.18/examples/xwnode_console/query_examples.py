#!/usr/bin/env python3
"""
Example XWQuery Queries

Examples for all 50 operations organized by category.
"""

from typing import Dict, List

EXAMPLES = {
    "core": {
        "description": "Core CRUD Operations",
        "queries": [
            ("SELECT all users", "SELECT * FROM users"),
            ("SELECT specific fields", "SELECT name, age, city FROM users"),
            ("SELECT with WHERE", "SELECT * FROM users WHERE age > 30"),
            ("INSERT new record", "INSERT INTO users VALUES {name: 'John Doe', age: 30, city: 'Boston'}"),
            ("UPDATE records", "UPDATE users SET age = 36 WHERE id = 2"),
            ("DELETE records", "DELETE FROM users WHERE active = false"),
            ("CREATE collection", "CREATE COLLECTION new_collection"),
            ("DROP collection", "DROP COLLECTION IF EXISTS old_collection"),
        ]
    },
    
    "filtering": {
        "description": "Filtering Operations",
        "queries": [
            ("WHERE clause", "SELECT * FROM products WHERE price > 100"),
            ("FILTER operation", "SELECT * FROM products FILTER stock > 0 AND available = true"),
            ("LIKE pattern matching", "SELECT * FROM users WHERE name LIKE '%Smith%'"),
            ("IN membership", "SELECT * FROM products WHERE category IN ['Electronics', 'Books']"),
            ("HAS property check", "SELECT * FROM posts WHERE HAS tags"),
            ("BETWEEN range", "SELECT * FROM products WHERE price BETWEEN 50 AND 500"),
            ("RANGE query", "SELECT * FROM products WHERE id RANGE 10 TO 50"),
            ("TERM search", "SELECT * FROM posts WHERE title TERM 'XWNode'"),
            ("OPTIONAL matching", "SELECT * FROM users OPTIONAL role = 'admin'"),
            ("VALUES inline data", "VALUES {id: 1, name: 'Test'}, {id: 2, name: 'Test2'}"),
        ]
    },
    
    "aggregation": {
        "description": "Aggregation Operations",
        "queries": [
            ("COUNT all", "SELECT COUNT(*) FROM users"),
            ("COUNT with condition", "SELECT COUNT(*) FROM users WHERE age > 30"),
            ("SUM total", "SELECT SUM(total) FROM orders"),
            ("AVG average", "SELECT AVG(price) FROM products"),
            ("MIN/MAX values", "SELECT MIN(price), MAX(price) FROM products"),
            ("DISTINCT values", "SELECT DISTINCT city FROM users"),
            ("GROUP BY category", "SELECT category, COUNT(*) FROM products GROUP BY category"),
            ("GROUP BY with aggregate", "SELECT category, AVG(price), COUNT(*) FROM products GROUP BY category"),
            ("HAVING filter groups", "SELECT category, COUNT(*) FROM products GROUP BY category HAVING COUNT(*) > 10"),
            ("SUMMARIZE data", "SELECT SUMMARIZE users BY city"),
        ]
    },
    
    "ordering": {
        "description": "Ordering Operations",
        "queries": [
            ("ORDER BY ascending", "SELECT * FROM products ORDER BY price ASC"),
            ("ORDER BY descending", "SELECT * FROM products ORDER BY price DESC"),
            ("ORDER BY multiple", "SELECT * FROM products ORDER BY category, price"),
            ("GROUP BY with ORDER", "SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY COUNT(*) DESC"),
        ]
    },
    
    "graph": {
        "description": "Graph Operations",
        "queries": [
            ("MATCH pattern", "MATCH (u:User)-[:ORDERED]->(p:Product) RETURN u.name, p.name"),
            ("PATH finding", "PATH FROM users.1 TO users.10 THROUGH orders"),
            ("OUT traversal", "SELECT * FROM users OUT orders"),
            ("IN traversal", "SELECT * FROM products IN orders"),
            ("RETURN specific fields", "MATCH (u:User) RETURN u.name, u.email"),
        ]
    },
    
    "projection": {
        "description": "Projection Operations",
        "queries": [
            ("PROJECT fields", "SELECT * FROM users PROJECT name, age, city"),
            ("EXTEND with computed", "SELECT * FROM products EXTEND discount = price * 0.1"),
            ("PROJECT renamed", "SELECT * FROM users PROJECT fullname = name, years = age"),
        ]
    },
    
    "array": {
        "description": "Array Operations",
        "queries": [
            ("SLICING range", "SELECT * FROM users SLICING 0:10"),
            ("SLICING with step", "SELECT * FROM users SLICING 0:50:5"),
            ("INDEXING specific", "SELECT * FROM users INDEXING [0, 5, 10, 15]"),
        ]
    },
    
    "data": {
        "description": "Data Operations",
        "queries": [
            ("LOAD data", "LOAD DATA FROM 'users.json' INTO users"),
            ("STORE data", "STORE users TO 'backup_users.json'"),
            ("MERGE upsert", "MERGE INTO users VALUES {id: 1, name: 'Updated'}"),
            ("ALTER structure", "ALTER COLLECTION users ADD COLUMN status STRING"),
        ]
    },
    
    "advanced": {
        "description": "Advanced Operations",
        "queries": [
            ("JOIN tables", "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"),
            ("UNION combine", "SELECT name FROM users UNION SELECT name FROM authors"),
            ("WITH CTE", "WITH top_users AS (SELECT * FROM users WHERE age > 40) SELECT * FROM top_users"),
            ("AGGREGATE window", "SELECT user_id, SUM(total) OVER (PARTITION BY user_id) FROM orders"),
            ("FOREACH iteration", "FOREACH user IN users DO UPDATE user SET processed = true"),
            ("LET variable", "LET max_price = (SELECT MAX(price) FROM products) SELECT * FROM products WHERE price = max_price"),
            ("FOR loop", "FOR i IN RANGE(1, 10) DO INSERT INTO numbers VALUES {value: i}"),
            ("WINDOW function", "SELECT *, AVG(price) OVER (ORDER BY date ROWS 3 PRECEDING) FROM products"),
            ("DESCRIBE schema", "DESCRIBE users"),
            ("CONSTRUCT new data", "CONSTRUCT {user: name, email: email} FROM users"),
            ("ASK boolean", "ASK EXISTS(SELECT * FROM users WHERE role = 'admin')"),
            ("SUBSCRIBE changes", "SUBSCRIBE TO users WHERE role = 'admin'"),
            ("SUBSCRIPTION manage", "SUBSCRIPTION sub1 ON users"),
            ("MUTATION transaction", "MUTATION BEGIN; UPDATE users SET active = true; COMMIT;"),
            ("PIPE operations", "SELECT * FROM users | FILTER age > 30 | ORDER BY age"),
            ("OPTIONS metadata", "SELECT * FROM users OPTIONS {timeout: 5000, limit: 100}"),
        ]
    },
    
    "mixed": {
        "description": "Complex Mixed Operations",
        "queries": [
            ("Join with aggregation", 
             "SELECT u.city, COUNT(*), AVG(o.total) FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.city"),
            ("Subquery",
             "SELECT * FROM products WHERE price > (SELECT AVG(price) FROM products)"),
            ("Multiple conditions",
             "SELECT * FROM products WHERE category = 'Electronics' AND price < 500 AND stock > 0"),
            ("Complex aggregation",
             "SELECT category, AVG(price) as avg_price, COUNT(*) as count, SUM(stock) as total_stock FROM products GROUP BY category HAVING count > 5 ORDER BY avg_price DESC"),
        ]
    }
}


def get_examples(category: str = "all") -> List[tuple]:
    """
    Get example queries by category.
    
    Args:
        category: Category name or 'all' for all examples
    
    Returns:
        List of (description, query) tuples
    """
    if category == "all":
        all_examples = []
        for cat_data in EXAMPLES.values():
            all_examples.extend(cat_data["queries"])
        return all_examples
    
    if category in EXAMPLES:
        return EXAMPLES[category]["queries"]
    
    return []


def get_categories() -> List[str]:
    """Get list of available categories."""
    return list(EXAMPLES.keys())


def print_examples(category: str = "all"):
    """Print examples for a category."""
    if category not in EXAMPLES and category != "all":
        print(f"Unknown category: {category}")
        print(f"Available categories: {', '.join(get_categories())}")
        return
    
    if category == "all":
        for cat_name, cat_data in EXAMPLES.items():
            print(f"\n{cat_data['description']}:")
            print("=" * 60)
            for i, (desc, query) in enumerate(cat_data["queries"], 1):
                print(f"{i}. {desc}")
                print(f"   {query}")
                print()
    else:
        cat_data = EXAMPLES[category]
        print(f"\n{cat_data['description']}:")
        print("=" * 60)
        for i, (desc, query) in enumerate(cat_data["queries"], 1):
            print(f"{i}. {desc}")
            print(f"   {query}")
            print()


def get_random_example() -> tuple:
    """Get a random example query."""
    import random
    category = random.choice(list(EXAMPLES.keys()))
    return random.choice(EXAMPLES[category]["queries"])

