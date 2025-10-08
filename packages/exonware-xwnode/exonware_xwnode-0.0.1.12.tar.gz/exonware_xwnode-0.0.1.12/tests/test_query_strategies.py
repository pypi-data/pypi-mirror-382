#!/usr/bin/env python3
"""
Comprehensive Query Strategy Tests

This module tests all query strategy implementations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 2, 2025
"""

import sys
import os

# Add xwnode to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from exonware.xwnode.strategies.queries.sql import SQLStrategy
from exonware.xwnode.strategies.queries.hiveql import HiveQLStrategy
from exonware.xwnode.strategies.queries.pig import PigStrategy
from exonware.xwnode.strategies.queries.cql import CQLStrategy
from exonware.xwnode.strategies.queries.n1ql import N1QLStrategy
from exonware.xwnode.strategies.queries.eql import EQLStrategy
from exonware.xwnode.strategies.queries.kql import KQLStrategy
from exonware.xwnode.strategies.queries.flux import FluxStrategy
from exonware.xwnode.strategies.queries.datalog import DatalogStrategy
from exonware.xwnode.strategies.queries.graphql import GraphQLStrategy
from exonware.xwnode.strategies.queries.sparql import SPARQLStrategy
from exonware.xwnode.strategies.queries.gremlin import GremlinStrategy
from exonware.xwnode.strategies.queries.cypher import CypherStrategy
from exonware.xwnode.strategies.queries.linq import LINQStrategy
from exonware.xwnode.strategies.queries.jsoniq import JSONiqStrategy
from exonware.xwnode.strategies.queries.jmespath import JMESPathStrategy
from exonware.xwnode.strategies.queries.xquery import XQueryStrategy
from exonware.xwnode.strategies.queries.xpath import XPathStrategy
from exonware.xwnode.strategies.queries.xml_query import XMLQueryStrategy
from exonware.xwnode.strategies.queries.json_query import JSONQueryStrategy

from exonware.xwnode.types import QueryMode, QueryTrait


def test_sql_strategy():
    """Test SQL query strategy."""
    print("Testing SQL Strategy...")
    
    # Create SQL strategy
    sql = SQLStrategy()
    
    # Test basic properties
    assert sql.get_mode() == QueryMode.SQL
    assert sql.get_traits() == QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL | QueryTrait.BATCH
    
    # Test query validation
    assert sql.validate_query("SELECT * FROM users")
    assert sql.validate_query("INSERT INTO users VALUES (1, 'John')")
    assert not sql.validate_query("invalid query")
    
    # Test query execution
    result = sql.execute("SELECT * FROM users")
    assert result["result"] == "SELECT executed"
    
    # Test structured query methods
    result = sql.select_query("users", ["name", "email"])
    assert "result" in result
    
    result = sql.insert_query("users", {"name": "John", "email": "john@example.com"})
    assert "result" in result
    
    print("✅ SQL Strategy tests passed!")


def test_hiveql_strategy():
    """Test HiveQL query strategy."""
    print("Testing HiveQL Strategy...")
    
    # Create HiveQL strategy
    hiveql = HiveQLStrategy()
    
    # Test basic properties
    assert hiveql.get_mode() == QueryMode.HIVEQL
    assert hiveql.get_traits() == QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL | QueryTrait.BATCH
    
    # Test query validation
    assert hiveql.validate_query("SELECT * FROM table1")
    assert hiveql.validate_query("LOAD DATA INPATH '/path' INTO TABLE table1")
    assert not hiveql.validate_query("invalid query")
    
    # Test query execution
    result = hiveql.execute("SELECT * FROM table1")
    assert result["result"] == "HiveQL SELECT executed"
    
    # Test query plan
    plan = hiveql.get_query_plan("SELECT * FROM table1 JOIN table2")
    assert plan["mapreduce_jobs"] >= 2
    
    print("✅ HiveQL Strategy tests passed!")


def test_graphql_strategy():
    """Test GraphQL query strategy."""
    print("Testing GraphQL Strategy...")
    
    # Create GraphQL strategy
    graphql = GraphQLStrategy()
    
    # Test basic properties
    assert graphql.get_mode() == QueryMode.GRAPHQL
    assert graphql.get_traits() == QueryTrait.GRAPH | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    # Test query validation
    assert graphql.validate_query("query { user { name email } }")
    assert graphql.validate_query("mutation { createUser(name: \"John\") }")
    assert not graphql.validate_query("invalid query")
    
    # Test query execution
    result = graphql.execute("query { user { name } }")
    assert result["result"] == "GraphQL query executed"
    
    # Test graph query methods
    result = graphql.path_query("user1", "user2")
    assert "result" in result
    
    result = graphql.neighbor_query("user1")
    assert "result" in result
    
    print("✅ GraphQL Strategy tests passed!")


