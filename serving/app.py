from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from src import config
from src.serve_utils import predict

app = FastAPI(title="Stockout Risk Service", version="1.0")


class PredictionRequest(BaseModel):
    Date: str = Field(..., description="ISO date of prediction")
    BranchID: int
    BranchName: str
    ItemCode: str
    ItemName: str
    CurrentQuantity: float
    ReservedQuantity: float = 0
    SafetyStockLevel: float
    QuantitySold: float = 0


@app.post("/predict")
def predict_endpoint(request: PredictionRequest):
    payload = request.dict()
    result = predict(payload)
    if "error" in result and result.get("fallback"):
        # still return 200 but with fallback info
        return {"prediction": result, "note": "Fallback used"}
    return {"prediction": result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
