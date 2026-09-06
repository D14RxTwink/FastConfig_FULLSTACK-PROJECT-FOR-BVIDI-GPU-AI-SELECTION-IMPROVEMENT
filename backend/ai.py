async def get_gpu_analysis_from_ai(gpu_name: str, vram: int, bus: int, arch: str) -> dict:
    # Защита от пустых значений
    vram = int(vram) if vram is not None else 0
    bus = int(bus) if bus is not None else 0
    gpu_name = str(gpu_name) if gpu_name else "Видеокарта"
    arch = str(arch) if arch else "Н/Д"

    # 1. Офис / Мультимедиа (Любая современная дискретная видеокарта — 100%)
    office_score = 100

    # 2. Игры: зависит от объёма видеопамяти и шины
    if vram >= 24:
        games_score = 99
    elif vram >= 16:
        games_score = 95
    elif vram >= 12:
        games_score = 85
    elif vram >= 8:
        games_score = 70
    elif vram >= 6:
        games_score = 50
    else:
        games_score = 30

    # 3. 3D Рендеринг / Моделирование: важна видеопамять + ширина шины
    if vram >= 24 and bus >= 384:
        render_score = 98
    elif vram >= 16 and bus >= 256:
        render_score = 92
    elif vram >= 12:
        render_score = 80
    elif vram >= 8:
        render_score = 60
    else:
        render_score = 35

    # 4. Machine Learning (ML) / AI: критичен объём VRAM для весов моделей
    if vram >= 48:
        ml_score = 100
    elif vram >= 24:
        ml_score = 98
    elif vram >= 16:
        ml_score = 85
    elif vram >= 12:
        ml_score = 70
    elif vram >= 8:
        ml_score = 45
    else:
        ml_score = 15

    # Формируем автоматический вердикт
    if ml_score >= 85:
        verdict_text = f"{gpu_name} ({vram}GB VRAM, {bus}-bit): флагманское решение для тяжелого ML, AI-обучения и 3D-рендеринга."
    elif games_score >= 80:
        verdict_text = f"{gpu_name} ({vram}GB VRAM): отличный баланс для 1400p/4K гейминга, работы в Blender и тяжелых рабочих задач."
    elif games_score >= 60:
        verdict_text = f"{gpu_name} ({vram}GB VRAM): оптимальный вариант для Full HD гейминга, монтажа видео и базового 3D."
    else:
        verdict_text = f"{gpu_name} ({vram}GB VRAM): начальный уровень для офисной работы, мультимедиа и неприхотливых игр."

    return {
        "verdict": verdict_text,
        "games_score": games_score,
        "render_3d_score": render_score,
        "ml_score": ml_score,
        "office_score": office_score
    }