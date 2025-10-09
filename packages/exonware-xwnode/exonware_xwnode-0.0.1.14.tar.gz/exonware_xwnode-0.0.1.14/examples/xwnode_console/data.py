#!/usr/bin/env python3
"""
Test Data Generation for XWQuery Console

Generates 5 realistic collections for testing XWQuery operations.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


def set_seed(seed: int = 42):
    """Set random seed for reproducible data."""
    random.seed(seed)


def generate_users(count: int = 50) -> List[Dict[str, Any]]:
    """
    Generate sample users.
    
    Returns 50 users with varied demographics and roles.
    """
    first_names = [
        "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
        "Ivy", "Jack", "Kate", "Liam", "Mia", "Noah", "Olivia", "Peter",
        "Quinn", "Rachel", "Sam", "Tara", "Uma", "Victor", "Wendy", "Xavier",
        "Yara", "Zack", "Anna", "Ben", "Chloe", "David"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
    ]
    
    cities = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
        "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
        "Austin", "Jacksonville", "San Francisco", "Columbus", "Indianapolis",
        "Seattle", "Denver", "Boston", "Portland", "Miami"
    ]
    
    roles = ["admin", "user", "moderator", "viewer", "editor"]
    
    users = []
    for i in range(count):
        user_id = i + 1
        users.append({
            "id": user_id,
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "email": f"user{user_id}@example.com",
            "age": random.randint(18, 65),
            "city": random.choice(cities),
            "role": random.choice(roles),
            "active": random.choice([True, True, True, False]),  # 75% active
            "joined_date": (datetime.now() - timedelta(days=random.randint(1, 730))).strftime("%Y-%m-%d"),
            "last_login": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        })
    
    return users


def generate_products(count: int = 100) -> List[Dict[str, Any]]:
    """
    Generate sample products.
    
    Returns 100 products across different categories.
    """
    categories = {
        "Electronics": ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones", "Webcam", "Speaker"],
        "Books": ["Novel", "Textbook", "Comic", "Magazine", "Encyclopedia", "Dictionary"],
        "Clothing": ["Shirt", "Pants", "Dress", "Shoes", "Hat", "Jacket", "Socks"],
        "Home": ["Lamp", "Chair", "Table", "Sofa", "Bed", "Cabinet", "Mirror"],
        "Sports": ["Ball", "Racket", "Gloves", "Shoes", "Bag", "Helmet"]
    }
    
    products = []
    product_id = 1
    
    for category, items in categories.items():
        items_to_generate = int(count * len(items) / sum(len(v) for v in categories.values()))
        
        for _ in range(items_to_generate):
            item_name = random.choice(items)
            products.append({
                "id": product_id,
                "name": f"{item_name} {random.choice(['Pro', 'Plus', 'Max', 'Ultra', 'Premium', ''])}".strip(),
                "category": category,
                "price": round(random.uniform(10, 1000), 2),
                "stock": random.randint(0, 500),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "brand": f"Brand{random.randint(1, 20)}",
                "available": random.choice([True, True, True, False])
            })
            product_id += 1
    
    # Fill remaining to reach count
    while len(products) < count:
        category = random.choice(list(categories.keys()))
        item_name = random.choice(categories[category])
        products.append({
            "id": product_id,
            "name": f"{item_name} {random.choice(['Lite', 'Basic', 'Standard'])}",
            "category": category,
            "price": round(random.uniform(10, 1000), 2),
            "stock": random.randint(0, 500),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "brand": f"Brand{random.randint(1, 20)}",
            "available": random.choice([True, True, True, False])
        })
        product_id += 1
    
    return products[:count]


def generate_orders(count: int = 200, user_count: int = 50, product_count: int = 100) -> List[Dict[str, Any]]:
    """
    Generate sample orders.
    
    Returns 200 orders linking users and products.
    """
    orders = []
    
    for i in range(count):
        order_id = i + 1
        user_id = random.randint(1, user_count)
        product_id = random.randint(1, product_count)
        quantity = random.randint(1, 5)
        unit_price = round(random.uniform(10, 1000), 2)
        total = round(unit_price * quantity, 2)
        
        orders.append({
            "id": order_id,
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "total": total,
            "status": random.choice(["pending", "shipped", "delivered", "cancelled"]),
            "date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "payment_method": random.choice(["credit_card", "paypal", "bank_transfer"])
        })
    
    return orders


def generate_posts(count: int = 30, user_count: int = 50) -> List[Dict[str, Any]]:
    """
    Generate sample blog posts.
    
    Returns 30 blog posts with tags and metrics.
    """
    titles = [
        "Introduction to XWNode",
        "Getting Started with XWQuery",
        "Advanced Data Structures",
        "Performance Optimization Tips",
        "Query Language Best Practices",
        "Building Scalable Applications",
        "Data Modeling Strategies",
        "Real-time Analytics",
        "Microservices Architecture",
        "API Design Patterns"
    ]
    
    tags_pool = [
        "tech", "tutorial", "guide", "advanced", "beginner",
        "performance", "architecture", "design", "best-practices",
        "nodejs", "python", "database", "api", "cloud"
    ]
    
    posts = []
    
    for i in range(count):
        post_id = i + 1
        title = random.choice(titles)
        
        posts.append({
            "id": post_id,
            "author_id": random.randint(1, user_count),
            "title": f"{title} - Part {random.randint(1, 5)}",
            "content": f"This is the content of post {post_id}. Lorem ipsum dolor sit amet...",
            "tags": random.sample(tags_pool, k=random.randint(2, 5)),
            "views": random.randint(100, 10000),
            "likes": random.randint(10, 500),
            "comments": random.randint(0, 100),
            "published": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
            "status": random.choice(["draft", "published", "archived"])
        })
    
    return posts


def generate_events(count: int = 500, user_count: int = 50) -> List[Dict[str, Any]]:
    """
    Generate sample analytics events.
    
    Returns 500 analytics events for tracking.
    """
    event_types = [
        "page_view", "click", "scroll", "form_submit",
        "button_click", "link_click", "video_play", "download"
    ]
    
    pages = [
        "/home", "/products", "/about", "/contact", "/blog",
        "/pricing", "/features", "/docs", "/support", "/login"
    ]
    
    events = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        event_id = i + 1
        event_time = base_time + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        events.append({
            "id": event_id,
            "event_type": random.choice(event_types),
            "user_id": random.randint(1, user_count),
            "page": random.choice(pages),
            "element": f"element_{random.randint(1, 100)}",
            "timestamp": event_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "session_id": f"session_{random.randint(1, 1000)}",
            "device": random.choice(["desktop", "mobile", "tablet"]),
            "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"])
        })
    
    # Sort by timestamp
    events.sort(key=lambda x: x["timestamp"])
    
    return events


def load_all_collections(seed: int = 42) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load all 5 collections with sample data.
    
    Args:
        seed: Random seed for reproducible data
    
    Returns:
        Dictionary with all collections
    """
    set_seed(seed)
    
    return {
        "users": generate_users(50),
        "products": generate_products(100),
        "orders": generate_orders(200, 50, 100),
        "posts": generate_posts(30, 50),
        "events": generate_events(500, 50)
    }


def get_collection_stats(collections: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
    """Get statistics about loaded collections."""
    return {name: len(data) for name, data in collections.items()}

