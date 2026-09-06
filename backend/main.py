import os
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .database import engine, Base, get_db, AsyncSessionLocal
from . import models, schemas
from .ai import get_gpu_analysis_from_ai


async def auto_seed_db():
    try:
        async with AsyncSessionLocal() as session:
            # Проверяем наличие видеокарт
            result = await session.execute(select(models.Gpu))
            existing_gpus = result.scalars().all()
            
            if not existing_gpus:
                # 1. Создаем архитектуры с обязательным family_name
                ada = models.Architecture(
                    family_name="NVIDIA", 
                    architecture="Ada Lovelace", 
                    generation_series="RTX 4000"
                )
                ampere = models.Architecture(
                    family_name="NVIDIA", 
                    architecture="Ampere", 
                    generation_series="RTX 3000"
                )
                session.add_all([ada, ampere])
                await session.flush()  # Получаем автосгенерированные ID

                # 2. Добавляем видеокарты со ссылкой на architecture_id
                gpus = [
                    models.Gpu(
                        full_name="NVIDIA GeForce RTX 4060",
                        vram_gb=8,
                        memory_type="GDDR6",
                        bus_width_bits=128,
                        budget_tier="mid",
                        for_games=True,
                        for_3d=True,
                        for_ml=False,
                        for_office=False,
                        architecture_id=ada.id
                    ),
                    models.Gpu(
                        full_name="NVIDIA GeForce RTX 3060",
                        vram_gb=12,
                        memory_type="GDDR6",
                        bus_width_bits=192,
                        budget_tier="budget",
                        for_games=True,
                        for_3d=True,
                        for_ml=True,
                        for_office=False,
                        architecture_id=ampere.id
                    ),
                    models.Gpu(
                        full_name="NVIDIA GeForce RTX 4090",
                        vram_gb=24,
                        memory_type="GDDR6X",
                        bus_width_bits=384,
                        budget_tier="flagship",
                        for_games=True,
                        for_3d=True,
                        for_ml=True,
                        for_office=False,
                        architecture_id=ada.id
                    )
                ]
                session.add_all(gpus)
                await session.commit()
                print("База данных успешно заполнена видеокартами!")
    except Exception as e:
        print(f"Ошибка при заполнении базы: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Наполняем базу при старте
    await auto_seed_db()
    yield

app = FastAPI(title="FastConfig API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "..", "verstka", "index.html")
    if not os.path.exists(html_path):
        html_path = os.path.join(base_dir, "verstka", "index.html")
        
    if os.path.exists(html_path):
        return FileResponse(html_path)
    
    raise HTTPException(status_code=404, detail="Файл index.html не найден")

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