from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password123"
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()