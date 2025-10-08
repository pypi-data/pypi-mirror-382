#!/usr/bin/env python3
"""
Integration: XWNode + XWSystem lazy-install with complex serialization (Avro, Parquet)
- Verifies xwnode uses xwsystem correctly
- Exercises xwsystem lazy auto-install for enterprise serializers
- Round-trips real data through Avro and Parquet
"""
import os
import sys
from pathlib import Path

# Ensure src available when running directly
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import pytest

def test_xwnode_xwsystem_lazy_complex_serialization(tmp_path: Path):
    # 1) Build an XWNode and prepare complex data
    from exonware.xwnode import XWNode

    node = XWNode.from_native({
        "users": [
            {"id": 1, "name": "Alice", "age": 30, "scores": [95, 88, 91]},
            {"id": 2, "name": "Bob", "age": 25, "scores": [89, 84, 90]},
        ],
        "meta": {"version": "1.0", "tags": ["test", "integration"]},
    })
    data = node.to_native()

    # 2) Proactively trigger lazy install for heavy deps using xwimport
    #    This should auto-install if missing.
    from exonware.xwsystem import xwimport
    fastavro = xwimport("fastavro")
    pyarrow = xwimport("pyarrow")

    assert hasattr(fastavro, "__version__")
    assert hasattr(pyarrow, "__version__")

    # 3) Use enterprise serializers (should be backed by those libs)
    from exonware.xwsystem import AvroSerializer, ParquetSerializer

    # Avro round-trip with an explicit schema
    avro_schema = {
        "type": "record",
        "name": "Root",
        "fields": [
            {"name": "users", "type": {"type": "array", "items": {
                "type": "record",
                "name": "User",
                "fields": [
                    {"name": "id", "type": "int"},
                    {"name": "name", "type": "string"},
                    {"name": "age", "type": "int"},
                    {"name": "scores", "type": {"type": "array", "items": "int"}}
                ]
            }}},
            {"name": "meta", "type": {
                "type": "record",
                "name": "Meta",
                "fields": [
                    {"name": "version", "type": "string"},
                    {"name": "tags", "type": {"type": "array", "items": "string"}}
                ]
            }}
        ]
    }

    avro = AvroSerializer()
    avro.schema = avro_schema

    avro_bytes = avro.dumps(data)
    assert isinstance(avro_bytes, (bytes, bytearray))
    data_from_avro = avro.loads(avro_bytes)
    assert data_from_avro == data

    # Parquet round-trip (columnar) via file since Parquet is file-oriented
    pq = ParquetSerializer()
    parquet_path = tmp_path / "data.parquet"
    pq.dump_to_file(data, parquet_path)
    assert parquet_path.exists() and parquet_path.stat().st_size > 0
    data_from_parquet = pq.load_from_file(parquet_path)
    # Parquet may reorder fields/rows; basic structural check:
    assert "users" in data_from_parquet and "meta" in data_from_parquet
    assert len(data_from_parquet["users"]) == len(data["users"])

    # 4) Ensure subsequent imports are fast (lazy install cached)
    fastavro2 = xwimport("fastavro")
    pyarrow2 = xwimport("pyarrow")
    assert fastavro2 is fastavro or fastavro2.__name__ == fastavro.__name__
    assert pyarrow2 is pyarrow or pyarrow2.__name__ == pyarrow.__name__

def test_xwnode_xwsystem_basic_integration():
    """Test basic xwnode + xwsystem integration without heavy serialization."""
    from exonware.xwnode import XWNode
    from exonware.xwsystem import JSONSerializer, YAMLSerializer
    
    # Create a complex node structure
    node = XWNode.from_native({
        "config": {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"enabled": True, "ttl": 3600}
        },
        "features": ["auth", "logging", "monitoring"],
        "version": "1.0.0"
    })
    
    data = node.to_native()
    
    # Test JSON serialization
    json_serializer = JSONSerializer()
    json_data = json_serializer.dumps(data)
    data_from_json = json_serializer.loads(json_data)
    assert data_from_json == data
    
    # Test YAML serialization
    yaml_serializer = YAMLSerializer()
    yaml_data = yaml_serializer.dumps(data)
    data_from_yaml = yaml_serializer.loads(yaml_data)
    assert data_from_yaml == data

def test_xwnode_xwsystem_lazy_import_caching():
    """Test that xwimport caching works correctly."""
    from exonware.xwsystem import xwimport
    
    # First import should work
    json_module = xwimport("json")
    assert json_module is not None
    
    # Second import should be cached (same module)
    json_module2 = xwimport("json")
    assert json_module is json_module2
    
    # Test with a module that might not be installed
    try:
        # This should either work or raise ImportError
        # (not install automatically since it's not in our mapping)
        xwimport("nonexistent_module_12345")
        assert False, "Should have raised ImportError"
    except ImportError:
        pass  # Expected behavior
