from neo4j import GraphDatabase
from chromadb import HttpClient
from config import settings

def test_vault():
    try:
        # Test Neo4j
        driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
        driver.verify_connectivity()
        print("✅ Neo4j: Connected!")

        # Test Chroma
        client = HttpClient(host=settings.chroma_host, port=settings.chroma_port)
        print(f"✅ Chroma: Connected! (Version: {client.get_version()})")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_vault()