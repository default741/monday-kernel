from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ingestor import MondayVaultIngestor

app = FastAPI(title="Monday Kernel: Vault Agent", version="2026.1.0")
vault = MondayVaultIngestor()

# Data Model for Ingestion
class IngestionRequest(BaseModel):
    content: str
    category: str = "General"
    tags: list[str] = []

@app.get("/")
async def root():
    return {"status": "online", "agent": "Vault", "system": "Monday Kernel"}

@app.post("/ingest")
async def ingest_to_vault(request: IngestionRequest):
    try:
        node_id = vault.vault_data(
            content=request.content,
            category=request.category,
            tags=request.tags
        )
        return {
            "status": "success",
            "node_id": node_id,
            "message": "Information secured in Monday Kernel Vault"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recall")
async def recall_from_vault(query: str):
    try:
        results = vault.recall(query)
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)