def test_sparql_strategy():
    """Test SPARQL query strategy."""
    print("Testing SPARQL Strategy...")
    
    # Create SPARQL strategy
    sparql = SPARQLStrategy()
    
    # Test basic properties
    assert sparql.get_mode() == QueryMode.SPARQL
    assert sparql.get_traits() == QueryTrait.GRAPH | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    # Test query validation
    assert sparql.validate_query("SELECT ?name WHERE { ?person foaf:name ?name }")
    assert sparql.validate_query("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }")
    assert not sparql.validate_query("invalid query")
    
    # Test query execution
    result = sparql.execute("SELECT ?name WHERE { ?person foaf:name ?name }")
    assert result["result"] == "SPARQL SELECT executed"
    
    # Test graph query methods
    result = sparql.path_query("http://example.org/person1", "http://example.org/person2")
    assert "result" in result
    
    print("✅ SPARQL Strategy tests passed!")


def test_linq_strategy():
    """Test LINQ query strategy."""
    print("Testing LINQ Strategy...")
    
    # Create LINQ strategy
    linq = LINQStrategy()
    
    # Test basic properties
    assert linq.get_mode() == QueryMode.LINQ
    assert linq.get_traits() == QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    # Test query validation
    assert linq.validate_query("from user in users where user.Age > 18 select user")
    assert linq.validate_query("users.Where(u => u.Age > 18).Select(u => u.Name)")
    assert not linq.validate_query("invalid query")
    
    # Test query execution
    result = linq.execute("from user in users select user")
    assert result["result"] == "LINQ query syntax executed"
    
    # Test document query methods
    result = linq.filter_query("user.Age > 18")
    assert "result" in result
    
    result = linq.projection_query(["Name", "Email"])
    assert "result" in result
    
    print("✅ LINQ Strategy tests passed!")


def test_jsoniq_strategy():
    """Test JSONiq query strategy."""
    print("Testing JSONiq Strategy...")
    
    # Create JSONiq strategy
    jsoniq = JSONiqStrategy()
    
    # Test basic properties
    assert jsoniq.get_mode() == QueryMode.JSONIQ
    assert jsoniq.get_traits() == QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    # Test query validation
    assert jsoniq.validate_query("for $user in collection() where $user.age > 18 return $user")
    assert jsoniq.validate_query("$users.name")
    assert not jsoniq.validate_query("invalid query")
    
    # Test query execution
    result = jsoniq.execute("for $user in collection() return $user")
    assert result["result"] == "JSONiq FLWOR executed"
    
    # Test document query methods
    result = jsoniq.path_query("users.name")
    assert "result" in result
    
    print("✅ JSONiq Strategy tests passed!")


def test_jmespath_strategy():
    """Test JMESPath query strategy."""
    print("Testing JMESPath Strategy...")
    
    # Create JMESPath strategy
    jmespath = JMESPathStrategy()
    
    # Test basic properties
    assert jmespath.get_mode() == QueryMode.JMESPATH
    assert jmespath.get_traits() == QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    # Test query validation
    assert jmespath.validate_query("users[?age > `18`].name")
    assert jmespath.validate_query("sort_by(users, &age)")
    assert not jmespath.validate_query("invalid query")
    
    # Test query execution
    result = jmespath.execute("users[?age > `18`]")
    assert result["result"] == "JMESPath filter executed"
    
    # Test document query methods
    result = jmespath.filter_query("age > `18`")
    assert "result" in result
    
    print("✅ JMESPath Strategy tests passed!")


def test_xquery_strategy():
    """Test XQuery query strategy."""
    print("Testing XQuery Strategy...")
    
    # Create XQuery strategy
    xquery = XQueryStrategy()
    
    # Test basic properties
    assert xquery.get_mode() == QueryMode.XQUERY
    assert xquery.get_traits() == QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    # Test query validation
    assert xquery.validate_query("for $user in doc()//user where $user/age > 18 return $user")
    assert xquery.validate_query("doc()//user[@id='1']")
    assert not xquery.validate_query("invalid query")
    
    # Test query execution
    result = xquery.execute("for $user in doc()//user return $user")
    assert result["result"] == "XQuery FLWOR executed"
    
    # Test document query methods
    result = xquery.path_query("users/user")
    assert "result" in result
    
    print("✅ XQuery Strategy tests passed!")


def test_xpath_strategy():
    """Test XPath query strategy."""
    print("Testing XPath Strategy...")
    
    # Create XPath strategy
    xpath = XPathStrategy()
    
    # Test basic properties
    assert xpath.get_mode() == QueryMode.XPATH
    assert xpath.get_traits() == QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    # Test query validation
    assert xpath.validate_query("//user[@age > 18]")
    assert xpath.validate_query("/users/user[1]")
    assert not xpath.validate_query("invalid query")
    
    # Test query execution
    result = xpath.execute("//user")
    assert result["result"] == "XPath location path executed"
    
    # Test document query methods
    result = xpath.path_query("users/user")
    assert "result" in result
    
    print("✅ XPath Strategy tests passed!")


def test_pig_strategy():
    """Test Pig query strategy."""
    print("Testing Pig Strategy...")
    pig = PigStrategy()
    assert pig.get_mode() == QueryMode.PIG
    assert pig.validate_query("LOAD data FROM 'file'")
    result = pig.execute("LOAD data FROM 'file'")
    assert "result" in result
    print("✅ Pig Strategy tests passed!")

