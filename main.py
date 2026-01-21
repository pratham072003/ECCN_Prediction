from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from core.classifier import classify_product
import uvicorn
import os

app = FastAPI(
    title="ECCN Classification API",
    description="API to classify products into Export Control Classification Numbers (ECCN) using RAG + LLM.",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ClassificationRequest(BaseModel):
    product_text: str

class ClassificationResponse(BaseModel):
    ecn_number: str
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.post("/classify", response_model=ClassificationResponse)
async def classify_product_endpoint(request: ClassificationRequest):
    """
    Classify a product description into an ECCN code.
    """
    if not request.product_text or len(request.product_text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Product text cannot be empty.")
    
    try:
        # Call the classifier logic
        result = classify_product(request.product_text)
        return ClassificationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    # Check if vector DB exists
    db_path = "lancedb_data"
    if not os.path.exists(db_path) or not os.listdir(db_path):
        print(f"Vector database not found at {db_path}. Starting ingestion...")
        try:
            from core.data_loader import load_data_and_index
            load_data_and_index()
            print("Ingestion complete.")
        except Exception as e:
            print(f"Failed to run ingestion: {e}")
            # we don't raise error here to let app start, but it won't work well
    else:
        print(f"Vector database found at {db_path}. Skipping ingestion.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
