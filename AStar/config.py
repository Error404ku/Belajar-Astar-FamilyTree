import os
from neo4j import GraphDatabase

# Ganti dengan kredensial Neo4j Anda
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "kata_sandi_anda"  # Ganti dengan kata sandi Neo4j Anda

# Buat instance driver Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
