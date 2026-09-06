from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .database import engine, Base, get_db
from . import models, schemas
from .ai import get_gpu_analysis_from_ai

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="FastConfig API", lifespan=lifespan)

@app.get("/")
async def read_index():
    return FileResponse("verstka/index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/gpus", response_model=List[schemas.GpuSchema])
async def get_all_gpus(db: AsyncSession = Depends(get_db)):
    query = select(models.Gpu).options(selectinload(models.Gpu.arch_info))
    result = await db.execute(query)
    gpus = result.scalars().all()
    return gpus

@app.get("/gpus/{gpu_id}/analyze")
async def analyze_gpu(gpu_id: int, db: AsyncSession = Depends(get_db)):
    query = select(models.Gpu).options(selectinload(models.Gpu.arch_info)).where(models.Gpu.id == gpu_id)
    result = await db.execute(query)
    gpu = result.scalar_one_or_none()

    if not gpu:
        raise HTTPException(status_code=404, detail="Видеокарта не найдена")

    arch_name = gpu.arch_info.architecture if gpu.arch_info else "Н/Д"

    ai_data = await get_gpu_analysis_from_ai(
        gpu_name=gpu.full_name,
        vram=gpu.vram_gb,
        bus=gpu.bus_width_bits,
        arch=arch_name
    )

    return ai_data