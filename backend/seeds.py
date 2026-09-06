import asyncio
from .database import AsyncSessionLocal, engine, Base
from .models import Architecture, Gpu

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Архитектуры (пополнены профессиональными и прошлыми поколениями)
        ada = Architecture(family_name="GeForce / RTX Workstation", architecture="Ada Lovelace", generation_series="RTX 40 / Ada Generation")
        ampere = Architecture(family_name="GeForce / Quadro RTX", architecture="Ampere", generation_series="RTX 30 / Ampere Workstation")
        turing = Architecture(family_name="GeForce / Quadro RTX", architecture="Turing", generation_series="RTX 20 / Quadro RTX / GTX 16")
        pascal = Architecture(family_name="GeForce GTX / Quadro P-Series", architecture="Pascal", generation_series="GTX 10 / Quadro P")
        
        db.add_all([ada, ampere, turing, pascal])
        await db.commit()

        # 2. Расширенный список GPU (GeForce + Quadro / Workstation)
        gpus = [
            # === Ada Lovelace (RTX 40 & Professional Ada) ===
            Gpu(full_name="NVIDIA GeForce RTX 4090", vram_gb=24, memory_type="GDDR6X", bus_width_bits=384, arch_info=ada, for_games=True, for_3d=True, for_ml=True, for_office=False, budget_tier="flagship"),
            Gpu(full_name="NVIDIA RTX 6000 Ada Generation", vram_gb=48, memory_type="GDDR6", bus_width_bits=384, arch_info=ada, for_games=False, for_3d=True, for_ml=True, for_office=False, budget_tier="flagship"),
            Gpu(full_name="NVIDIA GeForce RTX 4070 Ti Super", vram_gb=16, memory_type="GDDR6X", bus_width_bits=256, arch_info=ada, for_games=True, for_3d=True, for_ml=True, for_office=False, budget_tier="mid"),
            Gpu(full_name="NVIDIA GeForce RTX 4060", vram_gb=8, memory_type="GDDR6", bus_width_bits=128, arch_info=ada, for_games=True, for_3d=False, for_ml=False, for_office=True, budget_tier="budget"),
            Gpu(full_name="NVIDIA RTX 4000 Ada Generation", vram_gb=20, memory_type="GDDR6", bus_width_bits=160, arch_info=ada, for_games=False, for_3d=True, for_ml=True, for_office=False, budget_tier="mid"),

            # === Ampere (RTX 30 & Ampere Workstation) ===
            Gpu(full_name="NVIDIA GeForce RTX 3090 Ti", vram_gb=24, memory_type="GDDR6X", bus_width_bits=384, arch_info=ampere, for_games=True, for_3d=True, for_ml=True, for_office=False, budget_tier="flagship"),
            Gpu(full_name="NVIDIA RTX A5000", vram_gb=24, memory_type="GDDR6", bus_width_bits=384, arch_info=ampere, for_games=False, for_3d=True, for_ml=True, for_office=False, budget_tier="flagship"),
            Gpu(full_name="NVIDIA GeForce RTX 3060", vram_gb=12, memory_type="GDDR6", bus_width_bits=192, arch_info=ampere, for_games=True, for_3d=True, for_ml=True, for_office=True, budget_tier="budget"),
            Gpu(full_name="NVIDIA RTX A2000", vram_gb=12, memory_type="GDDR6", bus_width_bits=192, arch_info=ampere, for_games=False, for_3d=True, for_ml=False, for_office=True, budget_tier="mid"),

            # === Turing (RTX 20, GTX 16 & Quadro RTX) ===
            Gpu(full_name="NVIDIA Quadro RTX 6000", vram_gb=24, memory_type="GDDR6", bus_width_bits=384, arch_info=turing, for_games=False, for_3d=True, for_ml=True, for_office=False, budget_tier="flagship"),
            Gpu(full_name="NVIDIA Quadro RTX 4000", vram_gb=8, memory_type="GDDR6", bus_width_bits=256, arch_info=turing, for_games=False, for_3d=True, for_ml=False, for_office=False, budget_tier="mid"),
            Gpu(full_name="NVIDIA GeForce RTX 2080 Ti", vram_gb=11, memory_type="GDDR6", bus_width_bits=352, arch_info=turing, for_games=True, for_3d=True, for_ml=False, for_office=False, budget_tier="mid"),
            Gpu(full_name="NVIDIA GeForce GTX 1660 Super", vram_gb=6, memory_type="GDDR6", bus_width_bits=192, arch_info=turing, for_games=True, for_3d=False, for_ml=False, for_office=True, budget_tier="budget"),

            # === Pascal (GTX 10 & Quadro P-Series) ===
            Gpu(full_name="NVIDIA Quadro P5000", vram_gb=16, memory_type="GDDR5X", bus_width_bits=256, arch_info=pascal, for_games=False, for_3d=True, for_ml=False, for_office=False, budget_tier="mid"),
            Gpu(full_name="NVIDIA Quadro P2200", vram_gb=5, memory_type="GDDR5x", bus_width_bits=160, arch_info=pascal, for_games=False, for_3d=True, for_ml=False, for_office=True, budget_tier="budget"),
            Gpu(full_name="NVIDIA GeForce GTX 1080 Ti", vram_gb=11, memory_type="GDDR5X", bus_width_bits=352, arch_info=pascal, for_games=True, for_3d=True, for_ml=False, for_office=False, budget_tier="mid"),
            Gpu(full_name="NVIDIA GeForce GTX 1060", vram_gb=6, memory_type="GDDR5", bus_width_bits=192, arch_info=pascal, for_games=True, for_3d=False, for_ml=False, for_office=True, budget_tier="budget")
        ]

        db.add_all(gpus)
        await db.commit()
        print("База успешно заполнена! Добавлены линейки Quadro, RTX Workstation и GTX Pascal.")

if __name__ == "__main__":
    asyncio.run(seed_data())