# python: 3.7.12
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import uvicorn
from PIL import Image
from io import BytesIO
import numpy as np

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

class FruitAnalysisResponse(BaseModel):
    fruit: Fruit
    similarity: float

def load_image_into_numpy_array(data):
    return np.array(Image.open(BytesIO(data)))

@app.post("/fruits", response_model=FruitAnalysisResponse)
async def analysis_fruit(
    fruit: Fruit = Form(...),
    fruit_part: FruitPart = Form(...),
    image: UploadFile = File(...)
):
    # 각 과일에 속한 부분이 아니면
    if fruit == Fruit.WATER_MELON and (fruit_part != FruitPart.WATER_MELON_CIRCULAR and fruit_part != FruitPart.WATER_MELON_STRIPES and fruit_part != FruitPart.WATER_MELON_NAVEL):
        raise HTTPException(status_code=400, detail="Invalid fruit parts")
    if fruit == Fruit.ORIENTAL_MELON and (fruit_part != FruitPart.ORIENTAL_MELON_INJURY and fruit_part != FruitPart.ORIENTAL_MELON_NAVEL and fruit_part != FruitPart.ORIENTAL_MELON_OVAL):
        raise HTTPException(status_code=400, detail="Invalid fruit parts")
    if fruit == Fruit.PEACH and (fruit_part != FruitPart.PEACH_LINE and fruit_part != FruitPart.PEACH_INJURY and fruit_part != FruitPart.PEACH_RED):
        raise HTTPException(status_code=400, detail="Invalid fruit parts")
    
    image = load_image_into_numpy_array(await image.read())
    similarity = compare_fruit(fruit=fruit.name, fruit_part=fruit_part.name, comparison_image=image)

    return FruitAnalysisResponse(similarity=similarity, fruit=fruit)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
