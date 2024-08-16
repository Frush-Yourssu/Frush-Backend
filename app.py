# python: 3.7.12
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import uvicorn
from PIL import Image
import io
import numpy as np
import base64

from utils.fruit import compare_fruit
from enums.fruit import Fruit, FruitPart

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FruitAnalysisRequest(BaseModel):
    fruit: Fruit
    fruit_part: FruitPart
    image: str  # Base64 encoded image

class FruitAnalysisResponse(BaseModel):
    fruit: Fruit
    similarity: float

def load_image_into_numpy_array(data):
    return np.array(Image.open(BytesIO(data)))

@app.post("/fruits", response_model=FruitAnalysisResponse)
async def analysis_fruit(request: FruitAnalysisRequest):
    # 각 과일에 속한 부분이 아니면
    if request.fruit == Fruit.WATER_MELON and (request.fruit_part != FruitPart.WATER_MELON_CIRCULAR and request.fruit_part != FruitPart.WATER_MELON_STRIPES and request.fruit_part != FruitPart.WATER_MELON_NAVEL):
        raise HTTPException(status_code=400, detail="Invalid fruit parts")
    if request.fruit == Fruit.ORIENTAL_MELON and (request.fruit_part != FruitPart.ORIENTAL_MELON_INJURY and request.fruit_part != FruitPart.ORIENTAL_MELON_NAVEL and request.fruit_part != FruitPart.ORIENTAL_MELON_OVAL):
        raise HTTPException(status_code=400, detail="Invalid fruit parts")
    if request.fruit == Fruit.PEACH and (request.fruit_part != FruitPart.PEACH_LINE and request.fruit_part != FruitPart.PEACH_INJURY and request.fruit_part != FruitPart.PEACH_RED):
        raise HTTPException(status_code=400, detail="Invalid fruit parts")
    
    image_data = base64.b64decode(request.image)
    image = Image.open(io.BytesIO(image_data))
    image_np = np.array(image)

    similarity = compare_fruit(fruit=request.fruit.name, fruit_part=request.fruit_part.name, comparison_image=image_np)

    return FruitAnalysisResponse(similarity=similarity, fruit=request.fruit)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
