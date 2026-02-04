import uuid
from neo4j import GraphDatabase
from chromadb import HttpClient
from config import settings

class MondayVaultIngestor:
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        self.chroma_client = HttpClient(host=settings.chroma_host, port=settings.chroma_port)
        # Get or create our primary collection
        self.collection = self.chroma_client.get_or_create_collection(name="kernel_memories")

    def vault_data(self, content: str, category: str, tags: list[str]):
        """Ingests a single piece of data into both Graph and Vector stores."""
        node_id = str(uuid.uuid4())

        # 1. VECTOR INGESTION (Semantic Memory)
        self.collection.add(
            documents=[content],
            metadatas=[{"category": category, "tags": ",".join(tags)}],
            ids=[node_id]
        )

        # 2. GRAPH INGESTION (Relational Memory)
        with self.neo4j_driver.session() as session:
            session.execute_write(self._create_graph_nodes, node_id, content, category, tags)

        return node_id

    @staticmethod
    def _create_graph_nodes(tx, node_id, content, category, tags):
        # Create the main Note node
        query = """
        MERGE (n:Note {id: $id})
        SET n.content = $content, n.category = $category, n.timestamp = datetime()
        WITH n
        UNWIND $tags AS tagName
        MERGE (t:Tag {name: tagName})
        MERGE (n)-[:HAS_TAG]->(t)
        """
        tx.run(query, id=node_id, content=content, category=category, tags=tags)

    def recall(self, query: str, limit: int = 3):
        """
        Performs a hybrid search across Vector and Graph stores.
        """
        # 1. VECTOR SEARCH: Find semantically similar content
        vector_results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )

        # 2. GRAPH SEARCH: Find related entities via tags
        # We'll extract a "potential tag" from the query or just look for connections
        with self.neo4j_driver.session() as session:
            graph_results = session.execute_read(self._find_related_nodes, query)

        return {
            "semantic_matches": vector_results["documents"][0],
            "structural_matches": graph_results
        }

    @staticmethod
    def _find_related_nodes(tx, query):
        # A simple Cypher query to find notes connected to tags
        # that appear in the user's search query
        query_parts = query.lower().split()
        cypher = """
        MATCH (n:Note)-[:HAS_TAG]->(t:Tag)
        WHERE t.name IN $tags
        RETURN n.content AS content, t.name AS tag
        LIMIT 5
        """
        result = tx.run(cypher, tags=query_parts)
        return [{"content": record["content"], "tag": record["tag"]} for record in result]

# --- Initial Execution Test ---
if __name__ == "__main__":
    vault = MondayVaultIngestor()
    test_id = vault.vault_data(
        content="Monday Kernel is a polyglot Personal OS built with Python and Rust.",
        category="Project Info",
        tags=["python", "rust", "mentorship", "2026"]
    )
    print(f"🚀 Success! Data vaulted with ID: {test_id}")