#exonware\xsystem\serialization\graphdb.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: January 02, 2025

GraphDB serializer for Neo4j/Dgraph graph structure optimization.
"""

import json
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path

# Explicit imports - no try/except blocks per DEV_GUIDELINES.md
from neo4j import GraphDatabase
from pydgraph import DgraphClient

from .base import ASerialization
from .errors import SerializationError


class GraphDbError(SerializationError):
    """GraphDB specific serialization errors."""
    pass


class GraphDbSerializer(ASerialization):
    """
    GraphDB serializer for Neo4j/Dgraph graph structure optimization.
    
    Optimized for graph data with nodes, edges, and relationships.
    Supports both Neo4j and Dgraph backends with automatic detection.
    """
    
    def __init__(self, backend: str = "auto", uri: str = "bolt://localhost:7687"):
        """
        Initialize GraphDB serializer.
        
        Args:
            backend: "neo4j", "dgraph", or "auto" for automatic detection
            uri: Database URI (Neo4j: bolt://, Dgraph: localhost:9080)
        """
        super().__init__()
        self.backend = backend
        self.uri = uri
        self._driver = None
        self._db_type = None
        
    def _get_driver(self) -> Any:
        """Get database driver with automatic backend detection."""
        if self._driver is not None:
            return self._driver
            
        # Use Neo4j first
        if self.backend in ("auto", "neo4j"):
            self._driver = GraphDatabase.driver(self.uri)
            self._db_type = "neo4j"
            return self._driver
        
        # Use Dgraph
        if self.backend in ("auto", "dgraph"):
            self._driver = DgraphClient(self.uri)
            self._db_type = "dgraph"
            return self._driver
        
        raise GraphDbError("Invalid backend specified")
    
    def dumps(self, data: Any, **kwargs) -> bytes:
        """Serialize graph data to JSON format."""
        try:
            # Convert graph data to JSON-serializable format
            if isinstance(data, dict):
                graph_data = self._prepare_graph_data(data)
            elif isinstance(data, list):
                graph_data = {"nodes": data}
            else:
                graph_data = {"data": data}
            
            return json.dumps(graph_data).encode('utf-8')
        except Exception as e:
            raise GraphDbError(f"Graph serialization failed: {e}")
    
    def loads(self, data: bytes, **kwargs) -> Any:
        """Deserialize graph data from JSON format."""
        try:
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            raise GraphDbError(f"Graph deserialization failed: {e}")
    
    def _prepare_graph_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare graph data for serialization."""
        result = {"nodes": [], "edges": []}
        
        if "nodes" in data:
            result["nodes"] = data["nodes"]
        if "edges" in data:
            result["edges"] = data["edges"]
        if "relationships" in data:
            result["edges"] = data["relationships"]
        
        return result
    
    def create_node(self, labels: List[str], properties: Dict[str, Any]) -> str:
        """Create a node in the graph database."""
        try:
            driver = self._get_driver()
            
            if self._db_type == "neo4j":
                with driver.session() as session:
                    query = f"CREATE (n:{':'.join(labels)}) SET n += $props RETURN id(n) as node_id"
                    result = session.run(query, props=properties)
                    return str(result.single()["node_id"])
            elif self._db_type == "dgraph":
                # Dgraph uses mutations
                mutation = {
                    "set": [{
                        "uid": "_:new",
                        "dgraph.type": labels[0] if labels else "Node",
                        **properties
                    }]
                }
                response = driver.txn().mutate(mutation)
                return response.uids["new"]
                
        except Exception as e:
            raise GraphDbError(f"Node creation failed: {e}")
    
    def create_edge(self, from_node: str, to_node: str, 
                   relationship: str, properties: Optional[Dict[str, Any]] = None) -> str:
        """Create an edge/relationship in the graph database."""
        try:
            driver = self._get_driver()
            properties = properties or {}
            
            if self._db_type == "neo4j":
                with driver.session() as session:
                    query = """
                    MATCH (a), (b) 
                    WHERE id(a) = $from_id AND id(b) = $to_id
                    CREATE (a)-[r:{rel}]->(b)
                    SET r += $props
                    RETURN id(r) as edge_id
                    """.format(rel=relationship)
                    result = session.run(query, from_id=int(from_node), 
                                       to_id=int(to_node), props=properties)
                    return str(result.single()["edge_id"])
            elif self._db_type == "dgraph":
                mutation = {
                    "set": [{
                        "uid": from_node,
                        relationship: {"uid": to_node, **properties}
                    }]
                }
                response = driver.txn().mutate(mutation)
                return response.uids.get("new", "created")
                
        except Exception as e:
            raise GraphDbError(f"Edge creation failed: {e}")
    
    def query_nodes(self, labels: Optional[List[str]] = None, 
                   properties: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query nodes from the graph database."""
        try:
            driver = self._get_driver()
            
            if self._db_type == "neo4j":
                with driver.session() as session:
                    label_filter = f":{':'.join(labels)}" if labels else ""
                    prop_filter = " AND ".join([f"n.{k} = ${k}" for k in (properties or {})])
                    where_clause = f"WHERE {prop_filter}" if prop_filter else ""
                    
                    query = f"MATCH (n{label_filter}) {where_clause} RETURN n"
                    result = session.run(query, properties or {})
                    return [dict(record["n"]) for record in result]
            elif self._db_type == "dgraph":
                # Dgraph uses GraphQL+- queries
                type_filter = f"@filter(type({labels[0]}))" if labels else ""
                query = f"""
                {{
                    nodes(func: has(dgraph.type)) {type_filter} {{
                        uid
                        expand(_all_)
                    }}
                }}
                """
                response = driver.txn().query(query)
                return response.json["nodes"]
                
        except Exception as e:
            raise GraphDbError(f"Node query failed: {e}")
    
    def query_path(self, start_node: str, end_node: str, 
                  max_depth: int = 5) -> List[List[str]]:
        """Find paths between two nodes."""
        try:
            driver = self._get_driver()
            
            if self._db_type == "neo4j":
                with driver.session() as session:
                    query = """
                    MATCH path = (start)-[*1..{depth}]-(end)
                    WHERE id(start) = $start_id AND id(end) = $end_id
                    RETURN [node in nodes(path) | id(node)] as path_ids
                    """.format(depth=max_depth)
                    result = session.run(query, start_id=int(start_node), end_id=int(end_node))
                    return [record["path_ids"] for record in result]
            elif self._db_type == "dgraph":
                # Dgraph path queries are more complex
                query = f"""
                {{
                    path(func: uid({start_node})) @recurse(depth: {max_depth}) {{
                        uid
                        expand(_all_)
                    }}
                }}
                """
                response = driver.txn().query(query)
                return [response.json["path"]]
                
        except Exception as e:
            raise GraphDbError(f"Path query failed: {e}")
    
    def close(self) -> None:
        """Close database connection."""
        if self._driver is not None:
            try:
                if self._db_type == "neo4j":
                    self._driver.close()
                elif self._db_type == "dgraph":
                    self._driver.close()
                self._driver = None
                self._db_type = None
            except Exception as e:
                raise GraphDbError(f"Close operation failed: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