def test_cql_strategy():
    """Test CQL query strategy."""
    print("Testing CQL Strategy...")
    cql = CQLStrategy()
    assert cql.get_mode() == QueryMode.CQL
    assert cql.validate_query("SELECT * FROM table")
    result = cql.execute("SELECT * FROM table")
    assert "result" in result
    print("✅ CQL Strategy tests passed!")

def test_n1ql_strategy():
    """Test N1QL query strategy."""
    print("Testing N1QL Strategy...")
    n1ql = N1QLStrategy()
    assert n1ql.get_mode() == QueryMode.N1QL
    assert n1ql.validate_query("SELECT * FROM bucket")
    result = n1ql.execute("SELECT * FROM bucket")
    assert "result" in result
    print("✅ N1QL Strategy tests passed!")

def test_eql_strategy():
    """Test EQL query strategy."""
    print("Testing EQL Strategy...")
    eql = EQLStrategy()
    assert eql.get_mode() == QueryMode.EQL
    assert eql.validate_query("SEQUENCE event")
    result = eql.execute("SEQUENCE event")
    assert "result" in result
    print("✅ EQL Strategy tests passed!")

def test_kql_strategy():
    """Test KQL query strategy."""
    print("Testing KQL Strategy...")
    kql = KQLStrategy()
    assert kql.get_mode() == QueryMode.KQL
    assert kql.validate_query("TABLE data")
    result = kql.execute("TABLE data")
    assert "result" in result
    print("✅ KQL Strategy tests passed!")

def test_flux_strategy():
    """Test Flux query strategy."""
    print("Testing Flux Strategy...")
    flux = FluxStrategy()
    assert flux.get_mode() == QueryMode.FLUX
    assert flux.validate_query("from(bucket: \"data\")")
    result = flux.execute("from(bucket: \"data\")")
    assert "result" in result
    print("✅ Flux Strategy tests passed!")

def test_datalog_strategy():
    """Test Datalog query strategy."""
    print("Testing Datalog Strategy...")
    datalog = DatalogStrategy()
    assert datalog.get_mode() == QueryMode.DATALOG
    assert datalog.validate_query("?- parent(X, Y)")
    result = datalog.execute("?- parent(X, Y)")
    assert "result" in result
    print("✅ Datalog Strategy tests passed!")

def test_gremlin_strategy():
    """Test Gremlin query strategy."""
    print("Testing Gremlin Strategy...")
    gremlin = GremlinStrategy()
    assert gremlin.get_mode() == QueryMode.GREMLIN
    assert gremlin.validate_query("g.V()")
    result = gremlin.execute("g.V()")
    assert "result" in result
    print("✅ Gremlin Strategy tests passed!")

def test_cypher_strategy():
    """Test Cypher query strategy."""
    print("Testing Cypher Strategy...")
    cypher = CypherStrategy()
    assert cypher.get_mode() == QueryMode.CYPHER
    assert cypher.validate_query("MATCH (n) RETURN n")
    result = cypher.execute("MATCH (n) RETURN n")
    assert "result" in result
    print("✅ Cypher Strategy tests passed!")

def test_xml_query_strategy():
    """Test XML Query strategy."""
    print("Testing XML Query Strategy...")
    xml_query = XMLQueryStrategy()
    assert xml_query.get_mode() == QueryMode.XML_QUERY
    assert xml_query.validate_query("//element")
    result = xml_query.execute("//element")
    assert "result" in result
    print("✅ XML Query Strategy tests passed!")

def test_json_query_strategy():
    """Test JSON Query strategy."""
    print("Testing JSON Query Strategy...")
    json_query = JSONQueryStrategy()
    assert json_query.get_mode() == QueryMode.JSON_QUERY
    assert json_query.validate_query("$.field")
    result = json_query.execute("$.field")
    assert "result" in result
    print("✅ JSON Query Strategy tests passed!")

def test_all_query_strategies():
    """Test all query strategies."""
    print("🚀 Testing All Query Strategies...")
    
    # Structured Query Strategies
    test_sql_strategy()
    test_hiveql_strategy()
    test_pig_strategy()
    test_cql_strategy()
    test_n1ql_strategy()
    test_eql_strategy()
    test_kql_strategy()
    test_flux_strategy()
    test_datalog_strategy()
    
    # Graph Query Strategies
    test_graphql_strategy()
    test_sparql_strategy()
    test_gremlin_strategy()
    test_cypher_strategy()
    
    # Document Query Strategies
    test_linq_strategy()
    test_jsoniq_strategy()
    test_jmespath_strategy()
    test_xquery_strategy()
    test_xpath_strategy()
    
    # Generic Query Strategies
    test_xml_query_strategy()
    test_json_query_strategy()
    
    print("\n🎉 All Query Strategy Tests Passed!")
    print("✅ SQL, HiveQL, Pig, CQL, N1QL, EQL, KQL, Flux, Datalog")
    print("✅ GraphQL, SPARQL, Gremlin, Cypher")
    print("✅ LINQ, JSONiq, JMESPath, XQuery, XPath")
    print("✅ XML Query, JSON Query")


if __name__ == "__main__":
    test_all_query_strategies()
